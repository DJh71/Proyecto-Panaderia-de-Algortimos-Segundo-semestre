#Pues los registros 
from datetime import datetime

NOMBRE_NEGOCIO = "Panadería Las Migajas"
SIMBOLO_MONEDA = "Q"
TASA_IVA = 0.12  # 12 % (Creo recordar que este era el procentaje de iva xd)


#Cadenas 

def normalizar_texto(texto):
    """Quita los espacios extras y deja la primera letra en mayúscula y el resto en minuscula"""
    return " ".join(texto.split()).capitalize()


def normalizar_codigo(codigo):
    """Elima los espacios y guarda el codigo en mayusculas """
    return "".join(codigo.split()).upper()


def codigo_valido(codigo):
    """Valida el codigo con los 3 numeors del final """
    return (
        len(codigo) == 6
        and codigo.isascii()
        and codigo[:3].isalpha()
        and codigo[3:].isdigit()
    )


def formato_moneda(valor):
    """Cambia el formato de los numeros a dinero (quetzales) ej: 123 a Q.123"""
    return f"{SIMBOLO_MONEDA}{valor:,.2f}"


# IVA 

def calcular_iva(total, paga_iva):
    """calcula el iva haciendo subtotal= total / 0.12 """
    if not paga_iva:
        return round(total, 2), 0.0
    subtotal = round(total / (1 + TASA_IVA), 2)
    iva = round(total - subtotal, 2)
    return subtotal, iva


# ------------------------------------------------------------- Inventario ---

def obtener_categorias(inventario):
    """Agarra las categorias que existen pero sin duplicarlas"""
    return {producto["categoria"] for producto in inventario.values()}


def agregar_producto(inventario, codigo, nombre, categoria, precio, stock, paga_iva):
    """Antes de agregar un nuevo producto este validad que no se repita el codigo, nombre y categoria para no tener el mismo producto 2 veces"""
    codigo = normalizar_codigo(codigo)
    nombre = normalizar_texto(nombre)
    categoria = normalizar_texto(categoria)

    if not codigo_valido(codigo):
        raise ValueError("Código inválido: debe tener 3 letras y 3 dígitos (ej. PAN001).")
    if codigo in inventario:
        raise ValueError(f"Ya existe un producto con el código {codigo}.")
    if not nombre or not categoria:
        raise ValueError("El nombre y la categoría no pueden estar vacíos.")
    if precio <= 0:
        raise ValueError("El precio debe ser mayor que 0.")
    if stock < 0:
        raise ValueError("El stock no puede ser negativo.")

    producto = {
        "codigo": codigo, "nombre": nombre, "categoria": categoria,
        "precio": round(precio, 2), "stock": stock, "paga_iva": paga_iva,
    }
    inventario[codigo] = producto
    return producto


def eliminar_producto(inventario, codigo):
    """Elimina un producto directamente del inventario"""
    codigo = normalizar_codigo(codigo)
    if codigo not in inventario:
        raise ValueError(f"No existe ningún producto con el código {codigo}.")
    return inventario.pop(codigo)


def buscar_por_codigo(inventario, codigo):
    """Busca un producto por el codigo exacto """
    return inventario.get(normalizar_codigo(codigo))


def buscar_por_nombre(inventario, texto):
    """Busca productos cuyo nombre contenga el texto, sin distinguir mayúsculas"""
    fragmento = " ".join(texto.split()).casefold()
    if not fragmento:
        return []
    coincidencias = [p for p in inventario.values() if fragmento in p["nombre"].casefold()]
    return sorted(coincidencias, key=lambda p: p["nombre"].casefold())


def ordenar_inventario(inventario, criterio):
    """Devuelve los productos ordenados"""
    criterios = {
        "nombre": lambda p: p["nombre"].casefold(),
        "precio": lambda p: (p["precio"], p["nombre"].casefold()),
        "categoria": lambda p: (p["categoria"].casefold(), p["nombre"].casefold()),
    }
    if criterio not in criterios:
        raise ValueError(f"Criterio de orden desconocido: {criterio}.")
    return sorted(inventario.values(), key=criterios[criterio])


def formatear_inventario(productos):
    """Genera una tabla de texto con columnas alineadas para una lista"""
    if not productos:
        return "No hay productos para mostrar."
    linea = "-" * 76
    filas = [
        linea,
        f"{'Código':<8}{'Nombre':<26}{'Categoría':<14}{'Precio':>11}{'Stock':>7}{'IVA':>10}",
        linea,
    ]
    for p in productos:
        iva = f"{int(TASA_IVA * 100)}%" if p["paga_iva"] else "Exento"
        filas.append(
            f"{p['codigo']:<8}{p['nombre'][:25]:<26}{p['categoria'][:13]:<14}"
            f"{formato_moneda(p['precio']):>11}{p['stock']:>7}{iva:>10}"
        )
    filas.append(linea)
    return "\n".join(filas)


# Ventas 

def registrar_venta(inventario, ventas, codigo, cantidad, fecha=None):
    """Registra una venta validando el stock y desglosando el IVA"""
    codigo = normalizar_codigo(codigo)
    producto = inventario.get(codigo)
    if producto is None:
        raise ValueError(f"No existe ningún producto con el código {codigo}.")
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que 0.")
    if cantidad > producto["stock"]:
        raise ValueError(
            f"Stock insuficiente de '{producto['nombre']}': "
            f"disponible {producto['stock']}, solicitado {cantidad}."
        )

    total = round(producto["precio"] * cantidad, 2)
    subtotal, iva = calcular_iva(total, producto["paga_iva"])
    if fecha is None:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    producto["stock"] -= cantidad
    venta = (fecha, codigo, producto["nombre"], cantidad, subtotal, iva, total)
    ventas.append(venta)
    return venta


def ventas_del_dia(ventas, dia):
    """Filtra las ventas realizadas en el día"""
    return [venta for venta in ventas if venta[0].startswith(dia)]


def generar_reporte_ventas(ventas, dia):
    """Genera el reporte de ventas de el día con las columnas alineadas"""
    del_dia = ventas_del_dia(ventas, dia)
    linea = "=" * 92
    separador = "-" * 92
    filas = [
        linea,
        f"{NOMBRE_NEGOCIO.upper()} - REPORTE DE VENTAS DEL {dia}",
        linea,
        f"{'Fecha':<17}{'Código':<8}{'Producto':<24}{'Cant.':>6}"
        f"{'Subtotal':>12}{'IVA':>11}{'Total':>14}",
        separador,
    ]
    if not del_dia:
        filas.append("No hay ventas registradas en este día.")
        filas.append(linea)
        return "\n".join(filas)

    for fecha, codigo, producto, cantidad, subtotal, iva, total in del_dia:
        filas.append(
            f"{fecha:<17}{codigo:<8}{producto[:23]:<24}{cantidad:>6}"
            f"{formato_moneda(subtotal):>12}{formato_moneda(iva):>11}{formato_moneda(total):>14}"
        )

    unidades = sum(venta[3] for venta in del_dia)
    suma_subtotal = sum(venta[4] for venta in del_dia)
    suma_iva = sum(venta[5] for venta in del_dia)
    suma_total = sum(venta[6] for venta in del_dia)
    filas.append(separador)
    filas.append(
        f"{'TOTALES':<49}{unidades:>6}"
        f"{formato_moneda(suma_subtotal):>12}{formato_moneda(suma_iva):>11}"
        f"{formato_moneda(suma_total):>14}"
    )
    filas.append(f"Ventas realizadas: {len(del_dia)}")
    filas.append(linea)
    return "\n".join(filas)