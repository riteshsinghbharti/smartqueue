import pytest

@pytest.mark.asyncio
async def test_create_and_fetch_clinic(client):
    """Tests creating a new clinic queue and retrieving its public info."""
    create_payload = {
        "name": "City Care Dental Clinic",
        "slug": "city-care-dental",
        "doctor_name": "Dr. Alex Turner, DDS",
        "avg_consultation_time_mins": 15,
        "is_active": True
    }
    res = await client.post("/api/queues", json=create_payload)
    assert res.status_code == 201
    created = res.json()
    assert created["slug"] == "city-care-dental"

    # Fetch public info
    info_res = await client.get("/api/queues/city-care-dental/info")
    assert info_res.status_code == 200
    info = info_res.json()
    assert info["name"] == "City Care Dental Clinic"
    assert info["total_waiting"] == 0

@pytest.mark.asyncio
async def test_duplicate_slug_rejected(client):
    """Tests that registering two clinics with the same slug returns 400."""
    payload = {
        "name": "Prime Clinic",
        "slug": "prime-clinic",
        "doctor_name": "Dr. Watson",
        "avg_consultation_time_mins": 10,
        "is_active": True
    }
    res1 = await client.post("/api/queues", json=payload)
    assert res1.status_code == 201

    res2 = await client.post("/api/queues", json=payload)
    assert res2.status_code == 400

@pytest.mark.asyncio
async def test_generate_qr_code(client):
    """Tests that generating QR code returns a valid PNG image."""
    payload = {
        "name": "Metro Health",
        "slug": "metro-health",
        "doctor_name": "Dr. House",
        "avg_consultation_time_mins": 10
    }
    await client.post("/api/queues", json=payload)

    qr_res = await client.get("/api/queues/metro-health/qr")
    assert qr_res.status_code == 200
    assert qr_res.headers["content-type"] == "image/png"
    assert len(qr_res.content) > 100
