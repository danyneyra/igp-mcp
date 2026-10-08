from datetime import date, datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel, ConfigDict, Field, model_validator

CURRENT_YEAR = datetime.now().year
LIMA_TIMEZONE = ZoneInfo("America/Lima")


class LastEarthquake(BaseModel):
    """Modelo de datos para representar la información del último sismo ocurrido en Perú."""

    model_config = ConfigDict(
        extra="ignore",
    )

    id: int
    codigo: str
    numero: int
    fecha_hora: datetime = Field(alias="fecha_hora")
    magnitud: float
    referencia: str
    superficie: str | None
    latitud: float
    longitud: float
    profundidad: float
    intensidades: str
    tipo_evento: str
    created_at: datetime = Field(alias="created_at")
    simulacro: int
    mapa_sismico_url: str
    mapa_acelerometrico_url: str


class RecentEarthquake(BaseModel):
    """Modelo de datos para representar la información de los sismos recientes ocurridos en Perú."""

    model_config = ConfigDict(
        extra="ignore",
    )

    codigo: str
    reporte_acelerometrico_pdf: str | None = None
    idlistasismos: int
    fecha_local: datetime
    hora_local: datetime
    fecha_utc: datetime
    hora_utc: datetime
    latitud: float
    longitud: float
    magnitud: float
    profundidad: float
    referencia: str
    referencia2: str | None = None
    referencia3: str | None = None
    tipomagnitud: str | None = None
    mapa: str | None = None
    informe: str | None = None
    publicado: str | None = None
    numero_reporte: int | None = None
    id_pdf_tematico: int | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    intensidad: str | None = None


class Earthquake(BaseModel):
    """Modelo de datos para representar la información de un sismo."""

    model_config = ConfigDict(
        extra="ignore",
    )

    id: int | None = None
    codigo: str
    occurred_at: datetime
    magnitud: float
    profundidad: float
    latitud: float
    longitud: float
    referencia: str
    intensidad: str | None = None
    tipo_evento: str | None = None
    mapa_sismico_url: str | None = None
    mapa_acelerometrico_url: str | None = None
    report_pdf_url: str | None = None
    is_simulacro: bool | None = None
    source: str  # Fuente haciendo referencia al endpoint: "ultimo_sismo" o "sismos_recientes"


class EarthquakeSearchFilters(BaseModel):
    """Modelo de datos para representar los filtros de búsqueda de sismos."""

    model_config = ConfigDict(
        extra="ignore",
    )

    year: int = Field(
        default_factory=lambda: datetime.now().year, ge=2020, le=CURRENT_YEAR
    )
    start_date: date | None = None
    end_date: date | None = None

    min_magnitude: float | None = Field(default=None, ge=0.0, le=10.0)
    max_magnitude: float | None = Field(default=None, ge=0.0, le=10.0)
    min_depth: float | None = Field(default=None, ge=0.0, le=100.0)
    max_depth: float | None = Field(default=None, ge=0.0, le=100.0)
    min_latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    max_latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    min_longitude: float | None = Field(default=None, ge=-180.0, le=180.0)
    max_longitude: float | None = Field(default=None, ge=-180.0, le=180.0)

    reference: str | None = None

    limit: int = Field(default=20, ge=1, le=200)

    @model_validator(mode="after")
    def validate_ranges(self):
        ranges = [
            ("magnitud", self.min_magnitude, self.max_magnitude),
            ("profundidad", self.min_depth, self.max_depth),
            ("latitud", self.min_latitude, self.max_latitude),
            ("longitud", self.min_longitude, self.max_longitude),
        ]

        for name, minimum, maximum in ranges:
            if minimum is not None and maximum is not None and minimum > maximum:
                raise ValueError(
                    f"La mínima de {name} no puede ser mayor que la máxima"
                )

        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError("start_date no puede ser posterior a end_date")

        return self

    @model_validator(mode="after")
    def validate_coordinate_ranges(self):
        latitude_pair = (
            self.min_latitude is not None,
            self.max_latitude is not None,
        )
        longitude_pair = (
            self.min_longitude is not None,
            self.max_longitude is not None,
        )

        if latitude_pair not in [(False, False), (True, True)]:
            raise ValueError("min_latitude y max_latitude deben enviarse juntos")

        if longitude_pair not in [(False, False), (True, True)]:
            raise ValueError("min_longitude y max_longitude deben enviarse juntos")

        if (
            self.min_latitude is not None
            and self.max_latitude is not None
            and self.min_latitude > self.max_latitude
        ):
            raise ValueError("min_latitude no puede ser mayor que max_latitude")

        if (
            self.min_longitude is not None
            and self.max_longitude is not None
            and self.min_longitude > self.max_longitude
        ):
            raise ValueError("min_longitude no puede ser mayor que max_longitude")

        return self


def last_to_earthquake(item: LastEarthquake) -> Earthquake:
    """Convierte un diccionario de datos en un objeto Earthquake."""
    return Earthquake(
        id=item.id,
        codigo=item.codigo,
        occurred_at=(
            item.fecha_hora.replace(tzinfo=LIMA_TIMEZONE)
            if item.fecha_hora.tzinfo is None
            else item.fecha_hora.astimezone(LIMA_TIMEZONE)
        ),
        magnitud=item.magnitud,
        profundidad=item.profundidad,
        latitud=item.latitud,
        longitud=item.longitud,
        referencia=item.referencia,
        intensidad=item.intensidades,
        tipo_evento=item.tipo_evento,
        mapa_sismico_url=item.mapa_sismico_url,
        mapa_acelerometrico_url=item.mapa_acelerometrico_url,
        is_simulacro=item.simulacro == 1,
        source="ultimo_sismo",
    )


def recent_to_earthquake(item: RecentEarthquake) -> Earthquake:
    """Convierte un diccionario de datos en un objeto Earthquake."""
    return Earthquake(
        id=item.idlistasismos,
        codigo=item.codigo,
        occurred_at=datetime.combine(
            # Estos campos representan la fecha y hora local, incluso si incluyen Z.
            item.fecha_local.date(), item.hora_local.time(), tzinfo=LIMA_TIMEZONE
        ),
        magnitud=item.magnitud,
        profundidad=item.profundidad,
        latitud=item.latitud,
        longitud=item.longitud,
        referencia=item.referencia,
        intensidad=item.intensidad,
        tipo_evento=item.tipomagnitud,
        mapa_sismico_url=item.mapa,
        report_pdf_url=item.informe,
        is_simulacro=False,  # No hay información sobre simulacros en los sismos recientes
        source="sismos_recientes",
    )
