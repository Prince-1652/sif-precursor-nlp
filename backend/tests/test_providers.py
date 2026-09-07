import pytest
import asyncio
from app.providers.retry import with_retry, AIProviderFailed

async def success_fn():
    return "success"

async def timeout_fn():
    raise TimeoutError("timeout")

async def sometimes_fails_fn():
    if not hasattr(sometimes_fails_fn, "calls"):
        sometimes_fails_fn.calls = 0
    sometimes_fails_fn.calls += 1
    if sometimes_fails_fn.calls < 3:
        raise TimeoutError("timeout")
    return "success"

@pytest.mark.asyncio
async def test_retry_success():
    result = await with_retry(success_fn, max_retries=2, base_delay=0.01)
    assert result == "success"

@pytest.mark.asyncio
async def test_retry_eventual_success():
    sometimes_fails_fn.calls = 0
    result = await with_retry(sometimes_fails_fn, max_retries=3, base_delay=0.01)
    assert result == "success"
    assert sometimes_fails_fn.calls == 3

@pytest.mark.asyncio
async def test_retry_failure():
    with pytest.raises(AIProviderFailed):
        await with_retry(timeout_fn, max_retries=2, base_delay=0.01)
