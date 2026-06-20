"""
db.py
======
Capa de acceso a datos. Contiene la conexión a SQL Server y una función
por cada requerimiento del proyecto. Cada función ejecuta una consulta
sobre el Diccionario de Datos de SQL Server (sys.tables, sys.indexes,
sys.columns, etc.) y devuelve los resultados listos para mostrar en la
interfaz.
"""

import pyodbc
from config import (
    SERVER, DATABASE, USERNAME, PASSWORD, DRIVER,
    TAMANO_PAGINA_BYTES, VELOCIDAD_TRANSFERENCIA_MBPS, ESQUEMA,
)


def get_connection():
    """Crea y devuelve una nueva conexión a SQL Server usando config.py."""
    conn_str = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
    )
    return pyodbc.connect(conn_str)


def _ejecutar(query, params=None):
    """Ejecuta un SELECT y devuelve (lista_columnas, lista_de_filas)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params) if params else cursor.execute(query)
        columnas = [col[0] for col in cursor.description]
        filas = [list(fila) for fila in cursor.fetchall()]
        return columnas, filas
    finally:
        conn.close()


# ============================================================
# Requerimiento 1 — Tablas e índices del esquema
# ============================================================
def req1_tablas_e_indices():
    query = f"""
    SELECT
        tbl.name AS Nombre_Tabla,
        ind.name AS Nombre_Indices,
        sch.name AS Nombre_Esquema
    FROM sys.tables AS tbl
    JOIN sys.schemas AS sch ON tbl.schema_id = sch.schema_id
    JOIN sys.indexes AS ind ON tbl.object_id = ind.object_id
    WHERE sch.name = '{ESQUEMA}';
    """
    return _ejecutar(query)


# ============================================================
# Requerimiento 2 — Cantidad de tablas e índices por tabla
# ============================================================
def req2_cantidad_indices_por_tabla():
    query = f"""
    SELECT
        sys.tables.name AS Tabla,
        count(sys.indexes.name) AS Cantidad_de_Indices
    FROM sys.tables
    JOIN sys.schemas ON sys.tables.schema_id = sys.schemas.schema_id
    JOIN sys.indexes ON sys.tables.object_id = sys.indexes.object_id
    WHERE sys.schemas.name = '{ESQUEMA}'
    GROUP BY sys.tables.name
    ORDER BY Cantidad_de_Indices ASC;
    """
    return _ejecutar(query)


def req2_total_tablas():
    query = f"""
    SELECT count(sys.tables.name) AS Total_de_Tablas
    FROM sys.tables
    JOIN sys.schemas ON sys.tables.schema_id = sys.schemas.schema_id
    WHERE sys.schemas.name = '{ESQUEMA}';
    """
    _, filas = _ejecutar(query)
    return filas[0][0] if filas else 0


# ============================================================
# Requerimiento 3 — Restricciones del esquema
# ============================================================
def req3_restricciones():
    query = f"""
    SELECT
        CONSTRAINT_NAME AS Nombre_Restriccion,
        TABLE_NAME AS Tabla_Asociada,
        CONSTRAINT_TYPE AS Tipo_Restriccion
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = '{ESQUEMA}';
    """
    return _ejecutar(query)


# ============================================================
# Requerimiento 4 — Detalle de índices (columnas, unicidad)
# ============================================================
def req4_detalle_indices():
    query = f"""
    SELECT
        tbl.name AS Tabla,
        ind.name AS Indice,
        STRING_AGG(col.name, ', ') AS Columnas,
        ind.type_desc AS TipoIndice,
        CASE WHEN ind.is_unique = 1 THEN 'SI' ELSE 'NO' END AS EsUnico
    FROM sys.indexes ind
    JOIN sys.index_columns indcol
        ON ind.object_id = indcol.object_id AND ind.index_id = indcol.index_id
    JOIN sys.columns col
        ON indcol.object_id = col.object_id AND indcol.column_id = col.column_id
    JOIN sys.tables tbl
        ON ind.object_id = tbl.object_id
    WHERE SCHEMA_NAME(tbl.schema_id) = '{ESQUEMA}'
        AND ind.name IS NOT NULL
    GROUP BY tbl.name, ind.name, ind.type_desc, ind.is_unique
    ORDER BY tbl.name, ind.name;
    """
    return _ejecutar(query)


# ============================================================
# Requerimiento 5 — Triggers del esquema
# ============================================================
def req5_triggers():
    query = f"""
    SELECT
        trigg.name AS Nombre_Trigger,
        IIF(trigg.is_instead_of_trigger = 1, 'INSTEAD OF', 'AFTER / FOR') AS Tipo_Trigger,
        IIF(trigg.is_disabled = 1, 'Deshabilitado', 'Habilitado') AS Estado_Trigger,
        tbl.name AS Tabla_Activa
    FROM sys.triggers trigg
    JOIN sys.tables tbl ON trigg.parent_id = tbl.object_id
    JOIN sys.schemas sch ON tbl.schema_id = sch.schema_id
    WHERE sch.name = '{ESQUEMA}';
    """
    return _ejecutar(query)


# ============================================================
# Requerimiento 6 — Tamaño ocupado por cada tabla
# ============================================================
def req6_tamano_tablas():
    query = f"""
    SELECT
        tbl.name AS Tabla,
        part.rows AS Numero_de_Filas,
        CAST(ROUND((SUM(alocu.total_pages) * 8.0) / 1024, 2) AS DECIMAL(10,2)) AS Espacio_Reservado_MB,
        CAST(ROUND((SUM(alocu.used_pages) * 8.0) / 1024, 2) AS DECIMAL(10,2)) AS Espacio_Usado_MB
    FROM sys.tables AS tbl
    JOIN sys.indexes AS ind ON tbl.object_id = ind.object_id
    JOIN sys.partitions AS part ON ind.object_id = part.object_id AND ind.index_id = part.index_id
    JOIN sys.allocation_units AS alocu ON part.partition_id = alocu.container_id
    WHERE SCHEMA_NAME(tbl.schema_id) = '{ESQUEMA}' AND tbl.is_ms_shipped = 0 AND ind.index_id <= 1
    GROUP BY tbl.name, part.rows
    ORDER BY Espacio_Usado_MB DESC;
    """
    return _ejecutar(query)


# ============================================================
# Requerimiento 7 — Tamaño estimado de cada registro
# ============================================================
def req7_tamano_registro():
    query = f"""
    SELECT
        tbl.name AS Tabla,
        SUM(col.max_length) AS TamanoTotalFilaBytes
    FROM sys.tables tbl
    JOIN sys.columns col ON tbl.object_id = col.object_id
    WHERE SCHEMA_NAME(tbl.schema_id) = '{ESQUEMA}'
    GROUP BY tbl.name;
    """
    return _ejecutar(query)


# ============================================================
# Requerimiento 8 — Tamaño de cada columna según su tipo de dato
# ============================================================
def req8_tamano_columnas():
    query = f"""
    SELECT
        tbl.name AS Tabla,
        col.name AS Columna,
        typ.name AS TipoDato,
        col.max_length AS TamanoBytes
    FROM sys.tables tbl
    JOIN sys.columns col ON tbl.object_id = col.object_id
    JOIN sys.types typ ON col.user_type_id = typ.user_type_id
    WHERE SCHEMA_NAME(tbl.schema_id) = '{ESQUEMA}'
    ORDER BY tbl.name, col.column_id;
    """
    return _ejecutar(query)


# ============================================================
# Requerimiento 9 — Factor de bloqueo de tablas e índices
# ============================================================
def req9_factor_bloqueo_tablas():
    query = f"""
    SELECT
        tbl.name AS Tabla,
        SUM(col.max_length) AS TamanoRegistro,
        FLOOR(8192.0 / SUM(col.max_length)) AS FactorBloqueo
    FROM sys.tables tbl
    JOIN sys.columns col ON tbl.object_id = col.object_id
    WHERE SCHEMA_NAME(tbl.schema_id) = '{ESQUEMA}'
    GROUP BY tbl.name;
    """
    return _ejecutar(query)


def req9_factor_bloqueo_indices():
    query = f"""
    SELECT
        ind.name AS Indice,
        tbl.name AS Tabla,
        SUM(col.max_length) AS TamanoClaveBytes,
        FLOOR(8192.0 / SUM(col.max_length)) AS FactorBloqueoIndice
    FROM sys.indexes ind
    JOIN sys.tables tbl ON ind.object_id = tbl.object_id
    JOIN sys.index_columns indcol
        ON ind.object_id = indcol.object_id AND ind.index_id = indcol.index_id
    JOIN sys.columns col
        ON indcol.object_id = col.object_id AND indcol.column_id = col.column_id
    WHERE SCHEMA_NAME(tbl.schema_id) = '{ESQUEMA}'
        AND ind.name IS NOT NULL
    GROUP BY ind.name, tbl.name;
    """
    return _ejecutar(query)


# ============================================================
# Requerimiento 10 — Costo de una consulta de igualdad
# ============================================================
def req10_listar_tablas():
    """Lista de tablas del esquema, para poblar el combo de selección."""
    query = f"""
    SELECT tbl.name
    FROM sys.tables tbl
    JOIN sys.schemas sch ON tbl.schema_id = sch.schema_id
    WHERE sch.name = '{ESQUEMA}'
    ORDER BY tbl.name;
    """
    _, filas = _ejecutar(query)
    return [f[0] for f in filas]


def req10_buscar_indice(tabla, columna):
    """Verifica si existe un índice definido sobre la columna indicada."""
    query = f"""
    SELECT
        t.name AS Tabla,
        c.name AS Columna,
        i.name AS Indice,
        i.type_desc AS TipoIndice,
        i.is_unique AS EsUnico,
        i.is_primary_key AS EsLlavePrimaria
    FROM sys.indexes i
    JOIN sys.index_columns ic
        ON i.object_id = ic.object_id AND i.index_id = ic.index_id
    JOIN sys.columns c
        ON ic.object_id = c.object_id AND ic.column_id = c.column_id
    JOIN sys.tables t
        ON i.object_id = t.object_id
    WHERE SCHEMA_NAME(t.schema_id) = '{ESQUEMA}'
        AND t.name = ?
        AND c.name = ?;
    """
    return _ejecutar(query, (tabla, columna))


def req10_datos_tabla(tabla):
    """Registros, tamaño de registro, factor de bloqueo y páginas de la tabla."""
    query = f"""
    WITH DatosTabla AS (
        SELECT
            tbl.object_id,
            tbl.name AS Tabla,
            SUM(part.rows) AS Registros,
            SUM(col.max_length) AS TamanoRegistro
        FROM sys.tables tbl
        JOIN sys.partitions part ON tbl.object_id = part.object_id
        JOIN sys.columns col ON tbl.object_id = col.object_id
        WHERE SCHEMA_NAME(tbl.schema_id) = '{ESQUEMA}'
            AND part.index_id IN (0, 1)
            AND tbl.name = ?
        GROUP BY tbl.object_id, tbl.name
    )
    SELECT
        Tabla,
        Registros,
        TamanoRegistro,
        FLOOR(8192.0 / TamanoRegistro) AS FactorBloqueo,
        CEILING(Registros * 1.0 / FLOOR(8192.0 / TamanoRegistro)) AS Paginas
    FROM DatosTabla;
    """
    return _ejecutar(query, (tabla,))


def req10_calcular_costo(tabla, columna):
    """
    Estima el costo de una consulta de igualdad sobre `columna` en `tabla`.

    Supuestos de cálculo (documentar en el informe):
    - Si existe un índice sobre la columna: se asume acceso casi directo —
      1 acceso de disco para recorrer el índice + 1 acceso para leer la
      página de datos del registro = 2 accesos a disco estimados.
    - Si NO existe índice: se asume un escaneo secuencial completo de la
      tabla, cuyo costo es el número total de páginas de la tabla.
    - El tiempo se estima como (accesos_a_disco * tamaño_de_página en MB)
      dividido entre la velocidad de transferencia (17 MB/s, ver config.py).
    """
    _, indices = req10_buscar_indice(tabla, columna)
    _, datos = req10_datos_tabla(tabla)

    if not datos:
        return {"tabla": tabla, "columna": columna, "error": "No se encontraron datos para esta tabla."}

    _, registros, tamano_registro, factor_bloqueo, paginas = datos[0]
    existe_indice = len(indices) > 0
    accesos_disco = 2 if existe_indice else paginas

    tamano_pagina_mb = TAMANO_PAGINA_BYTES / (1024 * 1024)
    tiempo_segundos = (accesos_disco * tamano_pagina_mb) / VELOCIDAD_TRANSFERENCIA_MBPS

    return {
        "tabla": tabla,
        "columna": columna,
        "existe_indice": existe_indice,
        "indices_encontrados": indices,
        "registros": registros,
        "tamano_registro": tamano_registro,
        "factor_bloqueo": factor_bloqueo,
        "paginas_totales": paginas,
        "accesos_disco_estimados": accesos_disco,
        "tiempo_estimado_segundos": round(tiempo_segundos, 6),
    }
