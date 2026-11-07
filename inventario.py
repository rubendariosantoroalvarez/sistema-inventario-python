"""
Sistema de gestión de inventario
Proyecto en Python + SQLite.

La base de datos inventario.db se crea automáticamente en la misma
carpeta que este programa cuando se ejecuta por primera vez.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("inventario.db")


def conectar():
    """Abre una conexión con la base de datos SQLite."""
    return sqlite3.connect(DB_PATH)


def crear_tabla():
    """Crea la tabla productos si todavía no existe."""
    with conectar() as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL,
                categoria TEXT
            )
        """)


def pedir_entero(mensaje, minimo=None):
    """Solicita un número entero y valida la entrada."""
    while True:
        try:
            valor = int(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"El valor debe ser igual o mayor que {minimo}.")
                continue
            return valor
        except ValueError:
            print("Entrada inválida. Ingresá un número entero.")


def pedir_precio(mensaje):
    """Solicita un precio numérico no negativo."""
    while True:
        try:
            valor = float(input(mensaje).replace(",", "."))
            if valor < 0:
                print("El precio no puede ser negativo.")
                continue
            return valor
        except ValueError:
            print("Entrada inválida. Ingresá un número, por ejemplo 1250.50.")


def mostrar_productos(filas):
    """Muestra una lista de productos en formato legible."""
    if not filas:
        print("\nNo se encontraron productos.")
        return

    print("\n" + "-" * 95)
    print(f"{'ID':<5} {'NOMBRE':<20} {'CANTIDAD':>10} {'PRECIO':>12} {'CATEGORÍA':<18} DESCRIPCIÓN")
    print("-" * 95)
    for producto in filas:
        id_, nombre, descripcion, cantidad, precio, categoria = producto
        print(
            f"{id_:<5} {nombre[:19]:<20} {cantidad:>10} "
            f"${precio:>11.2f} {(categoria or '')[:17]:<18} {descripcion or ''}"
        )
    print("-" * 95)


def registrar_producto():
    """Registra un producto nuevo usando parámetros SQL."""
    print("\n--- Registrar producto ---")
    nombre = input("Nombre: ").strip()
    if not nombre:
        print("El nombre es obligatorio.")
        return

    descripcion = input("Descripción: ").strip()
    cantidad = pedir_entero("Cantidad: ", minimo=0)
    precio = pedir_precio("Precio: ")
    categoria = input("Categoría: ").strip()

    try:
        with conectar() as conexion:
            conexion.execute("""
                INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, descripcion, cantidad, precio, categoria))
        print("Producto registrado correctamente.")
    except sqlite3.Error as error:
        print(f"No se pudo registrar el producto: {error}")


def listar_productos():
    """Consulta y muestra todos los productos."""
    try:
        with conectar() as conexion:
            filas = conexion.execute("""
                SELECT id, nombre, descripcion, cantidad, precio, categoria
                FROM productos ORDER BY id
            """).fetchall()
        mostrar_productos(filas)
    except sqlite3.Error as error:
        print(f"Error al consultar los productos: {error}")


def buscar_producto():
    """Busca un producto por su identificador."""
    print("\n--- Buscar producto por ID ---")
    id_producto = pedir_entero("Ingresá el ID: ", minimo=1)
    try:
        with conectar() as conexion:
            producto = conexion.execute("""
                SELECT id, nombre, descripcion, cantidad, precio, categoria
                FROM productos WHERE id = ?
            """, (id_producto,)).fetchone()
        if producto:
            mostrar_productos([producto])
        else:
            print("No existe un producto con ese ID.")
    except sqlite3.Error as error:
        print(f"Error durante la búsqueda: {error}")


def actualizar_producto():
    """Actualiza todos los campos editables de un producto existente."""
    print("\n--- Actualizar producto ---")
    id_producto = pedir_entero("Ingresá el ID del producto: ", minimo=1)

    try:
        with conectar() as conexion:
            actual = conexion.execute("""
                SELECT id, nombre, descripcion, cantidad, precio, categoria
                FROM productos WHERE id = ?
            """, (id_producto,)).fetchone()

            if actual is None:
                print("No existe un producto con ese ID.")
                return

            print("Dejá un campo vacío para conservar su valor actual.")
            nombre = input(f"Nombre [{actual[1]}]: ").strip() or actual[1]
            descripcion = input(f"Descripción [{actual[2] or ''}]: ").strip()
            if not descripcion:
                descripcion = actual[2] or ""

            cantidad_texto = input(f"Cantidad [{actual[3]}]: ").strip()
            cantidad = actual[3] if not cantidad_texto else int(cantidad_texto)
            if cantidad < 0:
                print("La cantidad no puede ser negativa.")
                return

            precio_texto = input(f"Precio [{actual[4]}]: ").strip()
            precio = actual[4] if not precio_texto else float(precio_texto.replace(",", "."))
            if precio < 0:
                print("El precio no puede ser negativo.")
                return

            categoria = input(f"Categoría [{actual[5] or ''}]: ").strip() or (actual[5] or "")

            # La conexión administra la transacción: confirma al salir sin errores.
            conexion.execute("""
                UPDATE productos
                SET nombre = ?, descripcion = ?, cantidad = ?, precio = ?, categoria = ?
                WHERE id = ?
            """, (nombre, descripcion, cantidad, precio, categoria, id_producto))

        print("Producto actualizado correctamente.")
    except ValueError:
        print("Cantidad o precio inválido. No se realizaron cambios.")
    except sqlite3.Error as error:
        print(f"No se pudo actualizar el producto: {error}")


def eliminar_producto():
    """Elimina un producto según su ID, previa confirmación."""
    print("\n--- Eliminar producto ---")
    id_producto = pedir_entero("Ingresá el ID del producto: ", minimo=1)

    try:
        with conectar() as conexion:
            producto = conexion.execute(
                "SELECT nombre FROM productos WHERE id = ?", (id_producto,)
            ).fetchone()

            if producto is None:
                print("No existe un producto con ese ID.")
                return

            confirmacion = input(
                f"¿Seguro que querés eliminar '{producto[0]}'? (s/n): "
            ).strip().lower()

            if confirmacion == "s":
                conexion.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
                print("Producto eliminado correctamente.")
            else:
                print("Operación cancelada.")
    except sqlite3.Error as error:
        print(f"No se pudo eliminar el producto: {error}")


def reporte_stock_bajo():
    """Lista productos cuya cantidad es igual o inferior al límite ingresado."""
    print("\n--- Reporte de stock bajo ---")
    limite = pedir_entero("Mostrar productos con cantidad igual o inferior a: ", minimo=0)
    try:
        with conectar() as conexion:
            filas = conexion.execute("""
                SELECT id, nombre, descripcion, cantidad, precio, categoria
                FROM productos
                WHERE cantidad <= ?
                ORDER BY cantidad ASC, nombre ASC
            """, (limite,)).fetchall()
        mostrar_productos(filas)
    except sqlite3.Error as error:
        print(f"Error al generar el reporte: {error}")


def menu():
    """Presenta el menú principal y dirige al usuario a cada funcionalidad."""
    crear_tabla()

    while True:
        print("""
========== SISTEMA DE INVENTARIO ==========
1. Registrar nuevo producto
2. Visualizar todos los productos
3. Actualizar producto por ID
4. Eliminar producto por ID
5. Buscar producto por ID
6. Reporte de stock bajo
0. Salir
===========================================
""")
        opcion = input("Seleccioná una opción: ").strip()

        if opcion == "1":
            registrar_producto()
        elif opcion == "2":
            listar_productos()
        elif opcion == "3":
            actualizar_producto()
        elif opcion == "4":
            eliminar_producto()
        elif opcion == "5":
            buscar_producto()
        elif opcion == "6":
            reporte_stock_bajo()
        elif opcion == "0":
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida. Intentá nuevamente.")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nPrograma finalizado por el usuario.")
