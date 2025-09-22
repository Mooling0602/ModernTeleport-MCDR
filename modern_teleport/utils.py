from collections.abc import Callable
from typing import Any


# Usage: @execute_if(lambda: bool | Callable -> bool)
# Modified from: https://github.com/Mooling0602/MoolingUtils-MCDR/blob/main/mutils/__init__.py
def execute_if(condition: bool | Callable[[], bool], raise_error: bool = False):
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            _condition = condition() if callable(condition) else condition
            if _condition:
                return func(*args, **kwargs)
            else:
                if raise_error:
                    raise RuntimeError("Condition forcely required is not met!")
            return None

        return wrapper

    return decorator
