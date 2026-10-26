"""Pruebas de reglas reproducibles para SCRUM-7."""

from geolocalizar_farmacias import (
    asignar_anillo_por_direccion,
    detectar_anillos_en_direccion,
    procesar_registros,
)


def test_anillos_explicitos_reconocidos():
    casos = {
        "Av. Piraí esq. 2do Anillo": 2,
        "Av. Santos Dumont 3er Anillo": 3,
        "7mo Anillo Av. Banzer": 7,
        "Av. Paraguá esquina 4to Anillo": 4,
    }
    for direccion, esperado in casos.items():
        anillo, estado, metodo = asignar_anillo_por_direccion(direccion)
        assert anillo == esperado
        assert estado == "ASIGNADO"
        assert metodo == "DIRECCION_EXPLICITA"


def test_direccion_entre_anillos_es_ambigua():
    anillo, estado, metodo = asignar_anillo_por_direccion(
        "Av. Cristo Redentor entre 2do y 3er Anillo"
    )
    assert anillo is None
    assert estado == "AMBIGUO_EN_BORDE"
    assert metodo == "DIRECCION_AMBIGUA"


def test_direccion_sin_anillo_no_se_infiere():
    anillo, estado, metodo = asignar_anillo_por_direccion("Calle Junín esq. 21 de Mayo")
    assert anillo is None
    assert estado == "SIN_EVIDENCIA"
    assert metodo == "SIN_ASIGNACION"


def test_anillos_detectados_siempre_pertenecen_al_rango_1_a_8():
    direcciones = [
        "Primer Anillo",
        "Segundo Anillo",
        "Tercer Anillo",
        "Cuarto Anillo",
        "Quinto Anillo",
        "Sexto Anillo",
        "Séptimo Anillo",
        "Octavo Anillo",
        "Av. Cristo Redentor entre 2do y 3er Anillo",
    ]
    for direccion in direcciones:
        assert all(1 <= anillo <= 8 for anillo in detectar_anillos_en_direccion(direccion))


def test_conserva_coordenadas_validadas_sin_geocodificar():
    registro = {
        "farmacia": "Farmacias Chávez",
        "id_sucursal": "CH-01",
        "nombre_sucursal": "Sucursal Mutualista",
        "direccion": "3er Anillo Externo, entre C/ Estremadoiro M. Tovar y C/ Combate Riosino",
        "ciudad": "Santa Cruz de la Sierra",
        "latitud": "-17.7627790370079",
        "longitud": "-63.1592192648441",
        "estado_geocodificacion": "VALIDADA",
    }

    procesado = procesar_registros([registro], geocodificar=False)[0]

    assert procesado["latitud"] == "-17.76277904"
    assert procesado["longitud"] == "-63.15921926"
    assert procesado["estado_geocodificacion"] == "VALIDADA"
    assert procesado["anillo_asignado"] == "3"
    assert procesado["estado_anillo"] == "ASIGNADO"
