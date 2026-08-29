"""Server-rendered AFRIVA web interface."""

from flask import Blueprint, g, redirect, render_template, request, url_for

from app.auth import authenticate, login_user, logout_user
from app.middleware.tenant_middleware import load_tenant_context

web_bp = Blueprint("web", __name__)


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if getattr(g, "current_user", None) is not None:
        load_tenant_context()
        return redirect(url_for("web.dashboard"))

    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = authenticate(email, password)
        if user is None:
            error = "Email ou mot de passe incorrect."
        else:
            login_user(user)
            load_tenant_context()
            return redirect(url_for("web.dashboard"))
    return render_template("login.html", error=error)


@web_bp.post("/logout")
def logout():
    logout_user()
    return redirect(url_for("web.login"))


@web_bp.get("/dashboard")
def dashboard():
    if getattr(g, "current_user", None) is None:
        return redirect(url_for("web.login"))
    load_tenant_context()
    return render_template("dashboard.html", user=g.current_user, organization=g.current_organization)
