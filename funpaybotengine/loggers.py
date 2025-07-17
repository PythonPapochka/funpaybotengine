__all__ = ('session_logger', 'router_logger')


from logging import getLogger


session_logger = getLogger('funpaybotengine.session_logger')
router_logger = getLogger('funpaybotengine.router_logger')
