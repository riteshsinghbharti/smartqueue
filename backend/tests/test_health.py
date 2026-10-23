import pytest

@pytest.mark.asyncio
async def test_health_check_endpoint(client):
    """Verifies that the /health endpoint returns healthy status for cron ping."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Verifies root endpoint documentation link and service status."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "docs" in data
