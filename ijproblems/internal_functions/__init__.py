import os

if os.environ.get("USE_MOCK"):
    from ijproblems.internal_functions.mock import (  # noqa
        MockInternalFunctions as InternalFunctions,
    )
