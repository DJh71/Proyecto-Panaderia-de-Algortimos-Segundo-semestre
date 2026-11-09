"""Entidades del dominio: Producto y Venta."""
import re
from dataclasses import dataclass
from datetime import datetime

from .excepciones import (
    CodigoInvalidoError,
    DatosInvalidosError,
    StockInsuficienteError,
)
from .reglas import CalculadoraImpuesto


class Producto:
    """Producto de la panadería con atributos encapsulados y validados."""

    PATRON_CODIGO = re.compile(r"[A-Z]{3}[0-9]{3}")

    def __init__(self, codigo, nombre, categoria, precio, stock, calculadora):
        """Crea un producto validando cada dato.

        Args:
            codigo: 3 letras + 3 dígitos (ej. PAN001).
            nombre, categoria: texto no vacío.
            precio: precio unitario con IVA incluido (> 0).
            stock: unidades disponibles (entero >= 0).
            calculadora: objeto CalculadoraImpuesto (ConIVA o SinIVA).

        Raises:
            CodigoInvalidoError, DatosInvalidosError: si algún dato es inválido.
        """
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.stock = stock
        self.calculadora = calculadora

    # ---- utilidades de clase -------------------------------------------
    @staticmethod
    def normalizar_codigo(codigo):
        """Quita espacios y pasa a mayúsculas."""
        return "".join(str(codigo).split()).upper()

    @staticmethod
    def normalizar_texto(texto):
        """Colapsa espacios y pone la primera letra en mayúscula sin tocar el resto."""
        limpio = " ".join(str(texto).split())
        return limpio[:1].upper() + limpio[1:]

    @classmethod
    def validar_codigo(cls, codigo):
        """Devuelve True si el código tiene el formato correcto."""
        return bool(cls.PATRON_CODIGO.fullmatch(cls.normalizar_codigo(codigo)))

    @classmethod
    def desde_fila_csv(cls, fila):
        """Construye un Producto desde un diccionario leído del CSV.

        Raises:
            DatosInvalidosError: si faltan columnas o hay valores no numéricos.
        """
        try:
            return cls(
                fila["codigo"], fila["nombre"], fila["categoria"],
                float(fila["precio"]), int(fila["stock"]),
                CalculadoraImpuesto.desde_bandera(
                    fila["paga_iva"].strip().upper() in ("SI", "SÍ")
                ),
            )
        except (KeyError, ValueError, TypeError, AttributeError) as error:
            raise DatosInvalidosError(f"Fila de producto inválida: {error}") from error

    def a_fila_csv(self):
        """Devuelve el producto como lista lista para escribir en el CSV."""
        return [self.__codigo, self.__nombre, self.__categoria,
                f"{self.__precio:.2f}", self.__stock,
                "SI" if self.__calculadora.paga_iva() else "NO"]

    # ---- propiedades con validación ------------------------------------
    @property
    def codigo(self):
        """Código único del producto."""
        return self.__codigo

    @codigo.setter
    def codigo(self, valor):
        valor = self.normalizar_codigo(valor)
        if not self.PATRON_CODIGO.fullmatch(valor):
            raise CodigoInvalidoError(
                "Código inválido: debe tener 3 letras y 3 dígitos (ej. PAN001)."
            )
        self.__codigo = valor

    @property
    def nombre(self):
        """Nombre del producto."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = self.normalizar_texto(valor)
        if not valor:
            raise DatosInvalidosError("El nombre no puede estar vacío.")
        self.__nombre = valor

    @property
    def categoria(self):
        """Categoría del producto."""
        return self.__categoria

    @categoria.setter
    def categoria(self, valor):
        valor = self.normalizar_texto(valor)
        if not valor:
            raise DatosInvalidosError("La categoría no puede estar vacía.")
        self.__categoria = valor

    @property
    def precio(self):
        """Precio unitario con IVA incluido."""
        return self.__precio

    @precio.setter
    def precio(self, valor):
        try:
            valor = round(float(valor), 2)
        except (TypeError, ValueError) as error:
            raise DatosInvalidosError("El precio debe ser numérico.") from error
        if valor <= 0:
            raise DatosInvalidosError("El precio debe ser mayor que 0.")
        self.__precio = valor

    @property
    def stock(self):
        """Unidades disponibles."""
        return self.__stock

    @stock.setter
    def stock(self, valor):
        if not isinstance(valor, int) or isinstance(valor, bool):
            raise DatosInvalidosError("El stock debe ser un número entero.")
        if valor < 0:
            raise DatosInvalidosError("El stock no puede ser negativo.")
        self.__stock = valor

    @property
    def calculadora(self):
        """Calculadora de impuesto asociada (composición)."""
        return self.__calculadora

    @calculadora.setter
    def calculadora(self, valor):
        if not isinstance(valor, CalculadoraImpuesto):
            raise DatosInvalidosError("Se requiere una calculadora de impuesto.")
        self.__calculadora = valor

    # ---- comportamiento -------------------------------------------------
    @staticmethod
    def _validar_cantidad(cantidad):
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise DatosInvalidosError("La cantidad debe ser un entero mayor que 0.")

    def descontar_stock(self, cantidad):
        """Resta unidades al stock.

        Raises:
            DatosInvalidosError: si la cantidad no es un entero positivo.
            StockInsuficienteError: si no alcanza el stock.
        """
        self._validar_cantidad(cantidad)
        if cantidad > self.__stock:
            raise StockInsuficienteError(
                f"Stock insuficiente de '{self.__nombre}': "
                f"disponible {self.__stock}, solicitado {cantidad}."
            )
        self.__stock -= cantidad

    def agregar_stock(self, cantidad):
        """Suma unidades al stock.

        Raises:
            DatosInvalidosError: si la cantidad no es un entero positivo.
        """
        self._validar_cantidad(cantidad)
        self.__stock += cantidad

    def desglosar(self, cantidad):
        """Devuelve (subtotal, iva, total) de vender 'cantidad' unidades.

        El desglose lo hace la calculadora (polimorfismo: ConIVA o SinIVA).
        """
        self._validar_cantidad(cantidad)
        total = round(self.__precio * cantidad, 2)
        subtotal, iva = self.__calculadora.desglosar(total)
        return subtotal, iva, total

    # ---- métodos especiales ---------------------------------------------
    def __str__(self):
        return (f"{self.__codigo} - {self.__nombre} ({self.__categoria}) "
                f"Q{self.__precio:.2f} x {self.__stock}")

    def __repr__(self):
        return (f"Producto(codigo={self.__codigo!r}, nombre={self.__nombre!r}, "
                f"precio={self.__precio}, stock={self.__stock})")

    def __eq__(self, otro):
        if not isinstance(otro, Producto):
            return NotImplemented
        return self.__codigo == otro.codigo

    def __hash__(self):
        return hash(self.__codigo)

    def __lt__(self, otro):
        if not isinstance(otro, Producto):
            return NotImplemented
        return self.__nombre.casefold() < otro.nombre.casefold()


@dataclass(frozen=True)
class Venta:
    """Registro inmutable de una venta."""

    FORMATO_FECHA = "%Y-%m-%d %H:%M"

    fecha: str
    codigo: str
    producto: str
    cantidad: int
    subtotal: float
    iva: float
    total: float

    @classmethod
    def desde_producto(cls, producto, cantidad, fecha=None):
        """Crea la venta de 'cantidad' unidades de un Producto (no toca el stock).

        Raises:
            DatosInvalidosError: si la cantidad es inválida.
        """
        subtotal, iva, total = producto.desglosar(cantidad)
        if fecha is None:
            fecha = datetime.now().strftime(cls.FORMATO_FECHA)
        return cls(fecha, producto.codigo, producto.nombre, cantidad,
                   subtotal, iva, total)

    @classmethod
    def desde_fila_csv(cls, fila):
        """Construye una Venta desde un diccionario del CSV.

        Raises:
            DatosInvalidosError: si la fila está dañada.
        """
        try:
            return cls(fila["fecha"], fila["codigo"], fila["producto"],
                       int(fila["cantidad"]), float(fila["subtotal"]),
                       float(fila["iva"]), float(fila["total"]))
        except (KeyError, ValueError, TypeError) as error:
            raise DatosInvalidosError(f"Fila de venta inválida: {error}") from error

    def a_fila_csv(self):
        """Devuelve la venta como lista lista para el CSV."""
        return [self.fecha, self.codigo, self.producto, self.cantidad,
                f"{self.subtotal:.2f}", f"{self.iva:.2f}", f"{self.total:.2f}"]

    def es_del_dia(self, dia):
        """True si la venta ocurrió en el día 'YYYY-MM-DD'."""
        return self.fecha.startswith(dia)

    def __str__(self):
        return f"{self.fecha} | {self.codigo} x{self.cantidad} | Q{self.total:.2f}"
