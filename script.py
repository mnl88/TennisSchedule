import asyncio
from draw_the_schedule import main as draw_the_schedule


async def async_main():
    while True:
        draw_the_schedule()
        await asyncio.sleep(3*60)


if __name__ == '__main__':
    asyncio.run(async_main())
