"""Colecciones: Inventario (productos) y RegistroVentas (ventas)."""
from .excepciones import (
    DatosInvalidosError,
    ProductoDuplicadoError,
    ProductoNoEncontradoError,
)
from .modelos import Producto, Venta


class Inventario:
    """Colección de productos indexada por código (diccionario de objetos)."""

    CRITERIOS = {
        "nombre": lambda p: p.nombre.casefold(),
        "precio": lambda p: (p.precio, p.nombre.casefold()),
        "categoria": lambda p: (p.categoria.casefold(), p.nombre.casefold()),
    }

    def __init__(self):
        """Crea un inventario vacío."""
        self.__productos = {}

    def agregar(self, producto):
        """Agrega un producto.

        Raises:
            ProductoDuplicadoError: si el código ya existe.
        """
        if producto.codigo in self.__productos:
            raise ProductoDuplicadoError(
                f"Ya existe un producto con el código {producto.codigo}."
            )
        self.__productos[producto.codigo] = producto

    def eliminar(self, codigo):
        """Elimina y devuelve el producto con ese código.

        Raises:
            ProductoNoEncontradoError: si no existe.
        """
        producto = self.obtener(codigo)
        return self.__productos.pop(producto.codigo)

    def obtener(self, codigo):
        """Devuelve el producto con ese código.

        Raises:
            ProductoNoEncontradoError: si no existe.
        """
        codigo = Producto.normalizar_codigo(codigo)
        try:
            return self.__productos[codigo]
        except KeyError:
            raise ProductoNoEncontradoError(
                f"No existe ningún producto con el código {codigo}."
            ) from None

    def buscar_por_nombre(self, texto):
        """Productos cuyo nombre contiene el texto (sin distinguir mayúsculas)."""
        fragmento = " ".join(str(texto).split()).casefold()
        if not fragmento:
            return []
        return sorted(
            (p for p in self if fragmento in p.nombre.casefold()),
            key=self.CRITERIOS["nombre"],
        )

    def ordenar(self, criterio):
        """Lista de productos ordenada por 'nombre', 'precio' o 'categoria'.

        Raises:
            DatosInvalidosError: si el criterio no existe.
        """
        if criterio not in self.CRITERIOS:
            raise DatosInvalidosError(f"Criterio de orden desconocido: {criterio}.")
        return sorted(self, key=self.CRITERIOS[criterio])

    def categorias(self):
        """Set con las categorías existentes, sin duplicados."""
        return {p.categoria for p in self}

    def vender(self, codigo, cantidad, fecha=None):
        """Descuenta stock y devuelve la Venta generada.

        Raises:
            ProductoNoEncontradoError, DatosInvalidosError, StockInsuficienteError
        """
        producto = self.obtener(codigo)
        venta = Venta.desde_producto(producto, cantidad, fecha)
        producto.descontar_stock(cantidad)
        return venta

    def reabastecer(self, codigo, cantidad):
        """Suma stock a un producto existente y lo devuelve."""
        producto = self.obtener(codigo)
        producto.agregar_stock(cantidad)
        return producto

    def __len__(self):
        return len(self.__productos)

    def __contains__(self, codigo):
        return Producto.normalizar_codigo(codigo) in self.__productos

    def __iter__(self):
        return iter(self.__productos.values())

    def __repr__(self):
        return f"Inventario({len(self)} productos)"


class RegistroVentas:
    """Colección de ventas (objetos Venta inmutables)."""

    def __init__(self, ventas=()):
        """Crea el registro con ventas iniciales opcionales."""
        self.__ventas = list(ventas)

    def registrar(self, venta):
        """Agrega una venta al registro."""
        self.__ventas.append(venta)

    def del_dia(self, dia):
        """Ventas realizadas en el día 'YYYY-MM-DD'."""
        return [v for v in self.__ventas if v.es_del_dia(dia)]

    def __len__(self):
        return len(self.__ventas)

    def __iter__(self):
        return iter(self.__ventas)

    def __repr__(self):
        return f"RegistroVentas({len(self)} ventas)"
