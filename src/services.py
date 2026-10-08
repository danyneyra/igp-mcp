import unicodedata
from models import Earthquake, EarthquakeSearchFilters


def normalize_string(value: str) -> str:
    """Normaliza una cadena de texto eliminando acentos y caracteres especiales."""
    normalized_string = unicodedata.normalize("NFD", value)
    return "".join(
        c for c in normalized_string if unicodedata.category(c) != "Mn"
    ).lower()


def search_earthquakes(earthquakes: list[Earthquake], filters: EarthquakeSearchFilters):
    results = list(earthquakes)

    # Filtro por año
    if filters.year is not None:
        results = [eq for eq in results if eq.occurred_at.year == filters.year]

    # Filtro por rango de fechas
    if filters.start_date is not None:
        results = [eq for eq in results if filters.start_date <= eq.occurred_at.date()]
    if filters.end_date is not None:
        results = [eq for eq in results if eq.occurred_at.date() <= filters.end_date]

    # Filtro por magnitud
    if filters.min_magnitude is not None:
        results = [eq for eq in results if filters.min_magnitude <= eq.magnitud]
    if filters.max_magnitude is not None:
        results = [eq for eq in results if eq.magnitud <= filters.max_magnitude]

    # Filtro por profundidad
    if filters.min_depth is not None:
        results = [eq for eq in results if filters.min_depth <= eq.profundidad]
    if filters.max_depth is not None:
        results = [eq for eq in results if eq.profundidad <= filters.max_depth]

    # Filtro por latitud
    if filters.min_latitude is not None and filters.max_latitude is not None:
        results = [
            eq
            for eq in results
            if filters.min_latitude <= eq.latitud <= filters.max_latitude
        ]

    # Filtro por longitud
    if filters.min_longitude is not None and filters.max_longitude is not None:
        results = [
            eq
            for eq in results
            if filters.min_longitude <= eq.longitud <= filters.max_longitude
        ]

    # Filtro por referencia
    if filters.reference is not None:
        normalized_reference = normalize_string(filters.reference)
        results = [
            eq
            for eq in results
            if normalized_reference in normalize_string(eq.referencia)
        ]

    results.sort(key=lambda eq: eq.occurred_at, reverse=True)

    return results[: filters.limit]
