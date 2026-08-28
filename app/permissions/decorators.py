"""RBAC permission decorators scoped to the active organization membership."""

from functools import wraps

from flask import abort, g


def require_permission(permission_name):
    def decorator(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            membership = getattr(g, "current_membership", None)
            user = getattr(g, "current_user", None)
            if user is None or membership is None:
                abort(401)

            permissions = {permission.name for permission in membership.role.permissions}
            if permission_name not in permissions:
                abort(403)
            return fn(*args, **kwargs)

        return decorated_function

    return decorator
