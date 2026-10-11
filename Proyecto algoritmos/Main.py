#Las ventas

from datetime import datetime

import Archivos
import Operaciones as ops

ANCHO_MENU = 44
OPCIONES_MENU = [
    ("1", "Agregar producto"),
    ("2", "Buscar producto"),
    ("3", "Registrar venta"),
    ("4", "Mostrar inventario"),
    ("5", "Reporte de ventas del día"),
    ("6", "Eliminar producto"),
    ("7", "Agregar Stock"),
    ("8", "Guardar y Salir"),
]


# Entrada de datos

def pedir_entero(mensaje, minimo=0):
    """Funcion para los numeros enteros"""
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



def pedir_decimal(mensaje, minimo=0.0):
    """Funcion para los numeros con decimales"""
    while True:
        try:
            valor = float(input(mensaje).strip().replace(",", "."))
        except ValueError:
            print("  Entrada inválida: escribe un número (ej. 12.50).")
            continue
        if valor <= minimo:
            print(f"  El valor debe ser mayor que {minimo}.")
            continue
        return valor


def pedir_si_no(mensaje):
    """selecionnar la confirmacion"""
    while True:
        respuesta = input(f"{mensaje} (s/n): ").strip().lower()
        if respuesta in ("s", "si", "sí"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("  Responde con 's' o 'n'.")

def pedir_texto_no_vacio(mensaje):
    """Obligar al usuario a escribir un comando"""
    while True:
        texto = " ".join(input(mensaje).split())
        if texto:
            return texto
        print("  Este campo no puede estar vacío.")


def mostrar_menu():
    """Muestra el menu de opciones"""
    borde = "═" * ANCHO_MENU
    print(f"\n╔{borde}╗")
    print(f"║{ops.NOMBRE_NEGOCIO.upper():^{ANCHO_MENU}}║")
    print(f"║{'Sistema de Inventario y Ventas':^{ANCHO_MENU}}║")
    print(f"╠{borde}╣")
    for numero, texto in OPCIONES_MENU:
        print(f"║  {numero}. {texto:<{ANCHO_MENU - 5}}║")
    print(f"╚{borde}╝")


def guardar_todo(inventario, ventas):
    """Registra los cambios y ventas del inventario en el .CSV"""
    guardado_inventario = Archivos.guardar_inventario(inventario)
    guardado_ventas = Archivos.guardar_ventas(ventas)
    return guardado_inventario and guardado_ventas


# acciones

def accion_agregar(inventario, ventas):
    """Para pedir los datos del nuevo producto y de la misma forma registrarlo"""
    print("\n--- Agregar producto ---")

    while True:
        codigo = ops.normalizar_codigo(
            input("Código (3 letras + 3 dígitos, ej. PAN001; Enter para cancelar): ")
        )
        if not codigo:
            print("Operación cancelada.")
            return
        if not ops.codigo_valido(codigo):
            print("  Código inválido: usa 3 letras y 3 dígitos (ej. PAN001).")
        elif codigo in inventario:
            print(f"  El código {codigo} ya existe.")
        else:
            break

    nombre = pedir_texto_no_vacio("Nombre del producto: ")
    categorias = sorted(ops.obtener_categorias(inventario))
    if categorias:
        print(f"Categorías existentes: {', '.join(categorias)}")
    categoria = pedir_texto_no_vacio("Categoría: ")
    precio = pedir_decimal(f"Precio con IVA incluido ({ops.SIMBOLO_MONEDA}): ")
    stock = pedir_entero("Stock inicial: ", minimo=0)
    paga_iva = pedir_si_no("¿Este producto paga IVA?")

    try:
        producto = ops.agregar_producto(inventario, codigo, nombre, categoria,
                                        precio, stock, paga_iva)
    except ValueError as error:
        print(f"No se pudo agregar: {error}")
        return

    guardar_todo(inventario, ventas)
    Archivos.registrar_bitacora(
        f"ALTA producto {producto['codigo']} '{producto['nombre']}' "
        f"({producto['categoria']}) precio {producto['precio']:.2f} stock {producto['stock']}"
    )
    print(f"Producto {producto['codigo']} agregado correctamente.")


def accion_buscar(inventario):
    """La funcion que busca el producto """
    print("\n--- Buscar producto ---")
    print("1. Por código")
    print("2. Por nombre (coincidencia parcial)")
    modo = input("Elige una opción: ").strip()

    if modo == "1":
        producto = ops.buscar_por_codigo(inventario, input("Código: "))
        resultados = [producto] if producto else []
    elif modo == "2":
        resultados = ops.buscar_por_nombre(inventario, input("Nombre (o parte): "))
    else:
        print("Opción inválida.")
        return

    if resultados:
        print(f"\n{len(resultados)} resultado(s):")
        print(ops.formatear_inventario(resultados))
    else:
        print("No se encontraron productos.")


def accion_venta(inventario, ventas):
    """Registrar la venta y actualizar el stock
    """
    print("\n--- Registrar venta ---")
    codigo = input("Código del producto: ")
    producto = ops.buscar_por_codigo(inventario, codigo)
    if producto is None:
        print("No existe un producto con ese código.")
        return

    print(f"{producto['nombre']} | {ops.formato_moneda(producto['precio'])} | "
          f"stock disponible: {producto['stock']}")
    if producto["stock"] == 0:
        print("No hay stock disponible de este producto.")
        return

    cantidad = pedir_entero("Cantidad a vender: ", minimo=1)
    try:
        venta = ops.registrar_venta(inventario, ventas, codigo, cantidad)
    except ValueError as error:
        print(f"No se pudo registrar la venta: {error}")
        return

    fecha, cod, nombre, cant, subtotal, iva, total = venta
    etiqueta_iva = f"IVA {int(ops.TASA_IVA * 100)}%" if iva > 0 else "IVA (exento)"
    print("\nVenta registrada")
    print(f"  Producto : {nombre} ({cod})")
    print(f"  Cantidad : {cant}")
    print(f"  Subtotal : {ops.formato_moneda(subtotal):>12}")
    print(f"  {etiqueta_iva:<9}: {ops.formato_moneda(iva):>12}")
    print(f"  TOTAL    : {ops.formato_moneda(total):>12}")

    guardar_todo(inventario, ventas)
    Archivos.registrar_bitacora(
        f"VENTA {cod} x{cant} subtotal {subtotal:.2f} iva {iva:.2f} total {total:.2f}"
    )


def accion_mostrar(inventario):
    """Mostrar el inventario  """
    print("\n--- Inventario ---")
    print("Ordenar por:  1. Nombre   2. Precio   3. Categoría")
    criterios = {"1": "nombre", "2": "precio", "3": "categoria"}
    criterio = criterios.get(input("Elige una opción: ").strip())
    if criterio is None:
        print("Opción inválida.")
        return
    print(ops.formatear_inventario(ops.ordenar_inventario(inventario, criterio)))
    print(f"Total de productos: {len(inventario)}")


def accion_reporte(ventas):
    """actualiza el reporte de las ventas"""
    hoy = datetime.now().strftime("%Y-%m-%d")
    print()
    print(ops.generar_reporte_ventas(ventas, hoy))
    Archivos.registrar_bitacora(f"REPORTE de ventas del día {hoy} generado")

def accion_stock(inventario, ventas):
    """Suma unidades al stock de un producto que ya existe"""
    print("\n--- Agregar stock ---")
    codigo = input("Código del producto: ")
    producto = ops.buscar_por_codigo(inventario, codigo)
    if producto is None:
        print("No existe un producto con ese código.")
        return

    print(f"{producto['nombre']} | stock actual: {producto['stock']}")
    cantidad = pedir_entero("Cantidad a agregar: ", minimo=1)

    producto["stock"] += cantidad

    guardar_todo(inventario, ventas)
    Archivos.registrar_bitacora(
        f"STOCK {producto['codigo']} +{cantidad} (nuevo stock {producto['stock']})"
    )
    print(f"Stock actualizado: {producto['nombre']} ahora tiene {producto['stock']} unidades.")

def accion_eliminar(inventario, ventas):
    """Eliminar productos del inventario"""
    print("\n--- Eliminar producto ---")
    codigo = input("Código del producto a eliminar: ")
    producto = ops.buscar_por_codigo(inventario, codigo)
    if producto is None:
        print("No existe un producto con ese código.")
        return

    print(ops.formatear_inventario([producto]))
    if not pedir_si_no("¿Seguro que quieres eliminarlo?"):
        print("Operación cancelada.")
        return

    try:
        eliminado = ops.eliminar_producto(inventario, codigo)
    except ValueError as error:
        print(f"No se pudo eliminar: {error}")
        return

    guardar_todo(inventario, ventas)
    Archivos.registrar_bitacora(f"BAJA producto {eliminado['codigo']} '{eliminado['nombre']}'")
    print(f"Producto {eliminado['codigo']} eliminado.")


# lo que va a ver el profejijiji

def main():
    """Cargar los datos y ejecutar el ciclo del menú y guarda todo al salir"""
    inventario = Archivos.cargar_inventario()
    ventas = Archivos.cargar_ventas()
    Archivos.registrar_bitacora(
        f"INICIO de sesión: {len(inventario)} productos y {len(ventas)} ventas cargados"
    )

    try:
        while True:
            mostrar_menu()
            opcion = input("Elige una opción: ").strip()
            if opcion == "1":
                accion_agregar(inventario, ventas)
            elif opcion == "2":
                accion_buscar(inventario)
            elif opcion == "3":
                accion_venta(inventario, ventas)
            elif opcion == "4":
                accion_mostrar(inventario)
            elif opcion == "5":
                accion_reporte(ventas)
            elif opcion == "6":
                accion_eliminar(inventario, ventas)
            elif opcion == "7":
                accion_stock(inventario, ventas)
            elif opcion == "8":
                break
            else:
                print("Opción inválida. Elige un número del 1 al 8.")
    except (KeyboardInterrupt, EOFError):
        print("\nSesión interrumpida.")
    finally:
        guardar_todo(inventario, ventas)
        Archivos.registrar_bitacora("FIN de sesión: cambios guardados")
        print(f"\nCambios guardados. ¡Hasta pronto, {ops.NOMBRE_NEGOCIO}!")


if __name__ == "__main__":
    main()