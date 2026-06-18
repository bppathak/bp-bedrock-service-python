from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/bp-api/healthcheck")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_submission_flow() -> None:
    create_response = client.post(
        "/bp-api/submission/new",
        json={"presenter": {"email": "test@example.com", "display_name": "Test User"}},
    )
    assert create_response.status_code == 200
    submission = create_response.json()
    submission_id = submission["id"]

    payment_response = client.put(
        f"/bp-api/submission/{submission_id}/payment",
        json={"payment_reference": "PAY-123"},
    )
    assert payment_response.status_code == 200

    form_response = client.put(
        f"/bp-api/submission/{submission_id}/formType",
        json={"form_type": "passport"},
    )
    assert form_response.status_code == 200

    file_response = client.put(
        f"/bp-api/submission/{submission_id}/files",
        files={"file": ("test.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
    )
    assert file_response.status_code == 200
    assert file_response.json()["form"]["file_details"][0]["conversion_status"] == "WAITING"

    submit_response = client.put(
        f"/bp-api/submission/{submission_id}",
        json={"status": "SUBMITTED"},
    )
    assert submit_response.status_code == 200
    submitted = submit_response.json()
    assert submitted["status"] == "SUBMITTED"
    assert submitted["form"]["file_details"][0]["conversion_status"] == "QUEUED"
