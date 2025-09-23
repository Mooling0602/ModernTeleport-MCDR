from collections.abc import Callable
from functools import wraps
from typing import TypeVar, ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


def execute_if(condition: bool | Callable[[], bool], raise_error: bool = False):
    def decorator(func: Callable[P, T]) -> Callable[P, T | None]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            _condition = condition() if callable(condition) else condition
            if _condition:
                return func(*args, **kwargs)
            else:
                if raise_error:
                    raise RuntimeError("Condition forcely required is not met!")
            return None

        return wrapper

    return decorator
