import httpx


async def check_backend_health(
    url: str,
    timeout: float = 2.0,
) -> bool:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                url.rstrip("/") + "/health"
            )

        return response.status_code == 200

    except (httpx.TimeoutException, httpx.RequestError):
        return False
