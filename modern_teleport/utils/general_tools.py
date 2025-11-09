from typing import Callable, TypeVar, ParamSpec
from functools import wraps

P = ParamSpec("P")
T = TypeVar("T")


class ConditionError(RuntimeError):
    pass


def execute_if(
    condition: bool | Callable[[], bool],
    raise_error: bool = False
):
    def decorator(func: Callable[P, T]) -> Callable[P, T | None]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            _condition: bool = (
                condition() if callable(condition) else condition
            )
            if _condition:
                return func(*args, **kwargs)
            else:
                if raise_error:
                    raise ConditionError("Condition must be satisfied!")
                return None

        return wrapper

    return decorator
