# Proyecto: Sistema de gestión de inventario

## Requisitos
- Python 3 instalado.
- No requiere instalar paquetes externos: utiliza `sqlite3`, incluido en Python.

## Archivos
- `inventario.py`: aplicación con menú de terminal.
- `inventario.db`: se crea automáticamente al ejecutar el programa por primera vez.

## Cómo ejecutar
1. Descomprimí el ZIP en una carpeta.
2. Abrí una terminal en esa carpeta.
3. Ejecutá:

   ```bash
   python inventario.py
   ```

   En algunos equipos Windows también podés usar `py inventario.py`.

## Funcionalidades
1. Registrar productos.
2. Visualizar todos los productos.
3. Actualizar productos mediante su ID.
4. Eliminar productos mediante su ID, con confirmación.
5. Buscar productos mediante su ID.
6. Generar un reporte de productos cuya cantidad sea igual o inferior al límite indicado.

## Estructura de la tabla
La tabla `productos` contiene:
- `id`: INTEGER, clave primaria y autoincremental.
- `nombre`: TEXT, obligatorio.
- `descripcion`: TEXT.
- `cantidad`: INTEGER, obligatorio.
- `precio`: REAL, obligatorio.
- `categoria`: TEXT.

## Notas
- Las consultas que reciben datos del usuario utilizan parámetros `?` para ayudar a prevenir inyección SQL.
- Las operaciones de escritura se ejecutan dentro de transacciones administradas por SQLite.
- La base de datos se guarda en la misma carpeta que el archivo Python.
