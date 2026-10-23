import pytest
import asyncio
from app.core.cache import InMemoryCache

@pytest.mark.asyncio
async def test_cache_set_and_get():
    """Verifies basic cache set and get operations."""
    cache = InMemoryCache(default_ttl=5)
    await cache.set("key1", {"token": 42})
    val = await cache.get("key1")
    assert val == {"token": 42}

@pytest.mark.asyncio
async def test_cache_ttl_expiry():
    """Verifies that expired cache entries return None."""
    cache = InMemoryCache(default_ttl=1)
    await cache.set("short_key", "temporary_value", ttl=1)
    assert await cache.get("short_key") == "temporary_value"
    await asyncio.sleep(1.1)
    assert await cache.get("short_key") is None

@pytest.mark.asyncio
async def test_cache_queue_invalidation():
    """Verifies that invalidating a queue removes all its cached tickets."""
    cache = InMemoryCache(default_ttl=10)
    queue_id = "test-clinic-uuid"
    await cache.set("ticket_status:t1", {"pos": 1}, queue_id=queue_id)
    await cache.set("ticket_status:t2", {"pos": 2}, queue_id=queue_id)
    await cache.set("ticket_status:other", {"pos": 99}, queue_id="another-queue")

    # Invalidate test clinic
    await cache.invalidate_queue(queue_id)

    assert await cache.get("ticket_status:t1") is None
    assert await cache.get("ticket_status:t2") is None
    assert await cache.get("ticket_status:other") == {"pos": 99}
