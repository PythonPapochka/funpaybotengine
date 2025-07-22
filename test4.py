from funpaybotengine.dispatching.routers import Router
from funpaybotengine.dispatching.events import NewMessageEvent, NewSaleEvent


router = Router(id='some_router')

@router.on_new_message_event(id='some_handler')
async def some_handler(event: NewMessageEvent, some_args: bool) -> None:
    ...
