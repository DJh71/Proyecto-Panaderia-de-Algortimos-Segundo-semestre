"""Punto de entrada del sistema (única excepción a 'todo dentro de clases')."""
from inventario.app import SistemaInventario

if __name__ == "__main__":
    SistemaInventario("datos/inventario.csv").ejecutar()