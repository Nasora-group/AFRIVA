from app.models import Client, Commercial, Prospection, Product, Sale, db


def test_analytics_summary_is_tenant_scoped(app, inventory_context, monkeypatch):
    org, _, _, product = inventory_context
    commercial = Commercial(
        organization_id=org.id, first_name="A", last_name="Commercial"
    )
    client = Client(organization_id=org.id, name="Client BI")
    db.session.add_all([commercial, client])
    db.session.flush()
    sale = Sale(
        organization_id=org.id,
        commercial_id=commercial.id,
        client_id=client.id,
        status="completed",
        total_amount=12500,
    )
    db.session.add(sale)
    db.session.add(
        Prospection(
            organization_id=org.id,
            commercial_id=commercial.id,
            prospect_id=inventory_context[4].id,
        )
    )
    db.session.commit()
    monkeypatch.setattr(
        "app.api.analytics.get_current_organization", lambda: org
    )

    response = app.test_client().get("/api/v1/analytics/summary?period=all")

    assert response.status_code == 200
    data = response.get_json()
    assert data["revenue"] == "12500.00"
    assert data["sales_count"] == 1
    assert data["clients"] == 1
    assert data["prospections"] == 1
