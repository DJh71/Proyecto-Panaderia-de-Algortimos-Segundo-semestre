"""Excepciones personalizadas del sistema."""


class InventarioError(Exception):
    """Excepción base de todo el sistema de inventario."""


class CodigoInvalidoError(InventarioError):
    """El código no cumple el formato de 3 letras y 3 dígitos."""


class DatosInvalidosError(InventarioError):
    """Un dato (precio, stock, cantidad, nombre...) no es válido."""


class ProductoNoEncontradoError(InventarioError):
    """No existe un producto con el código indicado."""


class ProductoDuplicadoError(InventarioError):
    """Ya existe un producto con el mismo código."""


class StockInsuficienteError(InventarioError):
    """La cantidad solicitada supera el stock disponible."""


class ArchivoError(InventarioError):
    """Fallo al leer o escribir un archivo de datos."""
