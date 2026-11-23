import os
import sys
import unittest
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controladores.calculo_cobro import calcular_importe, horas_a_cobrar

# Tarifas tal como las pide el proyecto (mismas filas que la tabla `tarifas`)
PASO = [
    {"tarifa_id": 1, "hora_desde": 1, "hora_hasta": 5, "precio": Decimal("30.00")},
    {"tarifa_id": 2, "hora_desde": 6, "hora_hasta": None, "precio": Decimal("25.00")},
]
FRECUENTE = [
    {"tarifa_id": 3, "hora_desde": 1, "hora_hasta": 5, "precio": Decimal("26.00")},
    {"tarifa_id": 4, "hora_desde": 6, "hora_hasta": None, "precio": Decimal("22.00")},
]


class PruebasCobros(unittest.TestCase):

    def test_paso_una_hora(self):
        total, desglose = calcular_importe(1, PASO)
        self.assertEqual(total, Decimal("30.00"))
        self.assertEqual(len(desglose), 1)

    def test_paso_cinco_horas(self):
        self.assertEqual(calcular_importe(5, PASO)[0], Decimal("150.00"))

    def test_paso_seis_horas(self):
        # 5 x 30 + 1 x 25
        total, desglose = calcular_importe(6, PASO)
        self.assertEqual(total, Decimal("175.00"))
        self.assertEqual([d["horas"] for d in desglose], [5, 1])

    def test_paso_siete_horas(self):
        self.assertEqual(calcular_importe(7, PASO)[0], Decimal("200.00"))

    def test_frecuente_una_hora(self):
        self.assertEqual(calcular_importe(1, FRECUENTE)[0], Decimal("26.00"))

    def test_frecuente_cinco_horas(self):
        self.assertEqual(calcular_importe(5, FRECUENTE)[0], Decimal("130.00"))

    def test_frecuente_seis_horas(self):
        # 5 x 26 + 1 x 22
        self.assertEqual(calcular_importe(6, FRECUENTE)[0], Decimal("152.00"))

    def test_frecuente_siete_horas(self):
        self.assertEqual(calcular_importe(7, FRECUENTE)[0], Decimal("174.00"))

    def test_tarifas_incompletas_dan_error(self):
        solo_primer_tramo = [PASO[0]]
        with self.assertRaises(ValueError):
            calcular_importe(7, solo_primer_tramo)

    def test_horas_invalidas(self):
        with self.assertRaises(ValueError):
            calcular_importe(0, PASO)

    def test_fraccion_de_hora_cuenta_completa(self):
        entrada = datetime(2026, 11, 22, 10, 0, 0)
        self.assertEqual(horas_a_cobrar(entrada, datetime(2026, 11, 22, 10, 5, 0)), 1)
        self.assertEqual(horas_a_cobrar(entrada, datetime(2026, 11, 22, 11, 0, 0)), 1)
        self.assertEqual(horas_a_cobrar(entrada, datetime(2026, 11, 22, 11, 1, 0)), 2)
        self.assertEqual(horas_a_cobrar(entrada, datetime(2026, 11, 22, 15, 30, 0)), 6)


if __name__ == "__main__":
    unittest.main()
