import httpx
import asyncio

BASE_URL = "http://localhost:8080/match"
SETUP_BASE_URL = "http://localhost:8080/game"
PASSKEY = "room999"

async def post_passkey(user_id: str, timeout=35.0):
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            match_resp = await client.post(f"{BASE_URL}/passkey", json={"user_id": user_id, "user_name": user_id, "passkey": PASSKEY})
            match_data = match_resp.json()

            if match_data.get("status") == "matched":
                room_id = match_data["room_id"]

                users_resp = await client.get(f"{SETUP_BASE_URL}/users", params={"room_id": room_id})
                game_resp = await client.get(f"{SETUP_BASE_URL}/game", params={"room_id": room_id})

                return user_id, {
                    "match": match_data,
                    "users": users_resp.json(),
                    "game": game_resp.json()
                }
            else:
                return user_id, {"match": match_data}

        except httpx.ReadTimeout:
            return user_id, "Timeout"
async def cancel_match(user_id: str):
    async with httpx.AsyncClient() as client:
        await client.post(f"{BASE_URL}/cancel", json={"user_id": user_id, "user_name": user_id})
        
async def case1():
    print("== Case 1: 正常 2 人 passkey match ==")
    r1, r2 = await asyncio.gather(
        post_passkey("p1"),
        post_passkey("p2")
    )
    print(r1, r2)


async def case2():
    print("== Case 2: 1 人 join 後 timeout ==")
    r = await post_passkey("p3")
    print(r)


async def case3():
    print("== Case 3: 三人加入，前兩人 match，後一人 timeout ==")
    tasks = [post_passkey("p4"), post_passkey("p5"), post_passkey("p6")]
    results = await asyncio.gather(*tasks)
    print(results)


async def case4():
    print("== Case 4: 四人加入，兩兩成功配對 ==")
    tasks = [post_passkey("p7"), post_passkey("p8"), post_passkey("p9"), post_passkey("p10")]
    results = await asyncio.gather(*tasks)
    print(results)


async def case5():
    print("== Case 5: 一人加入後取消，另一人加入後 timeout ==")
    task1 = asyncio.create_task(post_passkey("p11"))
    await asyncio.sleep(10)
    await cancel_match("p11")
    print("p11 cancelled")

    await asyncio.sleep(1)
    r2 = await post_passkey("p12")
    print(r2)


async def case6():
    print("== Case 6: 一人加入後取消，然後兩人加入並成功配對 ==")
    task1 = asyncio.create_task(post_passkey("p13"))
    await asyncio.sleep(10)
    await cancel_match("p13")
    print("p13 cancelled")

    task2 = asyncio.create_task(post_passkey("p14"))
    await asyncio.sleep(3)
    task3 = asyncio.create_task(post_passkey("p15"))

    results = await asyncio.gather(task2, task3)
    print(results)


async def main():
    await case1()
    await asyncio.sleep(1)
    await case2()
    await asyncio.sleep(1)
    await case3()
    await asyncio.sleep(1)
    await case4()
    await asyncio.sleep(1)
    await case5()
    await asyncio.sleep(1)
    await case6()

if __name__ == "__main__":
    asyncio.run(main())
