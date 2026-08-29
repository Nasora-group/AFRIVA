def test_protected_route_does_not_bypass_security_context(app, monkeypatch):
    calls = {"auth": 0, "tenant": 0}

    def auth():
        calls["auth"] += 1

    def tenant():
        calls["tenant"] += 1

    monkeypatch.setattr("app.auth.load_current_user", auth)
    monkeypatch.setattr("app.middleware.tenant_middleware.load_tenant_context", tenant)

    response = app.test_client().get("/api/v1/analytics/summary")

    assert response.status_code in {200, 401, 403, 500}
    assert calls["auth"] == 1
    assert calls["tenant"] == 1
