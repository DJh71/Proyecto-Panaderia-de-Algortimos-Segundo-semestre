"""Persistencia: archivos CSV y bitácora."""
import csv
from datetime import datetime
from pathlib import Path

from .excepciones import ArchivoError, InventarioError
from .inventario import Inventario, RegistroVentas
from .modelos import Producto, Venta


class Bitacora:
    """Registra operaciones con fecha y hora en modo append."""

    def __init__(self, ruta):
        """Recibe la ruta del archivo de bitácora."""
        self._ruta = Path(ruta)

    def registrar(self, mensaje):
        """Agrega una línea a la bitácora. Devuelve False si no pudo escribir."""
        marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self._ruta.parent.mkdir(parents=True, exist_ok=True)
            with open(self._ruta, "a", encoding="utf-8") as archivo:
                archivo.write(f"[{marca}] {mensaje}\n")
            return True
        except OSError:
            return False


class RepositorioCSV:
    """Lee y escribe inventario y ventas en archivos CSV."""

    CAMPOS_INVENTARIO = ["codigo", "nombre", "categoria", "precio", "stock", "paga_iva"]
    CAMPOS_VENTAS = ["fecha", "codigo", "producto", "cantidad", "subtotal", "iva", "total"]

    def __init__(self, ruta_inventario, ruta_ventas, bitacora):
        """Recibe las rutas de los CSV y la bitácora donde anotar eventos."""
        self._ruta_inventario = Path(ruta_inventario)
        self._ruta_ventas = Path(ruta_ventas)
        self._bitacora = bitacora
        self.advertencias = []

    def _crear_con_encabezados(self, ruta, campos):
        """Crea un CSV nuevo solo con encabezados."""
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with open(ruta, "w", newline="", encoding="utf-8") as archivo:
                csv.writer(archivo).writerow(campos)
        except OSError as error:
            raise ArchivoError(f"No se pudo crear '{ruta.name}': {error}") from error
        self._bitacora.registrar(f"{ruta.name} no existía: se creó uno nuevo con encabezados")

    def _leer_filas(self, ruta, campos, construir, destino):
        """Lee un CSV; omite (con advertencia) las filas dañadas."""
        if not ruta.exists():
            self._crear_con_encabezados(ruta, campos)
            return
        try:
            with open(ruta, newline="", encoding="utf-8-sig") as archivo:
                for numero, fila in enumerate(csv.DictReader(archivo), start=2):
                    try:
                        destino(construir(fila))
                    except InventarioError as error:
                        self.advertencias.append(
                            f"La línea {numero} de {ruta.name} se omitió ({error})"
                        )
        except (OSError, csv.Error, UnicodeDecodeError) as error:
            raise ArchivoError(f"No se pudo leer '{ruta.name}': {error}") from error

    def _escribir_filas(self, ruta, campos, filas):
        """Sobrescribe un CSV con encabezados y filas."""
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with open(ruta, "w", newline="", encoding="utf-8") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(campos)
                escritor.writerows(filas)
        except OSError as error:
            raise ArchivoError(f"No se pudo guardar '{ruta.name}': {error}") from error

    def cargar_inventario(self):
        """Devuelve un Inventario; lo crea vacío si el archivo no existe.

        Raises:
            ArchivoError: si el archivo no se puede leer.
        """
        inventario = Inventario()
        self._leer_filas(self._ruta_inventario, self.CAMPOS_INVENTARIO,
                         Producto.desde_fila_csv, inventario.agregar)
        return inventario

    def guardar_inventario(self, inventario):
        """Guarda el inventario ordenado por código.

        Raises:
            ArchivoError: si no se puede escribir.
        """
        filas = [p.a_fila_csv() for p in sorted(inventario, key=lambda p: p.codigo)]
        self._escribir_filas(self._ruta_inventario, self.CAMPOS_INVENTARIO, filas)

    def cargar_ventas(self):
        """Devuelve un RegistroVentas; lo crea vacío si el archivo no existe.

        Raises:
            ArchivoError: si el archivo no se puede leer.
        """
        registro = RegistroVentas()
        self._leer_filas(self._ruta_ventas, self.CAMPOS_VENTAS,
                         Venta.desde_fila_csv, registro.registrar)
        return registro

    def guardar_ventas(self, registro):
        """Guarda todas las ventas.

        Raises:
            ArchivoError: si no se puede escribir.
        """
        self._escribir_filas(self._ruta_ventas, self.CAMPOS_VENTAS,
                             [v.a_fila_csv() for v in registro])
