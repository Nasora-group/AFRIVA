from app.models import Client, Commercial, Prospection, Prospect, Sale, db


def test_analytics_summary_is_tenant_scoped(app, tenant, monkeypatch):
    org = tenant
    commercial = Commercial(
        organization_id=org.id, first_name="A", last_name="Commercial"
    )
    client = Client(organization_id=org.id, name="Client BI")
    prospect = Prospect(organization_id=org.id, name="Prospect BI")
    db.session.add_all([commercial, client, prospect])
    db.session.flush()
    db.session.add(
        Sale(
            organization_id=org.id,
            commercial_id=commercial.id,
            client_id=client.id,
            status="completed",
            total_amount=12500,
        )
    )
    db.session.add(
        Prospection(
            organization_id=org.id,
            commercial_id=commercial.id,
            prospect_id=prospect.id,
        )
    )
    db.session.commit()
    monkeypatch.setattr("app.api.analytics.get_current_organization", lambda: org)

    response = app.test_client().get("/api/v1/analytics/summary?period=all")

    assert response.status_code == 200
    data = response.get_json()
    assert data["revenue"] == "12500.00"
    assert data["sales_count"] == 1
    assert data["clients"] == 1
    assert data["prospections"] == 1
