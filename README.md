# StreamUCV — Diccionario de Datos (Proyecto #1, ABD)

Aplicación en Python con interfaz gráfica (CustomTkinter) que consulta el
Diccionario de Datos de SQL Server sobre la base `StreamUCV` / esquema
`streaming`, y resuelve los 10 requerimientos del proyecto sin necesidad
de escribir SQL manualmente desde la interfaz.

## 1. Preparar la base de datos

Ejecutar en SQL Server, en este orden:

1. `create_repositorio_sqlserver.sql`
2. `create_tables_sqlserver.sql`
3. `insert_tables_sqlserver.sql`

## 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

También se necesita el **ODBC Driver 17 for SQL Server** instalado
en el sistema operativo.

## 3. Configurar la conexión

Editar `config.py` (es el único archivo donde se tocan estos valores):

```python
SERVER = "localhost"
DATABASE = "StreamUCV"
USERNAME = "sa"
PASSWORD = "tu_password"
DRIVER = "ODBC Driver 17 for SQL Server"
```

## 4. Ejecutar la aplicación

```bash
python app.py
```

## 5. Uso

1. Elegir un requerimiento en el menú desplegable.
2. Presionar **▶ Ejecutar**.
3. El resultado aparece en la tabla. Para el requerimiento 10, además
   debe seleccionarse una tabla y escribirse el nombre de una columna
   antes de ejecutar.

## Estructura del proyecto

```
config.py   -> variables de conexión y supuestos de cálculo
db.py       -> funciones que consultan el Diccionario de Datos (una por requerimiento)
app.py      -> interfaz gráfica (CustomTkinter)
```

## Supuestos de cálculo (Requerimiento 10)

- Tamaño de registro = suma de `max_length` de las columnas de la tabla.
- Factor de bloqueo = `8192 / tamaño_registro` (páginas de 8 KB).
- Si la columna tiene índice: se asumen 2 accesos a disco (índice + página de datos).
- Si no tiene índice: se asume escaneo completo = número total de páginas de la tabla.
- Tiempo estimado = `(accesos_a_disco * tamaño_página_en_MB) / 17 MB/s`.
