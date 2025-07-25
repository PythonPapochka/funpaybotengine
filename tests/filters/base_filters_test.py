from __future__ import annotations

import pytest
from pytest import FixtureRequest

from funpaybotengine.dispatching.events import RunnerEvent
from funpaybotengine.dispatching.filters import (
    Filter,
    CallableFilter,
    AwaitableFilter,
    all_of,
    any_of,
)
from funpaybotengine.dispatching.filters.base import _convert_filters


class TrueFilter(Filter):
    async def __call__(self) -> bool:
        return True


class FalseFilter(Filter):
    async def __call__(self) -> bool:
        return False


@pytest.fixture
def true_filter() -> TrueFilter:
    return TrueFilter()


@pytest.fixture
def false_filter() -> FalseFilter:
    return FalseFilter()


@pytest.fixture
def true_filter_function() -> CallableFilter:
    def true_filter_function() -> bool:
        return True

    return true_filter_function


@pytest.fixture
def false_filter_function() -> CallableFilter:
    def false_filter_function() -> bool:
        return False

    return false_filter_function


@pytest.fixture
def true_filter_async_function() -> AwaitableFilter:
    async def true_filter_async_function() -> bool:
        return True

    return true_filter_async_function


@pytest.fixture
def false_filter_async_function() -> AwaitableFilter:
    async def false_filter_async_function() -> bool:
        return False

    return false_filter_async_function


@pytest.fixture
def event() -> RunnerEvent[object]:
    return RunnerEvent(object, 'tag')


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'f1,f2,expected',
    [
        ('true_filter', 'true_filter', True),
        ('true_filter', 'false_filter', False),
        ('false_filter', 'true_filter', False),
        ('false_filter', 'false_filter', False),
    ],
)
async def test_and_operator(
    f1: str,
    f2: str,
    expected: bool,
    request: FixtureRequest,
    event: RunnerEvent[object],
) -> None:
    new_filter = request.getfixturevalue(f1) & request.getfixturevalue(f2)
    result = await new_filter()
    assert result is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'f1,f2,expected',
    [
        ('true_filter', 'true_filter', True),
        ('true_filter', 'false_filter', True),
        ('false_filter', 'true_filter', True),
        ('false_filter', 'false_filter', False),
    ],
)
async def test_or_operator(
    f1: str,
    f2: str,
    expected: bool,
    request: FixtureRequest,
    event: RunnerEvent[object],
) -> None:
    new_filter = request.getfixturevalue(f1) | request.getfixturevalue(f2)
    result = await new_filter()
    assert result is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'f,expected',
    [
        ('true_filter', False),
        ('false_filter', True),
    ],
)
async def test_not_operator(
    f: str,
    expected: bool,
    request: FixtureRequest,
    event: RunnerEvent[object],
) -> None:
    new_filter = ~request.getfixturevalue(f)
    result = await new_filter()
    assert result is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'f_list,expected',
    [
        (['true_filter', 'true_filter'], True),
        (['true_filter', 'false_filter'], False),
        (['false_filter', 'false_filter'], False),
        ([], True),
    ],
)
async def test_all_of_filter(
    f_list: list[str],
    expected: bool,
    request: FixtureRequest,
    event: RunnerEvent[object],
) -> None:
    filters = [request.getfixturevalue(i) for i in f_list]
    new_filter = all_of(*filters)
    result = await new_filter()
    assert result is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'f_list,expected',
    [
        (['true_filter', 'true_filter'], True),
        (['true_filter', 'false_filter'], True),
        (['false_filter', 'false_filter'], False),
        ([], False),
    ],
)
async def test_any_of_filter(
    f_list: list[str],
    expected: bool,
    request: FixtureRequest,
    event: RunnerEvent[object],
) -> None:
    filters = [request.getfixturevalue(i) for i in f_list]
    new_filter = any_of(*filters)
    result = await new_filter()
    assert result is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'f_func,expected',
    [
        ('true_filter_function', True),
        ('true_filter_async_function', True),
        ('false_filter_function', False),
        ('false_filter_async_function', False),
    ],
)
async def test_function_filters_conversion(
    f_func: str,
    expected: bool,
    request: FixtureRequest,
    event: RunnerEvent[object],
) -> None:
    filter_func = request.getfixturevalue(f_func)
    filter_obj = _convert_filters([filter_func])[0]
    result = await filter_obj()
    assert result is expected
