from funpaybotengine import Bot, Dispatcher
import logging
import sys
from logging.config import dictConfig


dictConfig(
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'formatter': 'brief',
                'level': logging.DEBUG,
                'class': 'logging.StreamHandler',
                'stream': sys.stdout
            }
        },
        'formatters': {
            'brief': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'loggers': {
            'funpaybotengine.session': {
                'level': logging.DEBUG,
                'handlers': ['console'],
            },
            'funpaybotengine.runner': {
                'level': logging.DEBUG,
                'handlers': ['console'],
            }
        }
    }
)


bot = Bot('b82sweupq2jxozpcvdmfv4v1x84udj4c', proxy='socks5://user148429:dgej93@45.39.104.142:19392')
dp = Dispatcher()


async def main():
    await bot.listen_events(dp)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())