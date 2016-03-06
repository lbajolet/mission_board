from .defaults import *

if os.environ.get("MB_PROD", None):
    from .prod import *
else:
    from .dev import *
