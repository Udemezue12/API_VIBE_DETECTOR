import json


from asgiref.sync import sync_to_async
from django.core.cache import cache


class AsyncCacheDependencies:
    async def get_from_cache(self, key):
        return await cache.aget(key)

    async def add_from_cache(self, key, value, timeout=600):
        return await cache.aadd(key, value, timeout)

    async def set_from_cache(self, key, value, timeout=60 * 10):
        return await cache.aset(key, value, timeout)

    async def delete_from_cache(self, key):
        return await sync_to_async(thread_sensitive=True)(key)


class SyncCacheDependencies:
    def get_from_cache(self, key):
        return cache.get(key)

    def add_to_cache(self, key, value, timeout=600):
        return cache.add(key, value, timeout=timeout)

    def set_from_cache(self, key, value, timeout=60 * 10):
        return cache.set(key, value, timeout=timeout)

    def delete_from_cache(self, key):
        return cache.delete(key)
