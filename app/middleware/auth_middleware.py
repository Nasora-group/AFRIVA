"""Authentication primitives for the Phase 3 foundation.

A production authentication provider can populate g.current_user after
validating the secure session. Tenant middleware then verifies membership.
"""

from functools import wraps

from flask import abort, g


def set_current_user(user):
    g.current_user = user


def get_current_user():
    return getattr(g, "current_user", None)


def require_authentication(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        if get_current_user() is None:
            abort(401)
        return fn(*args, **kwargs)

    return decorated
