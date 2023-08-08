import asyncio
import random


async def do_math():
    await asyncio.sleep(random.random() * 10)
    return random.randint(1, 10)


async def test_tg():
    tg = asyncio.TaskGroup()
    for _ in range(10):
        tg.create_task(do_math())

    results = await tg
    print(results)


if __name__ == "__main__":
    asyncio.run(test_tg())
