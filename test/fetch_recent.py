import asyncio
from src.client import fetch_recent_earthquakes


async def main():
    try:
        await fetch_recent_earthquakes(year=2026)
        print("Fetch de sismos recientes completado exitosamente.")
    except Exception as e:
        print(f"Error occurred: {e}")


asyncio.run(main())
