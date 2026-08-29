def test_health_endpoint_is_public(app):
    response = app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_index_endpoint_is_public(app):
    response = app.test_client().get("/")

    assert response.status_code == 200
    assert response.content_type.startswith("text/html")
    assert b"AFRIVA SAAS" in response.data
    assert b"Gestion commerciale" in response.data
