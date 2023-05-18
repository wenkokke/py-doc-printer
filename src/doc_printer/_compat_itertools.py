import sys
from itertools import chain as chain
from itertools import groupby as groupby
from itertools import repeat as repeat
from typing import List

from more_itertools import intersperse as intersperse

################################################################################
# Export List
################################################################################

__all__: List[str] = [
    "accumulate",
    "chain",
    "groupby",
    "intersperse",
    "repeat",
]

################################################################################
# Python 3.7: itertools.accumulate
################################################################################

if sys.version_info >= (3, 8):
    from itertools import accumulate as accumulate

elif sys.version_info < (3, 8) and sys.version_info >= (3, 7):
    import operator
    from itertools import accumulate as _accumulate
    from typing import Any, Callable, Iterable, Iterator, Optional

    from typing_extensions import TypeVar

    _T = TypeVar("_T")

    def accumulate(
        iterable: Iterable[_T],
        func: Callable[[_T, _T], _T] = operator.add,
        *,
        initial: Optional[_T] = None,
    ) -> Iterator[_T]:
        if initial is not None:
            yield from _accumulate((initial, *iterable), func=func)
        else:
            yield from _accumulate(iterable, func=func)

elif sys.version_info < (3, 7):
    import operator
    from typing import Any, Callable, Iterable, Iterator, Optional

    from typing_extensions import TypeVar

    _T = TypeVar("_T")

    def accumulate(
        iterable: Iterable[_T],
        func: Callable[[_T, _T], _T] = operator.add,
        *,
        initial: Optional[_T] = None,
    ) -> Iterator[_T]:
        "Return running totals"
        # accumulate([1,2,3,4,5]) --> 1 3 6 10 15
        # accumulate([1,2,3,4,5], initial=100) --> 100 101 103 106 110 115
        # accumulate([1,2,3,4,5], operator.mul) --> 1 2 6 24 120
        it = iter(iterable)
        total = initial
        if initial is None:
            try:
                total = next(it)
            except StopIteration:
                return
        yield total
        for element in it:
            total = func(total, element)
            yield total
