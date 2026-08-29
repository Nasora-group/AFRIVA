def test_protected_route_does_not_bypass_security_context(app, monkeypatch):
    calls = {"auth": 0, "tenant": 0}

    def auth():
        calls["auth"] += 1

    def tenant():
        calls["tenant"] += 1

    monkeypatch.setattr("app.load_current_user", auth)
    monkeypatch.setattr("app.load_tenant_context", tenant)

    response = app.test_client().get("/api/v1/analytics/summary")

    assert response.status_code in {401, 403, 500}
    assert calls["auth"] == 1
    assert calls["tenant"] == 1
