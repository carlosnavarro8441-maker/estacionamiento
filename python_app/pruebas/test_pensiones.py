
import os
import sys
import unittest

from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modelos.pension import calcular_antiguedad, elegir_descuento, tiene_mas_de
from modelos.pago_pension import calcular_monto


class PruebasPensiones(unittest.TestCase):

    def test_antiguedad_menor_a_dos_anios(self):

        resultado = calcular_antiguedad(
            date(2024, 12, 1),
            date(2026, 11, 30)
        )

        self.assertEqual(resultado, 1)

    def test_antiguedad_exactamente_dos_anios(self):

        resultado = calcular_antiguedad(
            date(2024, 11, 22),
            date(2026, 11, 22)
        )

        self.assertEqual(resultado, 2)

    def test_antiguedad_mayor_a_dos_anios(self):

        resultado = calcular_antiguedad(
            date(2023, 11, 22),
            date(2026, 11, 22)
        )

        self.assertEqual(resultado, 3)

    def test_calculo_sin_descuento(self):

        resultado = calcular_monto(
            "1000.00",
            0
        )

        self.assertEqual(
            resultado,
            Decimal("1000.00")
        )

    def test_calculo_con_descuento(self):

        resultado = calcular_monto(
            "1000.00",
            10
        )

        self.assertEqual(
            resultado,
            Decimal("900.00")
        )

    def test_rechaza_descuento_invalido(self):

        with self.assertRaises(ValueError):

            calcular_monto(
                "1000.00",
                101
            )

    # ---- Descuento: "más de 2 años" (estrictamente más) ----

    def test_dos_anios_exactos_no_tienen_descuento(self):
        self.assertFalse(
            tiene_mas_de(date(2024, 11, 22), 2, date(2026, 11, 22))
        )

    def test_un_dia_despues_de_dos_anios_si_tiene_descuento(self):
        self.assertTrue(
            tiene_mas_de(date(2024, 11, 22), 2, date(2026, 11, 23))
        )

    def test_menos_de_dos_anios_no_tiene_descuento(self):
        self.assertFalse(
            tiene_mas_de(date(2025, 6, 1), 2, date(2026, 11, 22))
        )

    def test_inicio_29_de_febrero(self):
        self.assertFalse(
            tiene_mas_de(date(2024, 2, 29), 2, date(2026, 2, 28))
        )
        self.assertTrue(
            tiene_mas_de(date(2024, 2, 29), 2, date(2026, 3, 1))
        )

    def test_elegir_descuento_aplica_solo_si_corresponde(self):
        descuentos = [
            {"descuento_id": 1, "anios_minimos": 2, "porcentaje": Decimal("10.00")},
        ]

        self.assertIsNone(
            elegir_descuento(descuentos, date(2024, 11, 22), date(2026, 11, 22))
        )

        elegido = elegir_descuento(
            descuentos, date(2023, 1, 1), date(2026, 11, 22)
        )
        self.assertEqual(elegido["porcentaje"], Decimal("10.00"))

    def test_elegir_descuento_toma_el_mayor_nivel(self):
        descuentos = [
            {"descuento_id": 1, "anios_minimos": 2, "porcentaje": Decimal("10.00")},
            {"descuento_id": 2, "anios_minimos": 5, "porcentaje": Decimal("20.00")},
        ]
        elegido = elegir_descuento(
            descuentos, date(2020, 1, 1), date(2026, 11, 22)
        )
        self.assertEqual(elegido["descuento_id"], 2)


if __name__ == "__main__":
    unittest.main()
