import aioredis

from data.config import REDIS_URL, SEARCH_RESULTS_CACHING_TIME


async def set_cache_data(key: str, value: str, ex: int = SEARCH_RESULTS_CACHING_TIME):
    redis = aioredis.from_url(REDIS_URL + '?db=2', decode_responses=True)

    await redis.set(key, value, ex=ex)

    await redis.close()


async def get_cache_data(key: str) -> str | None:
    redis = aioredis.from_url(REDIS_URL + '?db=2', decode_responses=True)

    result = await redis.get(key)

    await redis.close()

    return result
