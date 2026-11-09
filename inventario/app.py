"""Interfaz de consola y coordinación del sistema."""
from datetime import datetime
from pathlib import Path

from .excepciones import ArchivoError, InventarioError
from .modelos import Producto
from .persistencia import Bitacora, RepositorioCSV
from .reglas import CalculadoraImpuesto
from .reportes import ReporteInventario, ReporteVentas


class Consola:
    """Entrada y salida de datos por consola, con validación de lo escrito."""

    def pedir_entero(self, mensaje, minimo=0):
        """Pide un entero >= minimo hasta que sea válido."""
        while True:
            try:
                valor = int(input(mensaje).strip())
            except ValueError:
                print("  Entrada inválida: escribe un número entero.")
                continue
            if valor < minimo:
                print(f"  El valor debe ser al menos {minimo}.")
                continue
            return valor

    def pedir_decimal(self, mensaje):
        """Pide un número decimal mayor que 0."""
        while True:
            try:
                valor = float(input(mensaje).strip().replace(",", "."))
            except ValueError:
                print("  Entrada inválida: escribe un número (ej. 12.50).")
                continue
            if valor <= 0:
                print("  El valor debe ser mayor que 0.")
                continue
            return valor

    def pedir_si_no(self, mensaje):
        """Pide una confirmación s/n y devuelve True o False."""
        while True:
            respuesta = input(f"{mensaje} (s/n): ").strip().lower()
            if respuesta in ("s", "si", "sí"):
                return True
            if respuesta in ("n", "no"):
                return False
            print("  Responde con 's' o 'n'.")

    def pedir_texto(self, mensaje):
        """Pide un texto no vacío."""
        while True:
            texto = " ".join(input(mensaje).split())
            if texto:
                return texto
            print("  Este campo no puede estar vacío.")


class SistemaInventario:
    """Coordina el menú, el inventario, las ventas, el repositorio y la bitácora."""

    NOMBRE_NEGOCIO = "Panadería Las Migajas"
    SIMBOLO_MONEDA = "Q"
    ANCHO_MENU = 44
    OPCIONES = [
        ("1", "Agregar producto"), ("2", "Buscar producto"),
        ("3", "Registrar venta"), ("4", "Mostrar inventario"),
        ("5", "Reporte de ventas del día"), ("6", "Eliminar producto"),
        ("7", "Agregar stock"), ("8", "Guardar y salir"),
    ]

    def __init__(self, ruta_inventario):
        """Prepara los objetos colaboradores.

        Args:
            ruta_inventario: ruta del CSV de productos (relativa a la raíz del
                proyecto). ventas.csv y bitacora.log se guardan en la misma carpeta.
        """
        ruta = Path(ruta_inventario)
        if not ruta.is_absolute():
            ruta = Path(__file__).resolve().parent.parent / ruta
        self._bitacora = Bitacora(ruta.parent / "bitacora.log")
        self._repositorio = RepositorioCSV(
            ruta, ruta.parent / "ventas.csv", self._bitacora
        )
        self._consola = Consola()
        self._inventario = None
        self._ventas = None
        self._acciones = {
            "1": self._accion_agregar, "2": self._accion_buscar,
            "3": self._accion_venta, "4": self._accion_mostrar,
            "5": self._accion_reporte, "6": self._accion_eliminar,
            "7": self._accion_stock,
        }

    # ---- ciclo principal -------------------------------------------------
    def ejecutar(self):
        """Carga los datos, ejecuta el menú y guarda todo al salir."""
        try:
            self._inventario = self._repositorio.cargar_inventario()
            self._ventas = self._repositorio.cargar_ventas()
        except ArchivoError as error:
            print(f"Error: {error}")
            return
        for aviso in self._repositorio.advertencias:
            print(f"Aviso: {aviso}")
        self._bitacora.registrar(
            f"INICIO de sesión: {len(self._inventario)} productos "
            f"y {len(self._ventas)} ventas cargados"
        )

        try:
            while True:
                self._mostrar_menu()
                opcion = input("Elige una opción: ").strip()
                if opcion == "8":
                    break
                accion = self._acciones.get(opcion)
                if accion is None:
                    print("Opción inválida. Elige un número del 1 al 8.")
                    continue
                try:
                    accion()
                except InventarioError as error:
                    print(f"No se pudo completar la operación: {error}")
                    self._bitacora.registrar(f"ERROR controlado: {error}")
        except (KeyboardInterrupt, EOFError):
            print("\nSesión interrumpida.")
        finally:
            self._guardar_todo()
            self._bitacora.registrar("FIN de sesión: cambios guardados")
            print(f"\nCambios guardados. ¡Hasta pronto, {self.NOMBRE_NEGOCIO}!")

    def _mostrar_menu(self):
        """Dibuja el menú principal."""
        ancho = self.ANCHO_MENU
        borde = "═" * ancho
        print(f"\n╔{borde}╗")
        print(f"║{self.NOMBRE_NEGOCIO.upper():^{ancho}}║")
        print(f"║{'Sistema de Inventario y Ventas':^{ancho}}║")
        print(f"╠{borde}╣")
        for numero, texto in self.OPCIONES:
            print(f"║  {numero}. {texto:<{ancho - 5}}║")
        print(f"╚{borde}╝")

    def _guardar_todo(self):
        """Guarda inventario y ventas; avisa si falla sin cortar el programa."""
        try:
            self._repositorio.guardar_inventario(self._inventario)
            self._repositorio.guardar_ventas(self._ventas)
        except ArchivoError as error:
            print(f"Error: {error}")

    # ---- acciones del menú ----------------------------------------------
    def _accion_agregar(self):
        print("\n--- Agregar producto ---")
        while True:
            codigo = Producto.normalizar_codigo(input(
                "Código (3 letras + 3 dígitos, ej. PAN001; Enter para cancelar): "))
            if not codigo:
                print("Operación cancelada.")
                return
            if not Producto.validar_codigo(codigo):
                print("  Código inválido: usa 3 letras y 3 dígitos (ej. PAN001).")
            elif codigo in self._inventario:
                print(f"  El código {codigo} ya existe.")
            else:
                break

        nombre = self._consola.pedir_texto("Nombre del producto: ")
        categorias = sorted(self._inventario.categorias())
        if categorias:
            print(f"Categorías existentes: {', '.join(categorias)}")
        categoria = self._consola.pedir_texto("Categoría: ")
        precio = self._consola.pedir_decimal(
            f"Precio con IVA incluido ({self.SIMBOLO_MONEDA}): ")
        stock = self._consola.pedir_entero("Stock inicial: ")
        paga_iva = self._consola.pedir_si_no("¿Este producto paga IVA?")

        producto = Producto(codigo, nombre, categoria, precio, stock,
                            CalculadoraImpuesto.desde_bandera(paga_iva))
        self._inventario.agregar(producto)
        self._guardar_todo()
        self._bitacora.registrar(
            f"ALTA producto {producto.codigo} '{producto.nombre}' "
            f"({producto.categoria}) precio {producto.precio:.2f} stock {producto.stock}"
        )
        print(f"Producto {producto.codigo} agregado correctamente.")

    def _accion_buscar(self):
        print("\n--- Buscar producto ---")
        print("1. Por código")
        print("2. Por nombre (coincidencia parcial)")
        modo = input("Elige una opción: ").strip()
        if modo == "1":
            resultados = [self._inventario.obtener(input("Código: "))]
        elif modo == "2":
            resultados = self._inventario.buscar_por_nombre(input("Nombre (o parte): "))
        else:
            print("Opción inválida.")
            return
        if resultados:
            print(f"\n{len(resultados)} resultado(s):")
            print(ReporteInventario(resultados, self.SIMBOLO_MONEDA).generar())
        else:
            print("No se encontraron productos.")

    def _accion_venta(self):
        print("\n--- Registrar venta ---")
        producto = self._inventario.obtener(input("Código del producto: "))
        print(f"{producto.nombre} | Q{producto.precio:.2f} | "
              f"stock disponible: {producto.stock}")
        if producto.stock == 0:
            print("No hay stock disponible de este producto.")
            return
        cantidad = self._consola.pedir_entero("Cantidad a vender: ", minimo=1)

        venta = self._inventario.vender(producto.codigo, cantidad)
        self._ventas.registrar(venta)

        m = lambda v: f"{self.SIMBOLO_MONEDA}{v:,.2f}"
        etiqueta = f"IVA ({producto.calculadora.etiqueta})"
        print("\nVenta registrada")
        print(f"  Producto : {venta.producto} ({venta.codigo})")
        print(f"  Cantidad : {venta.cantidad}")
        print(f"  Subtotal : {m(venta.subtotal):>12}")
        print(f"  {etiqueta:<15}: {m(venta.iva):>12}")
        print(f"  TOTAL    : {m(venta.total):>12}")

        self._guardar_todo()
        self._bitacora.registrar(
            f"VENTA {venta.codigo} x{venta.cantidad} subtotal {venta.subtotal:.2f} "
            f"iva {venta.iva:.2f} total {venta.total:.2f}"
        )

    def _accion_mostrar(self):
        print("\n--- Inventario ---")
        print("Ordenar por:  1. Nombre   2. Precio   3. Categoría")
        criterios = {"1": "nombre", "2": "precio", "3": "categoria"}
        criterio = criterios.get(input("Elige una opción: ").strip())
        if criterio is None:
            print("Opción inválida.")
            return
        print(ReporteInventario(self._inventario.ordenar(criterio),
                                self.SIMBOLO_MONEDA).generar())
        print(f"Total de productos: {len(self._inventario)}")
        print("Categorías:", ", ".join(sorted(self._inventario.categorias())))

    def _accion_reporte(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        reporte = ReporteVentas(self._ventas, hoy, self.NOMBRE_NEGOCIO,
                                self.SIMBOLO_MONEDA)
        print()
        print(reporte.generar())
        self._bitacora.registrar(f"REPORTE de ventas del día {hoy} generado")

    def _accion_stock(self):
        print("\n--- Agregar stock ---")
        producto = self._inventario.obtener(input("Código del producto: "))
        print(f"{producto.nombre} | stock actual: {producto.stock}")
        cantidad = self._consola.pedir_entero("Cantidad a agregar: ", minimo=1)
        self._inventario.reabastecer(producto.codigo, cantidad)
        self._guardar_todo()
        self._bitacora.registrar(
            f"STOCK {producto.codigo} +{cantidad} (nuevo stock {producto.stock})")
        print(f"Stock actualizado: {producto.nombre} ahora tiene "
              f"{producto.stock} unidades.")

    def _accion_eliminar(self):
        print("\n--- Eliminar producto ---")
        producto = self._inventario.obtener(input("Código del producto a eliminar: "))
        print(ReporteInventario([producto], self.SIMBOLO_MONEDA).generar())
        if not self._consola.pedir_si_no("¿Seguro que quieres eliminarlo?"):
            print("Operación cancelada.")
            return
        eliminado = self._inventario.eliminar(producto.codigo)
        self._guardar_todo()
        self._bitacora.registrar(f"BAJA producto {eliminado.codigo} '{eliminado.nombre}'")
        print(f"Producto {eliminado.codigo} eliminado.")
