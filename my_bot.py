from __future__ import annotations

import asyncio

from funpaybotengine.types.messages import Message
from funpaybotengine.dispatching.events import NewMessageEvent
from funpaybotengine.dispatching.routers import Router, Dispatcher


# --- loggers ---
"""
dictConfig(
    config={
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'formatter': 'brief',
                'level': logging.INFO,
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
            },
        },
        'formatters': {
            'brief': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
        },
        'loggers': {
            'funpaybotengine.session_logger': {
                'level': logging.DEBUG,
                'handlers': ['console'],
            },
            'funpaybotengine.router_logger': {
                'level': logging.DEBUG,
                'handlers': ['console'],
            },
        },
    },
)
"""
# --- Event preparation ---
message = Message(
    raw_source='',
    id=1,
    is_heading=False,
    sender_id=12345,
    sender_username='qvvonk',
    badge=None,
    send_date_text='12.12.2005',
    text='Я лунтик',
    image_url=None,
    chat_id=2,
    chat_name='flood',
)

e = NewMessageEvent(
    obj=message,
    tag='abcdefgh',
)


# Program
dp = Dispatcher()
router = Router(
    'some_router',
)

router2 = Router(
    'some_router',
)

dp.connect_router(router)
dp.connect_router(router2)


# Start
async def main() -> None:
    await dp.propagate_event(e)


if __name__ == '__main__':
    asyncio.run(main())
