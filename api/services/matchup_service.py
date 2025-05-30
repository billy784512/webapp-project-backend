import asyncio
import uuid
from typing import Tuple, Dict, Optional, List

from utils.match_room_cache import get_or_create_room_data
# get_or_create_room_data(room_id: str, loader_fn: Callable[[], dict]) -> dict

class MatchupService:
    def __init__(self):
        self.queue: asyncio.Queue[Tuple[asyncio.Future, str]] = asyncio.Queue()
        self.user_room_map: Dict[str, str] = {} # 記錄每個使用者對應的room_id，用來查詢是否已配對、取得房間資料

    async def join_queue(self, user_id: str) -> str:
        future = asyncio.get_event_loop().create_future()
        await self.queue.put((future, user_id))

        if self.queue.qsize() >= 2:
            (fut1, user1) = await self.queue.get()
            (fut2, user2) = await self.queue.get()
            room_id = str(uuid.uuid4())
            self.user_room_map[user1] = room_id # 為他們產生一個唯一room_id
            self.user_room_map[user2] = room_id
            fut1.set_result(room_id)
            fut2.set_result(room_id)

        try:
            return await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError:  # 如果這個使用者在 30 秒內沒有成功配對，就拋出TimeoutError
            raise TimeoutError("配對逾時")

    def get_room_id(self, user_id: str) -> Optional[str]: # 傳回該使用者的房號（如未配對會是 None）
        return self.user_room_map.get(user_id)

    def is_user_matched(self, user_id: str) -> bool: # 查詢某個 user 是否已成功配對
        return user_id in self.user_room_map

    # 取得該 user 的題目圖片 (image bytes)
    def get_game_image_for_user(self, user_id: str) -> Optional[bytes]:
        room_id = self.get_room_id(user_id)
        if not room_id: # 根據 user_id 取得房號，若尚未配對成功則回傳 None
            return None

        def loader(): # 若是第一次這個房號被查詢，則讀取圖片並生成顏色表
            try:
                with open("assets/default.jpg", "rb") as f: # 假設圖片放在 assets/default.jpg
                    return {
                        "image": f.read(), # 圖片bytes
                        "colors": ["#FF0000", "#00FF00", "#0000FF"]
                    }
            except FileNotFoundError:
                return {"image": None, "colors": []}

        data = get_or_create_room_data(room_id, loader) # 透過 room_id 拿到這一場對戰共用的題目資料
        return data.get("image")  # 回傳圖片給controller

    # Spec 2：取得該 user 的題目顏色列表
    def get_color_list_for_user(self, user_id: str) -> Optional[List[str]]:
        room_id = self.get_room_id(user_id)
        if not room_id:
            return None

        def loader():
            try:
                with open("assets/default.jpg", "rb") as f:
                    return {
                        "image": f.read(),
                        "colors": ["#FF0000", "#00FF00", "#0000FF"]
                    }
            except FileNotFoundError:
                return {"image": None, "colors": []}

        data = get_or_create_room_data(room_id, loader)
        return data.get("colors")



