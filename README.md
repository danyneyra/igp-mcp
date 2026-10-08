# IGP MCP

IGP MCP permite que un asistente consulte información sobre sismos en Perú a través de la API del Instituto Geofísico del Perú (IGP). Puedes pedirle el último sismo, consultar eventos recientes o buscar por fecha, magnitud y ubicación.

Está construido con Python y FastMCP y acompaña un video tutorial. Las fechas de los sismos se entregan en la zona horaria `America/Lima`.

## Requisitos

- Python 3.13.
- Git para clonar el repositorio.
- Conexión a internet.
- Codex u otro cliente compatible con MCP.

Las consultas no requieren una clave de API. Los comandos siguientes están preparados para Windows con PowerShell.

## Instalación

### 1. Clonar el repositorio

Clona el repositorio y entra en su carpeta:

```powershell
git clone https://github.com/danyneyra/igp-mcp igp-mcp
cd igp-mcp
```

### 2. Crear el entorno virtual

El entorno virtual mantiene las dependencias del proyecto en la carpeta `.venv`:

```powershell
py -m venv .venv
```

### 3. Instalar las dependencias

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` fija las versiones de las dependencias para Windows y Python 3.13. Incluye `tzdata`, necesario para cargar `America/Lima` en Windows. `requirements.in` enumera las dependencias directas.

Puedes comprobar que las dependencias instaladas son compatibles entre sí:

```powershell
.\.venv\Scripts\python.exe -m pip check
```

Los comandos siguientes usan los ejecutables de `.venv`, por lo que no necesitas activar el entorno. Ejecútalos desde la raíz del proyecto.

## Ejecución

### HTTP

Es la modalidad utilizada en el video para conectar con Codex:

```powershell
.\.venv\Scripts\fastmcp.exe run src/server.py:mcp --transport http
```

Para desarrollar, agrega `--reload`: el servidor se reinicia al guardar cambios.

```powershell
.\.venv\Scripts\fastmcp.exe run src/server.py:mcp --transport http --reload
```

Si ya tienes el entorno virtual activado, puedes usar el mismo comando del video:

```powershell
fastmcp run src/server.py:mcp --transport http --reload
```

El endpoint predeterminado es `http://localhost:8000/mcp`. Mantén la terminal abierta mientras usas el MCP; para detenerlo, presiona `Ctrl+C`.

### STDIO

Al ejecutar el script directamente, FastMCP utiliza STDIO:

```powershell
.\.venv\Scripts\python.exe src\server.py
```

En esta modalidad, el cliente se comunica con el servidor mediante la entrada y salida del proceso. Cuando lo configuras en un cliente MCP, el cliente lo inicia automáticamente: no necesitas arrancarlo en otra terminal.

## Conexión con Codex

Agrega **una de las dos configuraciones** siguientes a `~/.codex/config.toml`. En Windows, el archivo está en `%USERPROFILE%\.codex\config.toml`.

### Por HTTP

Primero inicia el servidor con el comando HTTP de la sección anterior. Luego configura:

```toml
[mcp_servers.igp]
url = "http://localhost:8000/mcp"
```

### Por STDIO

Reemplaza `D:/igp-mcp` por la ruta absoluta de tu proyecto:

```toml
[mcp_servers.igp]
command = "D:/igp-mcp/.venv/Scripts/python.exe"
args = ["D:/igp-mcp/src/server.py"]
```

Codex iniciará el servidor cuando establezca la conexión. Si ya tienes una entrada `igp`, actualízala sin duplicarla. Después de guardar la configuración, recárgala o reinicia Codex y comprueba que aparecen las herramientas.

Consulta la [documentación oficial de MCP en Codex](https://developers.openai.com/codex/mcp) para más opciones.

## Conexión con otros clientes por STDIO

Para clientes que usan configuración JSON con `mcpServers`:

```json
{
  "mcpServers": {
    "igp": {
      "command": "D:/igp-mcp/.venv/Scripts/python.exe",
      "args": ["D:/igp-mcp/src/server.py"]
    }
  }
}
```

Reemplaza las rutas por las de tu proyecto. Si ya hay otros servidores configurados, agrega la entrada `igp` dentro de `mcpServers`. La ubicación del archivo depende del cliente; después de guardarlo, recarga su configuración o reinícialo.

## Herramientas

| Herramienta | Qué permite hacer | Valores predeterminados |
| --- | --- | --- |
| `get_last_earthquake` | Consultar el último sismo reportado. | Sin parámetros. |
| `get_recent_earthquakes` | Obtener sismos de un año, del más reciente al más antiguo. | `year=2026`, `limit=5`. |
| `search_earthquakes` | Buscar sismos combinando filtros. | `year=2026`, `limit=20`. |

### Filtros de búsqueda

| Parámetro | Descripción |
| --- | --- |
| `year` | Año a consultar, desde 2020 hasta el año vigente al iniciar el servidor. |
| `start_date`, `end_date` | Rango de fechas locales en formato `YYYY-MM-DD`, incluyendo ambos extremos. |
| `min_magnitude`, `max_magnitude` | Rango de magnitud, entre 0 y 10. |
| `min_depth`, `max_depth` | Rango de profundidad, entre 0 y 100 km. |
| `min_latitude`, `max_latitude` | Rango de latitud, entre -90 y 90. |
| `min_longitude`, `max_longitude` | Rango de longitud, entre -180 y 180. |
| `reference` | Texto para buscar en la descripción de la ubicación, ignorando mayúsculas y acentos. |
| `limit` | Cantidad máxima de resultados, entre 1 y 200. También se aplica a recientes. |

Todos los filtros son opcionales. Los mínimos no pueden superar los máximos; para cada coordenada, debes enviar ambos extremos del rango. La búsqueda valida los filtros antes de consultar la API.

Las fechas se devuelven con su zona horaria, por ejemplo: `2026-02-26T18:48:33-05:00`.

El servidor también incluye los recursos `igp://about` e `igp://search-guide`, y los prompts `analyze_region` y `find_significant_earthquakes`.

## Ejemplos

Una vez conectado, puedes pedir al asistente:

- «Consulta el último sismo reportado en Perú».
- «Muéstrame los cinco sismos más recientes de 2026».
- «Busca sismos de 2026 con magnitud mínima de 4.5 y referencia Arequipa».
- «Busca sismos de 2026 entre el 1 y el 28 de febrero».

## Estructura del proyecto

```text
src/
  client.py       # Consultas a la API del IGP
  models.py       # Modelos, validación y conversión de datos
  services.py     # Filtros y ordenamiento
  server.py       # Herramientas, recursos y prompts MCP
test/
  fetch_recent.py
  test_recent_to_earthquake.py
requirements.in   # Dependencias directas
requirements.txt  # Versiones fijas, incluidas las transitivas
README.md
```

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s test -v
```

La prueba verifica la conversión de un sismo, su hora local en `America/Lima` y su equivalencia UTC. Usa datos de ejemplo y no necesita internet. `fetch_recent.py` es un script de consulta manual, fuera de la prueba automatizada.

## Diferencias con el video

Se conserva la estructura del tutorial con estas mejoras:

- Fechas normalizadas a `America/Lima`.
- Validación de filtros antes de consultar la API.
- `limit` restringido a valores entre 1 y 200 en recientes.
- Prueba de conversión corregida y ejecutable con `unittest`.
- README y archivos de dependencias.

## Limitaciones

- El año predeterminado está fijado en 2026. Indica `year` para consultar otro año.
- Cada búsqueda consulta un único año, aunque el rango de fechas abarque varios.
- La búsqueda por referencia es textual; no delimita regiones geográficas con exactitud.
- Las listas pueden estar recortadas por `limit` y no incluyen el total de coincidencias. Los prompts no calculan estadísticas por sí mismos.
- La disponibilidad depende de la API del IGP. Una consulta anual que recibe HTTP 404 devuelve una lista vacía.
- El listado de dependencias está orientado a Windows y Python 3.13; la instalación limpia aún no se ha verificado. Para otras plataformas, instala `requirements.in`, que permite resolver las dependencias transitivas correspondientes.
