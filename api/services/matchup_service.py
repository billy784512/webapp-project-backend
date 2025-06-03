import os
import uuid
import random
import asyncio
import base64
import io
from pathlib import Path
from collections import defaultdict
from typing import Tuple, Dict, Optional, List

from PIL import Image
import numpy as np
from skimage.metrics import structural_similarity as ssim

from models.room_info import RoomInfo
from utils.config import config

class MatchupService:
    _instance: Optional["MatchupService"] = None

    def __init__(self):
        if MatchupService._instance is not None:
            raise Exception("Use MatchupService.get_instance().")
        MatchupService._instance = self

        self.anonymous_queue: List[Tuple[asyncio.Future, str]] = []
        self.anonymous_lock = asyncio.Lock()

        self.passkey_queues: Dict[str, List[Tuple[asyncio.Future, str]]] = {}
        self.passkey_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

        # key: room_id, val: user_id_list
        self.room_info_map: Dict[str, RoomInfo] = {}

        self._matching_task = asyncio.create_task(self._match_anonymous_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_passkey_queues_loop())

    @classmethod
    def get_instance(cls) -> "MatchupService":
        if cls._instance is None:
            cls._instance = MatchupService()
        return cls._instance
    
    # ========== PUBLIC API ==========

    async def anonymous_match(self, user_id: str) -> str:
        future = asyncio.get_event_loop().create_future()
        async with self.anonymous_lock:
            self.anonymous_queue.append((future, user_id))

        try:
            return await asyncio.wait_for(future, timeout=10.0)
        except asyncio.TimeoutError:
            await self.cancel_match(user_id)
            raise TimeoutError("Match Timeout")
        except asyncio.CancelledError:
            return {"status": "failed", "message": "Match cancelled"}

    async def passkey_match(self, user_id: str, passkey: str) -> str:
        future = asyncio.get_event_loop().create_future()
        async with self.passkey_locks[passkey]:
            queue = self.passkey_queues.setdefault(passkey, [])
            queue.append((future, user_id))

        if len(queue) >= 2:
            await self._match_passkey_queue(passkey)

        try:
            return await asyncio.wait_for(future, timeout=10.0)
        except asyncio.TimeoutError:
            await self.cancel_match(user_id)
            raise TimeoutError(f"Match timeout for passkey '{passkey}'")
        except asyncio.CancelledError:
                return {"status": "failed", "message": "Match cancelled"}

    async def cancel_match(self, user_id: str):
        async with self.anonymous_lock:
            new_queue = []
            for f, u in self.anonymous_queue:
                if u == user_id:
                    f.cancel()
                else:
                    new_queue.append((f, u))
            self.anonymous_queue = new_queue

        for passkey, lock in self.passkey_locks.items():
            async with lock:
                if passkey not in self.passkey_queues:
                    continue
                self.passkey_queues[passkey] = [(f, u) for (f, u) in self.passkey_queues[passkey] if u != user_id]

    def get_userid_by_roomid(self, room_id: str) -> List[str]:
        try:
            return self.room_info_map[room_id].user_ids
        except Exception as e:
            raise e
    
    def get_image_path_by_roomid(self, room_id: str) -> str:
        try:
            return self.room_info_map[room_id].image
        except Exception as e:
            raise e
        
    def get_color_list_by_roomid(self, room_id: str) -> List[str]:
        try:
            return self.room_info_map[room_id].color_list
        except Exception as e:
            raise e
    
    def calculate_result(self, room_id: str, base64_str: str) -> float:
        try:
            if base64_str.startswith("data:image"):
                base64_str = base64_str.split(",")[1]

            image_data = base64.b64decode(base64_str)

            user_image_pil = (
                Image.open(io.BytesIO(image_data)).convert("RGB").resize((64, 64))
            )

            image_path = self.get_image_path_by_roomid(room_id)
            if not image_path or not os.path.exists(image_path):
                print(
                    f"Error: Target image path not found or invalid for room_id {room_id}. Path: {image_path}"
                )
                return 0.0

            with open(image_path, "rb") as img_file:
                origin_image_data = img_file.read()

            origin_image_pil = (
                Image.open(io.BytesIO(origin_image_data))
                .convert("RGB")
                .resize((64, 64))
            )

            np_user_img = np.array(user_image_pil, dtype=np.float32) / 255.0
            np_origin_img = np.array(origin_image_pil, dtype=np.float32) / 255.0

            ssim_score, diff_img = ssim(
                np_user_img,
                np_origin_img,
                channel_axis=-1,
                full=True,
                data_range=1.0,
                win_size=7,
            )

            scaled_score = (ssim_score + 1) * 50

            final_score = round(max(0, min(100, scaled_score)), 2)

            return final_score
        except Exception as e:
            print(f"Unexpected error in calculate_result (room {room_id}): {str(e)}")
            return 0.0

    # ========== BACKGROUND TASKS ==========

    async def _match_anonymous_loop(self):
        while True:
            async with self.anonymous_lock:
                if len(self.anonymous_queue) >= 2:
                    (fut1, user1) = self.anonymous_queue.pop(0)
                    (fut2, user2) = self.anonymous_queue.pop(0)
                    room_id = self.prepare_room_info(user1, user2)

                    fut1.set_result({"status": "matched", "room_id": room_id, "players": [user1, user2]})
                    fut2.set_result({"status": "matched", "room_id": room_id, "players": [user1, user2]})
                else:
                    await asyncio.sleep(0.1)

    async def _match_passkey_queue(self, passkey: str):
        async with self.passkey_locks[passkey]:
            queue = self.passkey_queues.get(passkey)
            if queue is None or len(queue) < 2:
                return

            fut1, user1 = queue.pop(0)
            fut2, user2 = queue.pop(0)
            room_id = self.prepare_room_info(user1, user2)

            fut1.set_result({"status": "matched", "room_id": room_id, "players": [user1, user2], "passkey": passkey})
            fut2.set_result({"status": "matched", "room_id": room_id, "players": [user1, user2], "passkey": passkey})

    async def _cleanup_passkey_queues_loop(self):
        while True:
            await asyncio.sleep(60)
            keys_to_delete = []
            for key, queue in self.passkey_queues.items():
                async with self.passkey_locks[key]:
                    if not queue:
                        keys_to_delete.append(key)
            for key in keys_to_delete:
                async with self.passkey_locks[key]:
                    if key in self.passkey_queues and not self.passkey_queues[key]:
                        del self.passkey_queues[key]
                        del self.passkey_locks[key]
                        print(f"[Cleanup] Removed empty passkey queue: {key}")

    # ========== UTILITIES ==========
    
    def prepare_room_info(self, user_id1, user_id2) -> str:
        room_id = str(uuid.uuid4())
        room_info = RoomInfo()
        room_info.user_ids.append(user_id1)
        room_info.user_ids.append(user_id2)

        folder_path = Path(config.DIR.IMAGE).resolve()
        files = [f for f in os.listdir(folder_path)]

        room_info.color_list = [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(3)]
        room_info.image = os.path.join(folder_path, random.choice(files))

        self.room_info_map[room_id] = room_info
        print(f"########ROOM_INFO########")
        print(f"room_id: {room_id},\nusers: {self.room_info_map[room_id].user_ids},\nimage: {self.room_info_map[room_id].image},\ncolors: {self.room_info_map[room_id].color_list}")
        print(f"#########################")

        return room_id