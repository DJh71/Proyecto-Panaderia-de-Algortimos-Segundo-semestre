#Los archivos xd

import csv
import os
from datetime import datetime

CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_INVENTARIO = os.path.join(CARPETA, "inventario.csv")
RUTA_VENTAS = os.path.join(CARPETA, "ventas.csv")
RUTA_BITACORA = os.path.join(CARPETA, "bitacora.log")

CAMPOS_INVENTARIO = ["codigo", "nombre", "categoria", "precio", "stock", "paga_iva"]
CAMPOS_VENTAS = ["fecha", "codigo", "producto", "cantidad", "subtotal", "iva", "total"]


def registrar_bitacora(mensaje):
    """Guarda fecha y hora de la bitacora"""
    marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(RUTA_BITACORA, "a", encoding="utf-8") as archivo:
            archivo.write(f"[{marca}] {mensaje}\n")
        return True
    except OSError as error:
        print(f"Aviso: no se pudo escribir en la bitácora ({error}).")
        return False


def crear_archivo_con_encabezados(ruta, campos):
    """Cree una CSV con unicamente los nombres"""
    try:
        with open(ruta, "w", newline="", encoding="utf-8") as archivo:
            csv.writer(archivo).writerow(campos)
        return True
    except OSError as error:
        print(f"Error: no se pudo crear '{os.path.basename(ruta)}' ({error}).")
        return False


def cargar_inventario():
    """Carga el inventario desde inventario.csv.

    Si el archivo no existe, lo crea con encabezados y devuelve un inventario vacío.
    Las filas dañadas se omiten con un aviso en lugar de detener el programa"""
    inventario = {}
    if not os.path.exists(RUTA_INVENTARIO):
        crear_archivo_con_encabezados(RUTA_INVENTARIO, CAMPOS_INVENTARIO)
        registrar_bitacora("inventario.csv no existía: se creó uno nuevo con encabezados")
        return inventario

    try:
        with open(RUTA_INVENTARIO, newline="", encoding="utf-8-sig") as archivo:
            for numero, fila in enumerate(csv.DictReader(archivo), start=2):
                try:
                    codigo = fila["codigo"].strip().upper()
                    inventario[codigo] = {
                        "codigo": codigo,
                        "nombre": fila["nombre"].strip(),
                        "categoria": fila["categoria"].strip(),
                        "precio": float(fila["precio"]),
                        "stock": int(fila["stock"]),
                        "paga_iva": fila["paga_iva"].strip().upper() in ("SI", "SÍ"),
                    }
                except (ValueError, KeyError, AttributeError):
                    print(f"Aviso: la línea {numero} de inventario.csv es inválida y se omitió.")
    except OSError as error:
        print(f"Error: no se pudo leer inventario.csv ({error}).")
    return inventario


def guardar_inventario(inventario):
    """Guarda todo el inventario en inventario.csv (sobrescribe el archivo)"""
    try:
        with open(RUTA_INVENTARIO, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(CAMPOS_INVENTARIO)
            for codigo in sorted(inventario):
                p = inventario[codigo]
                escritor.writerow([
                    p["codigo"], p["nombre"], p["categoria"],
                    f"{p['precio']:.2f}", p["stock"], "SI" if p["paga_iva"] else "NO",
                ])
        return True
    except OSError as error:
        print(f"Error: no se pudo guardar el inventario ({error}).")
        return False


def cargar_ventas():
    """Carga las ventas desde ventas.csv como una lista de tuplas"""
    ventas = []
    if not os.path.exists(RUTA_VENTAS):
        crear_archivo_con_encabezados(RUTA_VENTAS, CAMPOS_VENTAS)
        registrar_bitacora("ventas.csv no existía: se creó uno nuevo con encabezados")
        return ventas

    try:
        with open(RUTA_VENTAS, newline="", encoding="utf-8-sig") as archivo:
            for numero, fila in enumerate(csv.DictReader(archivo), start=2):
                try:
                    ventas.append((
                        fila["fecha"], fila["codigo"], fila["producto"],
                        int(fila["cantidad"]), float(fila["subtotal"]),
                        float(fila["iva"]), float(fila["total"]),
                    ))
                except (ValueError, KeyError, TypeError):
                    print(f"Aviso: la línea {numero} de ventas.csv es inválida y se omitió.")
    except OSError as error:
        print(f"Error: no se pudo leer ventas.csv ({error}).")
    return ventas


def guardar_ventas(ventas):
    """Guarda todas las ventas en ventas.csv (sobrescribe el archivo)"""
    try:
        with open(RUTA_VENTAS, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(CAMPOS_VENTAS)
            for fecha, codigo, producto, cantidad, subtotal, iva, total in ventas:
                escritor.writerow([fecha, codigo, producto, cantidad,
                                   f"{subtotal:.2f}", f"{iva:.2f}", f"{total:.2f}"])
        return True
    except OSError as error:
        print(f"Error: no se pudieron guardar las ventas ({error}).")
        return False