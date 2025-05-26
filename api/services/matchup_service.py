import asyncio
import uuid
from typing import Tuple

class MatchupService:
    def __init__(self):
        self.queue: asyncio.Queue[Tuple[asyncio.Future, str]] = asyncio.Queue()

    async def join_queue(self, user_id: str) -> str:
        future = asyncio.get_event_loop().create_future()
        await self.queue.put((future, user_id))

        if self.queue.qsize() >= 2:
            (fut1, user1) = await self.queue.get()
            (fut2, user2) = await self.queue.get()
            room_id = str(uuid.uuid4())
            fut1.set_result(room_id)
            fut2.set_result(room_id)

        return await future
