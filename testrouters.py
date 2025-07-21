from funpaybotengine.dispatching.routers.base import Router


Router1 = Router('router1')
Router1_1 = Router('router1_1')
Router1_2 = Router('router1_2')
Router1_3 = Router('router1_3')
Router1_3_1 = Router('router1_3_1')
Router1_3_2 = Router('router1_3_2')
Router1_3_3 = Router('router1_3_3')
Router1_4 = Router('router1_4')


Router1_3.connect_routers(Router1_3_1, Router1_3_2, Router1_3_3)
Router1.connect_routers(Router1_2, Router1_3, Router1_4)


for i in Router1_3_3.chain_to_root_router:
    print(i.id)

print('*' * 50)


for i in Router1.chain_to_last_router:
    print(i.id)


@Router1_3_3.on_new_message_event()
async def something():
    ...

@Router1_4.on_new_sale_event()
async def something():
    ...


print(Router1.get_handler_by_id('2'))