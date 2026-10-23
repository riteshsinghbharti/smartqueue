import pytest

@pytest.mark.asyncio
async def test_patient_join_and_smart_polling(client):
    """Tests patient intake, token generation, smart polling position, and queue progression."""
    # 1. Create clinic
    await client.post("/api/queues", json={
        "name": "Beacon Clinic",
        "slug": "beacon-clinic",
        "doctor_name": "Dr. Sarah",
        "avg_consultation_time_mins": 10,
        "is_active": True
    })

    # 2. First patient joins
    p1_res = await client.post("/api/queues/beacon-clinic/join", json={
        "patient_name": "Alice Green",
        "age": 28,
        "gender": "Female",
        "note": "Flu symptoms"
    })
    assert p1_res.status_code == 201
    p1 = p1_res.json()
    assert p1["token_number"] == 1

    # 3. Second patient joins
    p2_res = await client.post("/api/queues/beacon-clinic/join", json={
        "patient_name": "Bob Stone",
        "age": 45,
        "gender": "Male"
    })
    assert p2_res.status_code == 201
    p2 = p2_res.json()
    assert p2["token_number"] == 2

    # 4. Check Bob's status via smart-polling
    bob_status = await client.get(f"/api/tickets/{p2['id']}/status")
    assert bob_status.status_code == 200
    bob_data = bob_status.json()
    assert bob_data["token_number"] == 2
    assert bob_data["position_ahead"] == 1
    assert bob_data["estimated_wait_mins"] == 10

    # 5. Doctor advances queue: calls Alice
    next_res = await client.post("/api/queues/beacon-clinic/call-next")
    assert next_res.status_code == 200

    # 6. Check Bob's updated status (is_up_next should now be true)
    bob_status_updated = await client.get(f"/api/tickets/{p2['id']}/status")
    assert bob_status_updated.status_code == 200
    bob_updated_data = bob_status_updated.json()
    assert bob_updated_data["is_up_next"] is True
