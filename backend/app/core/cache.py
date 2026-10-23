import time
import asyncio
from typing import Any, Dict, Optional, Set

class InMemoryCache:
    """
    High-performance in-memory cache with TTL and event-driven invalidation.
    Dramatically reduces database load by serving smart-polling requests directly from memory.
    """
    def __init__(self, default_ttl: int = 30):
        self._store: Dict[str, Dict[str, Any]] = {}
        # Track which ticket keys belong to which queue for targeted invalidation
        self._queue_ticket_keys: Dict[str, Set[str]] = {}
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            
            # Check expiry
            if time.time() > entry["expires_at"]:
                del self._store[key]
                return None
            
            return entry["data"]

    async def set(self, key: str, data: Any, ttl: Optional[int] = None, queue_id: Optional[str] = None) -> None:
        async with self._lock:
            expires_at = time.time() + (ttl if ttl is not None else self._default_ttl)
            self._store[key] = {
                "data": data,
                "expires_at": expires_at
            }
            if queue_id:
                if queue_id not in self._queue_ticket_keys:
                    self._queue_ticket_keys[queue_id] = set()
                self._queue_ticket_keys[queue_id].add(key)

    async def invalidate(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def invalidate_queue(self, queue_id: str) -> None:
        """
        Invalidates all cached state and ticket statuses associated with a specific queue.
        Triggered when a patient joins, gets called, or finishes consultation.
        """
        async with self._lock:
            # Invalidate queue summary entries
            self._store.pop(f"queue_summary:{queue_id}", None)
            
            # Invalidate all associated ticket keys
            ticket_keys = self._queue_ticket_keys.pop(queue_id, set())
            for key in ticket_keys:
                self._store.pop(key, None)

    async def clear_expired(self) -> None:
        """Periodic cleanup for memory hygiene."""
        async with self._lock:
            now = time.time()
            expired_keys = [k for k, v in self._store.items() if now > v["expires_at"]]
            for k in expired_keys:
                del self._store[k]

cache = InMemoryCache(default_ttl=30)
