import os

if os.environ.get("USE_MOCK"):
    from ijproblems.internal_functions.mock import (  # noqa
        MockInternalFunctions as InternalFunctions,
    )
else:
    from ijproblems.internal_functions.impl import (  # noqa
        InternalFunctions
    )
