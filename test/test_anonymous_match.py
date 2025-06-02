import httpx
import asyncio

BASE_URL = "http://localhost:8080/match"
SETUP_BASE_URL = "http://localhost:8080/setup"

async def post_anonymous(user_id: str, timeout=35.0):
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            match_resp = await client.post(
                f"{BASE_URL}/anonymous",
                json={"user_id": user_id, "user_name": user_id}
            )
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


async def test_case_1():
    print("== Case 1: 正常 2 人 match ==")
    r1, r2 = await asyncio.gather(
        post_anonymous("u1"),
        post_anonymous("u2")
    )
    print(r1, r2)


async def test_case_2():
    print("== Case 2: 1 人等到 timeout ==")
    result = await post_anonymous("u3")
    print(result)


async def test_case_3():
    print("== Case 3: A 等待後取消，B 加入但等 timeout ==")
    task_a = asyncio.create_task(post_anonymous("u4"))
    await asyncio.sleep(5)  # 等待 A 等一段時間
    await cancel_match("u4")
    print("u4 cancelled")

    await asyncio.sleep(1)
    result = await post_anonymous("u5")
    print(result)


async def test_case_4():
    print("== Case 4: A 等待後取消，B 加入，C 加入成功配對 ==")
    task_a = asyncio.create_task(post_anonymous("u6"))
    await asyncio.sleep(3)
    await cancel_match("u6")
    print("u6 cancelled")

    task_b = asyncio.create_task(post_anonymous("u7"))
    await asyncio.sleep(5)
    task_c = asyncio.create_task(post_anonymous("u8"))

    results = await asyncio.gather(task_b, task_c)
    print(results)


async def test_case_5():
    print("== Case 5: 3 人加入，2 match, 1 timeout ==")
    tasks = [
        asyncio.create_task(post_anonymous("u9")),
        asyncio.create_task(post_anonymous("u10")),
        asyncio.create_task(post_anonymous("u11")),
    ]
    results = await asyncio.gather(*tasks)
    print(results)


async def test_case_6():
    print("== Case 6: 4 人加入，兩兩配對 ==")
    tasks = [
        asyncio.create_task(post_anonymous("u12")),
        asyncio.create_task(post_anonymous("u13")),
        asyncio.create_task(post_anonymous("u14")),
        asyncio.create_task(post_anonymous("u15")),
    ]
    results = await asyncio.gather(*tasks)
    print(results)


async def main():
    await test_case_1()
    await asyncio.sleep(3)
    await test_case_2()
    await asyncio.sleep(3)
    await test_case_3()
    await asyncio.sleep(3)
    await test_case_4()
    await asyncio.sleep(3)
    await test_case_5()
    await asyncio.sleep(3)
    await test_case_6()

if __name__ == "__main__":
    asyncio.run(main())
