import logging
import asyncio
from draw_the_schedule import main as draw_the_schedule

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


async def async_main():
    while True:
        try:
            draw_the_schedule()
            await asyncio.sleep(3 * 60)
        except Exception as err:
            logger.error(err)
            await asyncio.sleep(10 * 60)
            await async_main()

if __name__ == '__main__':
    asyncio.run(async_main())
