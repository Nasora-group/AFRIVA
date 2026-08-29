"""Server-rendered AFRIVA web interface."""

from flask import Blueprint, g, redirect, render_template, request, url_for

from app.auth import authenticate, load_current_user, login_user, logout_user
from app.middleware.tenant_middleware import load_tenant_context

web_bp = Blueprint("web", __name__)


def _page(template):
    if load_current_user() is None:
        return redirect(url_for("web.login"))
    load_tenant_context()
    return render_template(
        template,
        user=g.current_user,
        organization=g.current_organization,
    )


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    load_current_user()
    if getattr(g, "current_user", None) is not None:
        load_tenant_context()
        return redirect(url_for("web.dashboard"))

    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
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
    return _page("dashboard.html")


@web_bp.get("/crm")
def crm():
    return _page("crm.html")


@web_bp.get("/sales")
def sales():
    return _page("sales.html")


@web_bp.get("/pos")
def pos():
    return _page("pos.html")


@web_bp.get("/stock")
def stock():
    return _page("stock.html")


@web_bp.get("/billing")
def billing():
    return _page("billing.html")


@web_bp.get("/analytics")
def analytics():
    return _page("analytics.html")
