import httpx2

from models import LastEarthquake, RecentEarthquake

IGP_BASE_URL = "https://ultimosismo.igp.gob.pe/api"


async def request_json(url: str):
    async with httpx2.AsyncClient() as client:
        response = await client.get(IGP_BASE_URL + url)
        response.raise_for_status()
        return response.json()


# Fetch de último sismo
async def fetch_last_earthquake() -> LastEarthquake:
    data = await request_json("/ultimo-sismo")
    return LastEarthquake.model_validate(data)


# Fetch de sismos recientes
async def fetch_recent_earthquakes(year: int = 2026) -> list[RecentEarthquake]:
    try:
        data = await request_json(f"/ultimo-sismo/ajaxb/{str(year)}")
        return [RecentEarthquake.model_validate(earthquake) for earthquake in data]
    except httpx2.HTTPStatusError as e:
        if e.response.status_code == 404:
            return []
        raise
    except httpx2.RequestError as e:
        raise RuntimeError(f"Error al realizar la solicitud: {e}") from e
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise RuntimeError(f"Error inesperado: {e}") from e
