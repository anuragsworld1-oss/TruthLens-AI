"""
Shared Flask extensions.
Limiter is initialized here so route modules can decorate endpoints
without creating a second app-bound instance.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    storage_uri="memory://",
)
