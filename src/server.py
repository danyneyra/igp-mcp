from datetime import date
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from models import (
    Earthquake,
    last_to_earthquake,
    recent_to_earthquake,
    EarthquakeSearchFilters,
)
from client import fetch_last_earthquake, fetch_recent_earthquakes
from services import search_earthquakes as search_earthquakes_service


from mcp.types import Icon

svg_icon = Icon(
    src="PHN2ZyB2ZXJzaW9uPSIxLjIiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgdmlld0JveD0iMCAwIDI1NiAyNTYiIHdpZHRoPSIyNTYiIGhlaWdodD0iMjU2Ij48c3R5bGU+LmF7ZmlsbDojZmZmfS5ie2ZpbGw6IzAzOTVmZX0uY3tmaWxsOiMwMzAzZmV9LmR7ZmlsbDojMDQwNGFkfS5le2ZpbGw6IzAzMDNhZH0uZntmaWxsOiMwNjA2YWV9Lmd7ZmlsbDojMDUwNWFlfS5oe2ZpbGw6IzA1MDVmZX08L3N0eWxlPjxwYXRoIGZpbGwtcnVsZT0iZXZlbm9kZCIgY2xhc3M9ImEiIGQ9Im0xMjkgMjQ2Yy02NC40IDAtMTE2LjUtNTIuMS0xMTYuNS0xMTYuNSAwLTY0LjQgNTIuMS0xMTYuNSAxMTYuNS0xMTYuNSA2NC40IDAgMTE2LjUgNTIuMSAxMTYuNSAxMTYuNSAwIDY0LjQtNTIuMSAxMTYuNS0xMTYuNSAxMTYuNXoiLz48cGF0aCBjbGFzcz0iYiIgZD0ibTUxLjUgMTExLjVjLTEyLjEtMi4zLTIzLjktNC41LTM2LjEtNi43IDItMTAuMyA1LjgtMjAuNyAxMS4xLTMwLjcgNC40LTguMSA0LjUtOCAxMy42LTYuNSA1NC43IDkgOTYuNyAzNy4zIDEyNi40IDgzLjggMTQuMiAyMi4xIDIyLjIgNDYuNyAyNS4zIDcyLjggMC4yIDEuNS0wLjIgMy44LTEuMiA0LjQtMTEuNiA2LjktMjMuOCAxMi40LTM3LjIgMTQuOC01LjktNjUuOC0zOC41LTExMC42LTEwMS45LTEzMS45eiIvPjxwYXRoIGNsYXNzPSJjIiBkPSJtMTE2LjEgMTYwLjljMTkuOCAyNC41IDI5LjggNTIuMiAzMC40IDgzLjktMTMuNiAwLTI2LjggMC0zOC40IDAtMy41LTEyLjktNS4zLTI1LTkuOS0zNS44LTEyLjctMjkuMS0zNS00Ny4zLTY2LjItNTQuMi00LjYtMS05LjMtMS4xLTEzLjgtMi4yLTEuNS0wLjMtMy43LTItMy44LTMuMi0wLjgtMTIuMy0xLjMtMjQuNS0xLjktMzcuNCA0Mi43IDEuNCA3Ni42IDE3LjMgMTAzLjYgNDguOXoiLz48cGF0aCBjbGFzcz0iZCIgZD0ibTE4NC4zIDE2N2MtMS42LTEuMS0zLjItMS44LTMuOC0zLjEtMTguOS0zNy00Ni40LTY1LjYtODMuNy04NC4zLTMuMy0xLjctNC45LTQtNS42LTcuNS0yLjktMTYuMy0yLjktMzIuNSAwLTQ4LjcgMC43LTMuNiAyLjQtNS4xIDUuOS02LjIgMTIuOS00IDI2LTQuOSAzOS42LTQuMi0xMy4zIDM0LjYtOS4zIDY2LjMgMTcgOTIuNCAyNi4xIDI2IDU3LjcgMjkuOSA5MiAxNi43IDAuNyAxNC0wLjYgMjcuNS00LjQgNDAuNy0wLjkgMi45LTIuNSA0LjEtNS41IDQuNi0xNy4xIDMuMy0zNC4xIDMuMS01MS41LTAuNHoiLz48cGF0aCBjbGFzcz0iZSIgZD0ibTE1MS4yIDE0LjdjMTEuMyAyLjMgMjEuOCA1LjcgMzIuMSAxMS4yLTUuNiA4LjctOC45IDE3LjgtNi44IDI3LjkgMS42IDcuOCA1LjMgMTQuNiAxMS4zIDIwIDExLjkgMTAuOCAyNi40IDExLjUgNDUuMSAxLjcgNi4xIDExLjggMTAuMyAyNC4xIDExLjggMzcuMyAwLjIgMS4yLTEuOCAzLjMtMy4zIDMuOS0xNi42IDcuMS0zMy43IDguNy01MS4yIDMuNS0yNC03LjItNDAuOS0yMi43LTQ5LjgtNDUuOC03LjQtMTkuNC02LjUtMzkuMiAyLjEtNTguNCAyLTQuMyA1LjQtMS41IDguNy0xLjN6Ii8+PHBhdGggY2xhc3M9ImQiIGQ9Im04MCAyMzUuMWMtMzIuNS0xNi01My40LTQxLjEtNjMuNC03NS43IDQyLjUtMC4xIDgyLjQgMzggODIuOSA4My4yLTYuNi0yLjYtMTIuOC01LTE5LjUtNy41eiIvPjxwYXRoIGNsYXNzPSJmIiBkPSJtNTYuNCA2NC41Yy03LjEtMS4zLTEzLjctMi42LTIxLjItNCAxMi45LTE3LjcgMjkuMy0zMC40IDUwLjEtMzkuMy0zLjIgMTcuOC0zLjYgMzUgMC4xIDUyLjItOS44LTMtMTkuMi01LjktMjktOC45eiIvPjxwYXRoIGNsYXNzPSJnIiBkPSJtMTk3LjEgMjE3LjhjLTEuNi03LjktMi45LTE1LjUtNC45LTIyLjktMS45LTcuMS00LjYtMTQtNy4xLTIxLjQgMTcuNCAzLjIgMzQuNSAzLjIgNTIuNC0wLjEtOC43IDIwLjYtMjEuNSAzNi45LTM5LjEgNTAtMC41LTIuMS0wLjktMy42LTEuMy01LjZ6Ii8+PHBhdGggY2xhc3M9ImgiIGQ9Im0xOTIuNCA2OS42Yy0xMi40LTExLjYtMTMuNi0yOS4zLTIuOS00MC4zIDE2LjYgMTAgMjkuOCAyMy4zIDM5LjkgMzkuOC05LjIgOS44LTI0LjggMTAtMzcgMC41eiIvPjwvc3ZnPg==",
    mime_type="image/svg+xml",
)

mcp = FastMCP(
    name="IGP MCP",
    instructions=(
        "IGP MCP permite consultar información sobre los últimos sismos ocurridos en Perú a través de la API del Instituto Geofísico del Perú (IGP)."
        " Puede buscar sismos utilizando filtros como año, rango de fechas, magnitud, profundidad, latitud, longitud y referencia geográfica. "
        "La búsqueda por referencia es textual y aproximada, por lo que puede no ser exacta. Se recomienda utilizar palabras clave relevantes para obtener mejores resultados. "
        "Todos los filtros son opcionales y pueden combinarse para refinar la búsqueda. "
    ),
    icons=[svg_icon],
    version="0.1.0",
    website_url="https://ultimosismo.igp.gob.pe/",
)


@mcp.tool
async def get_last_earthquake() -> Earthquake:
    "Obtiene la información del último sismo ocurrido en Perú."
    item = await fetch_last_earthquake()
    return last_to_earthquake(item)


@mcp.tool
async def get_recent_earthquakes(
    year: int = 2026, limit: Annotated[int, Field(ge=1, le=200)] = 5
) -> list[Earthquake]:
    "Obtiene la información de los sismos recientes ocurridos en Perú."
    # Fetch de sismos recientes
    data = await fetch_recent_earthquakes(year)
    # Convertir los datos a objetos Earthquake
    earthquakes = [recent_to_earthquake(item) for item in data]
    # Ordenar los sismos por fecha de ocurrencia (de más reciente a más antiguo)
    earthquakes.sort(key=lambda eq: eq.occurred_at, reverse=True)
    # Limitar la cantidad de resultados según el parámetro limit
    return earthquakes[:limit]


@mcp.tool
async def search_earthquakes(
    year: int = 2026,
    start_date: date | None = None,
    end_date: date | None = None,
    min_magnitude: float | None = None,
    max_magnitude: float | None = None,
    min_depth: float | None = None,
    max_depth: float | None = None,
    min_latitude: float | None = None,
    max_latitude: float | None = None,
    min_longitude: float | None = None,
    max_longitude: float | None = None,
    reference: str | None = None,
    limit: int = 20,
) -> list[Earthquake]:
    "Busca sismos según los filtros proporcionados."
    # Validar los filtros antes de consultar la API
    filters = EarthquakeSearchFilters(
        year=year,
        start_date=start_date,
        end_date=end_date,
        min_magnitude=min_magnitude,
        max_magnitude=max_magnitude,
        min_depth=min_depth,
        max_depth=max_depth,
        min_latitude=min_latitude,
        max_latitude=max_latitude,
        min_longitude=min_longitude,
        max_longitude=max_longitude,
        reference=reference,
        limit=limit,
    )
    # Fetch de sismos recientes
    data = await fetch_recent_earthquakes(filters.year)
    # Convertir los datos a objetos Earthquake
    earthquakes = [recent_to_earthquake(item) for item in data]
    # Aplicar filtros
    return search_earthquakes_service(earthquakes, filters)


@mcp.resource("igp://about")
def igp_about() -> str:
    "IGP MCP permite consultar información sobre los últimos sismos ocurridos en Perú a través de la API del Instituto Geofísico del Perú (IGP)."
    return (
        "El Instituto Geofísico del Perú (IGP) es la institución encargada de "
        "monitorear y estudiar los fenómenos geofísicos en el país, incluyendo "
        "los sismos. Su API proporciona información sobre los últimos sismos "
        "ocurridos en Perú, incluyendo detalles como magnitud, profundidad, "
        "ubicación y hora de ocurrencia."
    )


@mcp.resource("igp://search-guide")
def search_guide() -> str:
    "Guía para buscar sismos según diferentes criterios."
    return (
        "Puede buscar sismos utilizando los siguientes filtros:\n"
        "- year: Filtra sismos por año de ocurrencia.\n"
        "- start_date y end_date: Filtra sismos por un rango de fechas, acepta fechas en formato YYYY-MM-DD.\n"
        "- min_magnitude y max_magnitude: Filtra sismos por magnitud, acepta valores entre 0.0 y 10.0.\n"
        "- min_depth y max_depth: Filtra sismos por profundidad, acepta valores entre 0.0 y 100.0 km.\n"
        "- min_latitude y max_latitude: Filtra sismos por latitud, acepta valores entre -90.0 y 90.0.\n"
        "- min_longitude y max_longitude: Filtra sismos por longitud, acepta valores entre -180.0 y 180.0.\n"
        "- reference: Filtra sismos por referencia geográfica, puede ser una ciudad, región o cualquier descripción textual de la ubicación del sismo.\n"
        "- limit: Limita la cantidad de resultados devueltos, acepta valores entre 1 y 200.\n"
        "La busqueda por reference es textual y aproximada, por lo que puede no ser exacta. Se recomienda utilizar palabras clave relevantes para obtener mejores resultados.\n"
        "Todos los filtros son opcionales y pueden combinarse para refinar la búsqueda. "
    )


@mcp.prompt
def analyze_region(year: int, region: str) -> str:
    "Analiza los sismos ocurridos en una región específica durante un año determinado."
    return (
        f"Analizando los sismos ocurridos en la región '{region}' durante el año {year}. "
        "Se proporcionará un resumen de la actividad sísmica, incluyendo la cantidad de sismos, "
        "la magnitud promedio y la profundidad promedio de los eventos registrados."
        "Indica que la busqueda geográfica es aproximada y que se recomienda utilizar palabras clave relevantes para obtener mejores resultados."
    )


@mcp.prompt
def find_significant_earthquakes(year: int, min_magnitude: float = 4.0) -> str:
    "Encuentra sismos significativos ocurridos en un año determinado con una magnitud mínima especificada."
    return (
        f"Buscando sismos significativos ocurridos en el año {year} con una magnitud mínima de {min_magnitude}. "
        "Se proporcionará una lista de los eventos sísmicos que cumplen con los criterios especificados, "
        "incluyendo detalles como la fecha, hora, ubicación, magnitud y profundidad de cada sismo registrado."
    )


# Ejecutar el servidor MCP
if __name__ == "__main__":
    mcp.run()
