"""Regla de negocio: cálculo del IVA (polimorfismo con herencia)."""
from abc import ABC, abstractmethod

from .excepciones import DatosInvalidosError


class CalculadoraImpuesto(ABC):
    """Clase base abstracta: separa un precio final en subtotal e IVA."""

    def __init__(self, etiqueta):
        """Guarda la etiqueta que se muestra al usuario (ej. '12%')."""
        self._etiqueta = etiqueta

    @property
    def etiqueta(self):
        """Texto descriptivo del impuesto."""
        return self._etiqueta

    @abstractmethod
    def desglosar(self, total):
        """Devuelve (subtotal, iva) a partir de un total con impuesto incluido."""

    @abstractmethod
    def paga_iva(self):
        """Devuelve True si el producto paga IVA."""

    @staticmethod
    def desde_bandera(paga_iva):
        """Crea ConIVA o SinIVA según la bandera leída del CSV o del menú."""
        return ConIVA() if paga_iva else SinIVA()


class ConIVA(CalculadoraImpuesto):
    """Producto gravado: el precio ya incluye el IVA."""

    TASA_DEFAULT = 0.12

    def __init__(self, tasa=TASA_DEFAULT):
        """Crea la calculadora con la tasa indicada (entre 0 y 1).

        Raises:
            DatosInvalidosError: si la tasa está fuera de rango.
        """
        if not 0 <= tasa < 1:
            raise DatosInvalidosError("La tasa de IVA debe estar entre 0 y 1.")
        super().__init__(f"{round(tasa * 100, 2):g}%")
        self._tasa = tasa

    def desglosar(self, total):
        """subtotal = total / (1 + tasa); iva = total - subtotal."""
        subtotal = round(total / (1 + self._tasa), 2)
        return subtotal, round(total - subtotal, 2)

    def paga_iva(self):
        """Siempre True."""
        return True


class SinIVA(CalculadoraImpuesto):
    """Producto exento: todo el total es subtotal."""

    def __init__(self):
        """Crea la calculadora de productos exentos."""
        super().__init__("Exento")

    def desglosar(self, total):
        """Devuelve (total, 0.0)."""
        return round(total, 2), 0.0

    def paga_iva(self):
        """Siempre False."""
        return False
