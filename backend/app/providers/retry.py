import asyncio
from typing import Callable, Any

class AIProviderFailed(Exception):
    pass

class InvalidAPIKey(Exception):
    pass

class MalformedRequest(Exception):
    pass

async def with_retry(fn: Callable[[], Any], max_retries: int = 3, timeout: int = 10, base_delay: float = 1.0) -> Any:
    for attempt in range(max_retries + 1):
        try:
            return await asyncio.wait_for(fn(), timeout=timeout)
        except (TimeoutError, ConnectionError) as e:
            if attempt == max_retries:
                raise AIProviderFailed(f"Failed after {max_retries} retries. Last error: {e}")
            await asyncio.sleep(base_delay * (2 ** attempt))
        except (InvalidAPIKey, MalformedRequest):
            raise  # Do not retry fatal errors
        except Exception as e:
            if attempt == max_retries:
                raise AIProviderFailed(f"Failed after {max_retries} retries. Last error: {e}")
            await asyncio.sleep(base_delay * (2 ** attempt))
