from __future__ import annotations


__all__ = ('session_logger', 'router_logger', 'dispatcher_logger')


from logging import getLogger


session_logger = getLogger('funpaybotengine.session_logger')
router_logger = getLogger('funpaybotengine.router_logger')
dispatcher_logger = getLogger('funpaybotengine.dispatcher_logger')
