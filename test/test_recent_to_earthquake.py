from datetime import datetime, timedelta, timezone
import unittest
from zoneinfo import ZoneInfo
from src.models import RecentEarthquake, recent_to_earthquake


# Test de la función recent_to_earthquake
def test_recent_to_earthquake():
    # Crear un objeto RecentEarthquake de prueba
    recent_earthquake_data = {
        "idlistasismos": 1,
        "codigo": "ABC123",
        "fecha_local": "2026-02-26T00:00:00.000Z",
        "hora_local": "1970-01-01T18:48:33.000Z",
        "fecha_utc": "2026-02-26T00:00:00.000Z",
        "hora_utc": "1970-01-01T23:48:33.000Z",
        "magnitud": 5.0,
        "profundidad": 10.0,
        "latitud": -12.0,
        "longitud": -77.0,
        "referencia": "Referencia de prueba",
        "intensidad": "Intensidad de prueba",
        "tipomagnitud": "Tipo de magnitud de prueba",
        "mapa": "URL del mapa de prueba",
        "informe": "URL del informe de prueba",
    }
    recent_earthquake = RecentEarthquake.model_validate(recent_earthquake_data)

    # Convertir a objeto Earthquake
    earthquake = recent_to_earthquake(recent_earthquake)

    # Verificar que los atributos se hayan asignado correctamente
    assert earthquake.id == recent_earthquake.idlistasismos
    assert earthquake.codigo == recent_earthquake.codigo
    assert earthquake.occurred_at == datetime(
        2026, 2, 26, 18, 48, 33,
        tzinfo=ZoneInfo("America/Lima"),
    )
    assert isinstance(earthquake.occurred_at.tzinfo, ZoneInfo)
    assert earthquake.occurred_at.tzinfo.key == "America/Lima"
    assert earthquake.occurred_at.utcoffset() == timedelta(hours=-5)
    assert earthquake.occurred_at.astimezone(timezone.utc) == datetime(
        2026, 2, 26, 23, 48, 33, tzinfo=timezone.utc
    )
    assert earthquake.magnitud == recent_earthquake.magnitud
    assert earthquake.profundidad == recent_earthquake.profundidad
    assert earthquake.latitud == recent_earthquake.latitud
    assert earthquake.longitud == recent_earthquake.longitud
    assert earthquake.referencia == recent_earthquake.referencia
    assert earthquake.intensidad == recent_earthquake.intensidad
    assert earthquake.tipo_evento == recent_earthquake.tipomagnitud
    assert earthquake.mapa_sismico_url == recent_earthquake.mapa
    assert earthquake.report_pdf_url == recent_earthquake.informe
    assert (
        not earthquake.is_simulacro
    )  # No hay información sobre simulacros en los sismos recientes


def load_tests(loader, tests, pattern):
    """Permite ejecutar la prueba existente con unittest sin dependencias adicionales."""
    return unittest.TestSuite([unittest.FunctionTestCase(test_recent_to_earthquake)])


if __name__ == "__main__":
    unittest.main()
