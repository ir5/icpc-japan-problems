import os
from typing import Any

from ijproblems.internal_functions.interface import InterfaceInternalFunctions


def get_internal_functions(*args: Any) -> InterfaceInternalFunctions:
    if os.environ.get("USE_MOCK"):
        from ijproblems.internal_functions.mock import MockInternalFunctions  # noqa

        return MockInternalFunctions(*args)
    else:
        from ijproblems.internal_functions.impl import ImplInternalFunctions  # noqa

        return ImplInternalFunctions(*args)
