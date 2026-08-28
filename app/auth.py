"""Minimal session authentication primitives for the Phase 3 foundation."""

from functools import wraps

from flask import abort, g, session
from werkzeug.security import check_password_hash

from app.models.user import User


def authenticate(email, password):
    user = User.query.filter_by(email=email, status="active").first()
    if not user or not check_password_hash(user.password_hash, password):
        return None
    return user


def login_user(user):
    session.clear()
    session["user_id"] = user.id
    g.current_user = user


def logout_user():
    session.clear()
    g.pop("current_user", None)


def load_current_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.current_user = None
        return None
    user = User.query.filter_by(id=user_id, status="active").first()
    if user is None:
        session.clear()
    g.current_user = user
    return user


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if load_current_user() is None:
            abort(401)
        return fn(*args, **kwargs)

    return wrapper
