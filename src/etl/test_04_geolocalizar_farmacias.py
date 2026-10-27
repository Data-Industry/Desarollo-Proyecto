"""Pruebas de reglas reproducibles para US-03 / SCRUM-7 (Geolocalización)."""

from pathlib import Path
import sys
import unittest

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from geolocalizar_farmacias import (
    asignar_anillo_por_direccion,
    detectar_anillos_en_direccion,
    procesar_registros,
)


class TestGeolocalizarFarmacias(unittest.TestCase):
    """Pruebas unitarias de asignación espacial por anillos."""

    def test_anillos_explicitos_reconocidos(self):
        casos = {
            "Av. Piraí esq. 2do Anillo": 2,
            "Av. Santos Dumont 3er Anillo": 3,
            "7mo Anillo Av. Banzer": 7,
            "Av. Paraguá esquina 4to Anillo": 4,
        }
        for direccion, esperado in casos.items():
            anillo, estado, metodo = asignar_anillo_por_direccion(direccion)
            self.assertEqual(anillo, esperado)
            self.assertEqual(estado, "ASIGNADO")
            self.assertEqual(metodo, "DIRECCION_EXPLICITA")

    def test_direccion_entre_anillos_es_ambigua(self):
        anillo, estado, metodo = asignar_anillo_por_direccion(
            "Av. Cristo Redentor entre 2do y 3er Anillo"
        )
        self.assertIsNone(anillo)
        self.assertEqual(estado, "AMBIGUO_EN_BORDE")
        self.assertEqual(metodo, "DIRECCION_AMBIGUA")

    def test_direccion_sin_anillo_no_se_infiere(self):
        anillo, estado, metodo = asignar_anillo_por_direccion("Calle Junín esq. 21 de Mayo")
        self.assertIsNone(anillo)
        self.assertEqual(estado, "SIN_EVIDENCIA")
        self.assertEqual(metodo, "SIN_ASIGNACION")

    def test_anillos_detectados_siempre_pertenecen_al_rango_1_a_8(self):
        direcciones = [
            "Primer Anillo", "Segundo Anillo", "Tercer Anillo", "Cuarto Anillo",
            "Quinto Anillo", "Sexto Anillo", "Séptimo Anillo", "Octavo Anillo",
            "Av. Cristo Redentor entre 2do y 3er Anillo",
        ]
        for direccion in direcciones:
            self.assertTrue(all(1 <= a <= 8 for a in detectar_anillos_en_direccion(direccion)))

    def test_conserva_coordenadas_validadas_sin_geocodificar(self):
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
        self.assertEqual(procesado["latitud"], "-17.76277904")
        self.assertEqual(procesado["longitud"], "-63.15921926")
        self.assertEqual(procesado["estado_geocodificacion"], "VALIDADA")
        self.assertEqual(procesado["anillo_asignado"], "3")
        self.assertEqual(procesado["estado_anillo"], "ASIGNADO")


if __name__ == "__main__":
    unittest.main()
