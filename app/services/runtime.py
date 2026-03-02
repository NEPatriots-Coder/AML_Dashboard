from app.services.cache import TTLCache


runtime_cache: TTLCache | None = None


def init_runtime_cache(ttl_seconds: int) -> TTLCache:
    global runtime_cache
    runtime_cache = TTLCache(ttl_seconds=ttl_seconds)
    return runtime_cache
