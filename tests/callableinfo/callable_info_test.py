from funpaybotengine.dispatching.bases import CallableInfo
from collections.abc import Callable
import pytest
from typing import Any



@pytest.fixture
def workflow_data() -> dict[str, Any]:
    return {
        'arg1': 'arg1',
        'arg2': 2,
        'arg3': True,
        'arg4': False
    }


@pytest.fixture
def function_without_params() -> Callable[[], bool]:
    def inner() -> bool:
        return True

    return inner


@pytest.fixture
def function_with_params() -> Callable[..., Any]:
    def inner(arg1: Any, arg2: Any, arg3: Any, arg4: Any) -> Any:
        return arg1, arg2, arg3, arg4

    return inner


@pytest.fixture
def function_with_kwonly_params() -> Callable[..., Any]:
    def inner(arg1: str = 'not_arg_1', arg5: int = 1) -> Any:
        return arg1, arg5

    return inner


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'function,expected', [
        ('function_without_params', True),
        ('function_with_params', ('arg1', 2, True, False)),
        ('function_with_kwonly_params', ('arg1', 1)),
    ]
)
async def test_callable_info(workflow_data, function, expected, request):
    real_function = request.getfixturevalue(function)
    callable_info_obj = CallableInfo(real_function)
    assert (await callable_info_obj(**workflow_data)) == expected
