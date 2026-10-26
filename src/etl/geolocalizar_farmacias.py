"""Geolocaliza sucursales farmacéuticas sin inferir ubicaciones ni anillos.

SCRUM-7. La asignación actual usa exclusivamente referencias inequívocas a un
anillo presentes en la dirección oficial. La geocodificación con Nominatim es
optativa y sus resultados se guardan como candidatos que requieren validación.
"""

from __future__ import annotations

import argparse
import csv
import logging
import re
import ssl
import unicodedata
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

PROJECT_DIR = Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_DIR / "data" / "raw" / "sucursales_farmacias_scz.csv"
OUTPUT_PATH = PROJECT_DIR / "data" / "processed" / "farmacias_geolocalizadas.csv"
ANILLOS_GEOJSON_PATH = (
    PROJECT_DIR / "data" / "raw" / "cartografia" / "gamsc_anillos_1_8.geojson"
)
NOMINATIM_USER_AGENT = "proyecto-integrador-scrum7-geolocalizacion-academica"

LOGGER = logging.getLogger("geolocalizar_farmacias")

OUTPUT_FIELDS = [
    "farmacia",
    "id_sucursal",
    "nombre_sucursal",
    "direccion",
    "ciudad",
    "latitud",
    "longitud",
    "anillo_asignado",
    "estado_geocodificacion",
    "estado_anillo",
    "metodo_asignacion_anillo",
    "fuente",
    "fuente_geocodificacion",
    "fecha_verificacion",
    "advertencias",
    "consulta_geocodificacion",
    "respuesta_geocodificacion",
    "fecha_geocodificacion",
]

# Cada patrón exige la palabra ``anillo``: un número aislado nunca se interpreta
# como una clasificación territorial.
ANILLO_PATTERNS = {
    1: r"(?:1(?:er|ro|[º°o])|primer(?:o)?)",
    2: r"(?:2(?:do|[º°o])|segundo)",
    3: r"(?:3(?:er|ro|[º°o])|tercer(?:o)?)",
    4: r"(?:4(?:to|[º°o])|cuarto)",
    5: r"(?:5(?:to|[º°o])|quinto)",
    6: r"(?:6(?:to|[º°o])|sexto)",
    7: r"(?:7(?:mo|[º°o])|septimo)",
    8: r"(?:8(?:vo|[º°o])|octavo)",
}


def normalizar_texto(texto: str) -> str:
    """Normaliza mayúsculas y acentos para comparar direcciones sin alterarlas."""
    sin_acentos = "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto or "")
        if unicodedata.category(caracter) != "Mn"
    )
    return re.sub(r"\s+", " ", sin_acentos.casefold()).strip()


def detectar_anillos_en_direccion(direccion: str) -> List[int]:
    """Devuelve los anillos explícitamente mencionados, sin deducción geográfica."""
    texto = normalizar_texto(direccion)
    encontrados = set()
    # Se revisa el tramo previo a cada palabra "anillo" para reconocer tanto
    # "2do Anillo" como "entre 2do y 3er Anillo". El tamaño del contexto evita
    # asociar números remotos de una dirección con una vía de anillo.
    for coincidencia_anillo in re.finditer(r"\banillo\b", texto):
        contexto = texto[max(0, coincidencia_anillo.start() - 60) : coincidencia_anillo.start()]
        for anillo, patron in ANILLO_PATTERNS.items():
            if re.search(rf"\b{patron}\b", contexto):
                encontrados.add(anillo)
    return sorted(encontrados)


def asignar_anillo_por_direccion(direccion: str) -> Tuple[Optional[int], str, str]:
    """Clasifica solo una mención inequívoca; múltiples menciones quedan ambiguas."""
    anillos = detectar_anillos_en_direccion(direccion)
    if len(anillos) == 1:
        return anillos[0], "ASIGNADO", "DIRECCION_EXPLICITA"
    if len(anillos) > 1:
        return None, "AMBIGUO_EN_BORDE", "DIRECCION_AMBIGUA"
    return None, "SIN_EVIDENCIA", "SIN_ASIGNACION"


def asignar_anillo_por_geometria(
    latitud: Optional[float], longitud: Optional[float], geojson_path: Path = ANILLOS_GEOJSON_PATH
) -> Tuple[Optional[int], str, str]:
    """Reserva el contrato para el futuro cruce point-in-polygon oficial.

    No construye ni presupone polígonos. Cuando exista un GeoJSON municipal
    completo, validado y con atributo ``anillo`` de 1 a 8, esta función será el
    único punto a extender con GeoPandas/Shapely para realizar point-in-polygon.
    """
    if latitud is None or longitud is None:
        return None, "SIN_COORDENADAS", "SIN_CARTOGRAFIA_APLICABLE"
    if not geojson_path.exists():
        return None, "SIN_CARTOGRAFIA_OFICIAL", "CARTOGRAFIA_NO_DISPONIBLE"
    return None, "CARTOGRAFIA_PENDIENTE_VALIDACION", "CARTOGRAFIA_NO_IMPLEMENTADA"


def _a_float(valor: str) -> Optional[float]:
    if valor is None or not str(valor).strip():
        return None
    try:
        return float(str(valor).strip())
    except ValueError:
        return None


def validar_coordenadas(latitud: Optional[float], longitud: Optional[float]) -> Tuple[bool, str]:
    """Valida presencia por pares y rangos WGS84, sin validar precisión local."""
    if latitud is None and longitud is None:
        return True, "SIN_COORDENADAS"
    if latitud is None or longitud is None:
        return False, "COORDENADAS_INCOMPLETAS"
    if not -90 <= latitud <= 90:
        return False, "LATITUD_FUERA_DE_RANGO"
    if not -180 <= longitud <= 180:
        return False, "LONGITUD_FUERA_DE_RANGO"
    return True, "COORDENADAS_VALIDAS"


def _agregar_advertencia(advertencias: List[str], mensaje: str) -> None:
    if mensaje and mensaje not in advertencias:
        advertencias.append(mensaje)


def geocodificar_con_nominatim(
    direccion: str, ciudad: str
) -> Dict[str, str]:
    """Obtiene un candidato único de Nominatim, nunca una ubicación validada."""
    try:
        import certifi
        from geopy.extra.rate_limiter import RateLimiter
        from geopy.geocoders import Nominatim
    except ImportError as exc:  # pragma: no cover - cubierto por error de CLI
        raise RuntimeError("Falta geopy. Instale geopy para usar --geocodificar.") from exc

    consulta = f"{direccion}, {ciudad}, Bolivia"
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    geocoder = Nominatim(
        user_agent=NOMINATIM_USER_AGENT, timeout=15, ssl_context=ssl_context
    )
    # La política pública de Nominatim establece un máximo de una solicitud/s.
    fecha = datetime.now(timezone.utc).isoformat()
    geocode = RateLimiter(
        geocoder.geocode,
        min_delay_seconds=1.0,
        max_retries=0,
        swallow_exceptions=False,
    )
    try:
        resultados = geocode(consulta, exactly_one=False, addressdetails=True, limit=5)
    except Exception as exc:
        return {
            "estado": "PENDIENTE",
            "latitud": "",
            "longitud": "",
            "fuente": "Nominatim / OpenStreetMap",
            "consulta": consulta,
            "respuesta": f"Error de servicio: {type(exc).__name__}: {exc}",
            "fecha": fecha,
            "advertencia": "Nominatim no estuvo disponible; no se clasificó como NO_ENCONTRADA",
        }
    if not resultados:
        return {
            "estado": "NO_ENCONTRADA",
            "latitud": "",
            "longitud": "",
            "fuente": "Nominatim / OpenStreetMap",
            "consulta": consulta,
            "respuesta": "Sin resultados",
            "fecha": fecha,
            "advertencia": "Nominatim no devolvió resultados; requiere revisión manual",
        }

    if len(resultados) != 1:
        return {
            "estado": "AMBIGUA",
            "latitud": "",
            "longitud": "",
            "fuente": "Nominatim / OpenStreetMap",
            "consulta": consulta,
            "respuesta": f"{len(resultados)} candidatos: " + " | ".join(r.address for r in resultados),
            "fecha": fecha,
            "advertencia": "Nominatim devolvió múltiples candidatos; no se asignaron coordenadas",
        }

    resultado = resultados[0]
    latitud, longitud = float(resultado.latitude), float(resultado.longitude)
    valida, motivo = validar_coordenadas(latitud, longitud)
    respuesta = resultado.address
    if not valida or "santa cruz" not in normalizar_texto(respuesta):
        return {
            "estado": "AMBIGUA",
            "latitud": "",
            "longitud": "",
            "fuente": "Nominatim / OpenStreetMap",
            "consulta": consulta,
            "respuesta": respuesta,
            "fecha": fecha,
            "advertencia": f"Candidato Nominatim no verificable para Santa Cruz de la Sierra ({motivo})",
        }

    return {
        "estado": "CANDIDATO_VALIDACION",
        "latitud": f"{latitud:.8f}",
        "longitud": f"{longitud:.8f}",
        "fuente": "Nominatim / OpenStreetMap",
        "consulta": consulta,
        "respuesta": respuesta,
        "fecha": fecha,
        "advertencia": "Coordenadas candidatas de Nominatim; requieren validación contra fuente oficial",
    }


def procesar_registros(registros: Iterable[Dict[str, str]], geocodificar: bool = False) -> List[Dict[str, str]]:
    """Valida y transforma el catálogo raw en registros procesados auditables."""
    procesados: List[Dict[str, str]] = []
    ids_vistos = set()
    cartografia_disponible = ANILLOS_GEOJSON_PATH.exists()

    for origen in registros:
        farmacia = (origen.get("farmacia") or "").strip()
        id_sucursal = (origen.get("id_sucursal") or "").strip()
        clave = (farmacia, id_sucursal)
        if not farmacia or not id_sucursal:
            raise ValueError("Cada registro requiere farmacia e id_sucursal.")
        if clave in ids_vistos:
            raise ValueError(f"id_sucursal duplicado para farmacia: {farmacia} / {id_sucursal}")
        ids_vistos.add(clave)

        advertencias = []
        direccion = (origen.get("direccion") or "").strip()
        if not direccion:
            _agregar_advertencia(advertencias, "Dirección faltante; no se puede geocodificar")

        latitud = _a_float(origen.get("latitud", ""))
        longitud = _a_float(origen.get("longitud", ""))
        coordenadas_validas, estado_coordenadas = validar_coordenadas(latitud, longitud)
        if not coordenadas_validas:
            _agregar_advertencia(advertencias, estado_coordenadas)
            latitud = longitud = None

        estado_geo = (origen.get("estado_geocodificacion") or "PENDIENTE").strip() or "PENDIENTE"
        fuente_geo = (origen.get("fuente_geocodificacion") or "").strip()
        consulta_geo = respuesta_geo = fecha_geo = ""

        if latitud is None and longitud is None:
            if geocodificar and direccion:
                candidato = geocodificar_con_nominatim(direccion, origen.get("ciudad", ""))
                estado_geo = candidato["estado"]
                fuente_geo = candidato["fuente"]
                consulta_geo = candidato["consulta"]
                respuesta_geo = candidato["respuesta"]
                fecha_geo = candidato["fecha"]
                _agregar_advertencia(advertencias, candidato["advertencia"])
                latitud = _a_float(candidato["latitud"])
                longitud = _a_float(candidato["longitud"])
            else:
                estado_geo = "PENDIENTE"
                _agregar_advertencia(advertencias, "Sin coordenadas; requiere geocodificación")

        anillo, estado_anillo, metodo_anillo = asignar_anillo_por_direccion(direccion)
        if estado_anillo == "AMBIGUO_EN_BORDE":
            _agregar_advertencia(advertencias, "Múltiples anillos explícitos; no se asignó anillo")
        elif estado_anillo == "SIN_EVIDENCIA":
            _agregar_advertencia(advertencias, "Dirección sin referencia explícita de anillo")

        # La geometría solo podrá complementar direcciones sin evidencia; nunca
        # sobrescribe una referencia explícita ni resuelve una ambigüedad.
        if anillo is None and estado_anillo == "SIN_EVIDENCIA":
            _, estado_geometria, metodo_geometria = asignar_anillo_por_geometria(latitud, longitud)
            if estado_geometria == "SIN_CARTOGRAFIA_OFICIAL":
                _agregar_advertencia(advertencias, "Cartografía oficial completa de anillos 1–8 no disponible")
            elif estado_geometria == "CARTOGRAFIA_PENDIENTE_VALIDACION":
                _agregar_advertencia(advertencias, "Cartografía de anillos requiere validación antes de usarla")
            if metodo_geometria != "SIN_CARTOGRAFIA_APLICABLE":
                metodo_anillo = metodo_geometria

        if not cartografia_disponible:
            _agregar_advertencia(advertencias, "Sin capa GIS oficial completa de anillos 1–8")

        if anillo is not None and not 1 <= anillo <= 8:
            raise ValueError(f"Anillo fuera de rango para {id_sucursal}: {anillo}")
        if estado_anillo == "AMBIGUO_EN_BORDE" and anillo is not None:
            raise ValueError(f"Registro ambiguo con anillo asignado: {id_sucursal}")

        procesados.append(
            {
                "farmacia": farmacia,
                "id_sucursal": id_sucursal,
                "nombre_sucursal": (origen.get("nombre_sucursal") or "").strip(),
                "direccion": direccion,
                "ciudad": (origen.get("ciudad") or "").strip(),
                "latitud": "" if latitud is None else f"{latitud:.8f}",
                "longitud": "" if longitud is None else f"{longitud:.8f}",
                "anillo_asignado": "" if anillo is None else str(anillo),
                "estado_geocodificacion": estado_geo,
                "estado_anillo": estado_anillo,
                "metodo_asignacion_anillo": metodo_anillo,
                "fuente": (origen.get("fuente") or "").strip(),
                "fuente_geocodificacion": fuente_geo,
                "fecha_verificacion": (origen.get("fecha_verificacion") or date.today().isoformat()).strip(),
                "advertencias": "; ".join(advertencias),
                "consulta_geocodificacion": consulta_geo,
                "respuesta_geocodificacion": respuesta_geo,
                "fecha_geocodificacion": fecha_geo,
            }
        )
    return procesados


def leer_catalogo(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))


def escribir_salida(registros: List[Dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(registros)


def resumen(registros: Iterable[Dict[str, str]]) -> Dict[str, Any]:
    registros = list(registros)
    distribucion = Counter(
        int(registro["anillo_asignado"])
        for registro in registros
        if registro["anillo_asignado"]
    )
    return {
        "total_sucursales": len(registros),
        "anillos_asignados": sum(bool(registro["anillo_asignado"]) for registro in registros),
        "ambiguas": sum(registro["estado_anillo"] == "AMBIGUO_EN_BORDE" for registro in registros),
        "pendientes_geocodificacion": sum(
            registro["estado_geocodificacion"] == "PENDIENTE" for registro in registros
        ),
        "distribucion_por_anillo": dict(sorted(distribucion.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--geocodificar",
        action="store_true",
        help="Consulta Nominatim para direcciones sin coordenadas; genera solo candidatos de validación.",
    )
    args = parser.parse_args()

    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"No existe el catálogo requerido: {INPUT_PATH}")

    registros = procesar_registros(leer_catalogo(INPUT_PATH), geocodificar=args.geocodificar)
    escribir_salida(registros, OUTPUT_PATH)
    datos_resumen = resumen(registros)

    print("=== RESUMEN GEOLOCALIZACIÓN DE FARMACIAS ===")
    print(f"Total de sucursales: {datos_resumen['total_sucursales']}")
    print(f"Con anillo asignado: {datos_resumen['anillos_asignados']}")
    print(f"Ambiguas: {datos_resumen['ambiguas']}")
    print(f"Pendientes de geocodificación: {datos_resumen['pendientes_geocodificacion']}")
    print("Distribución por anillo:")
    for anillo, total in datos_resumen["distribucion_por_anillo"].items():
        print(f"  Anillo {anillo}: {total}")
    print(f"Salida: {OUTPUT_PATH}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
