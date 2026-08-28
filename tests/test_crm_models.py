from app.models import (
    Client,
    Commercial,
    Contact,
    Prospect,
    Prospection,
    Tour,
    TourStop,
    Visit,
    db,
)


def test_crm_models_are_registered(app):
    with app.app_context():
        expected = {
            "commercial",
            "client",
            "prospect",
            "contact",
            "visit",
            "prospection",
            "tour",
            "tour_stop",
        }
        assert expected.issubset(set(db.metadata.tables))


def test_crm_models_inherit_tenant_awareness():
    for model in (
        Commercial,
        Client,
        Prospect,
        Contact,
        Visit,
        Prospection,
        Tour,
        TourStop,
    ):
        assert hasattr(model, "organization_id")
        assert hasattr(model, "deleted_at")


def test_crm_relationships_are_defined():
    assert Commercial.clients.property.back_populates == "commercial"
    assert Commercial.prospects.property.back_populates == "commercial"
    assert Commercial.visits.property.back_populates == "commercial"
    assert Commercial.prospections.property.back_populates == "commercial"
    assert Client.visits.property.back_populates == "client"
    assert Prospect.visits.property.back_populates == "prospect"
    assert Tour.stops.property.back_populates == "tour"
