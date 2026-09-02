import httpx
from app.config import settings

async def get_ip_geolocation(ip: str) -> dict:
    # Handle local loopback IP for testing environment
    if ip in ["127.0.0.1", "localhost", "::1"]:
        ip = "8.8.8.8"  # Fallback public IP for standard local testing

    # Fallback Chain Provider A: ip-api.com
    try:
        if not settings.GEO_PROVIDER_A_ENABLED:
            raise RuntimeError("provider A disabled")
        if settings.MOCK_GEO_PROVIDER_A:
            return {"provider": "mock-a", "country": "United States", "city": "Ashburn"}
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    return {
                        "provider": "ip-api",
                        "country": data.get("country"),
                        "city": data.get("city")
                    }
    except Exception:
        pass

    # Fallback Chain Provider B: ipapi.co
    try:
        if not settings.GEO_PROVIDER_B_ENABLED:
            raise RuntimeError("provider B disabled")
        if settings.MOCK_GEO_PROVIDER_B:
            return {"provider": "mock-b", "country": "Canada", "city": "Toronto"}
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"https://ipapi.co/{ip}/json/")
            if resp.status_code == 200:
                data = resp.json()
                if not data.get("error"):
                    return {
                        "provider": "ipapi",
                        "country": data.get("country_name"),
                        "city": data.get("city")
                    }
    except Exception:
        pass

    # Complete Fallback (When all providers fail/are offline)
    return {"provider": "none", "country": "Unknown", "city": "Unknown"}