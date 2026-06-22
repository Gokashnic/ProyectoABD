--1. Listar el nombre de las tablas e índices existentes en el esquema streaming. 

USE StreamUCV;
GO

SELECT 
    tbl.name AS Nombre_Tabla,
    ind.name AS Nombre_Indices,
    sch.name AS Nombre_Esquemas
FROM sys.tables AS tbl
JOIN sys.schemas AS sch ON  tbl.schema_id = sch.schema_id
JOIN sys.indexes AS ind ON tbl.object_id = ind.object_id
WHERE sch.name = 'streaming';

--2. Indicar la cantidad total de tablas y la cantidad de índices definidos por cada tabla.

SELECT 
    count (sys.indexes.name) AS Cantidad_de_Indices,
    sys.tables.name AS Nombre_Tabla
FROM sys.tables
JOIN sys.schemas ON sys.tables.schema_id = sys.schemas.schema_id
JOIN sys.indexes ON sys.tables.object_id = sys.indexes.object_id
WHERE sys.schemas.name = 'streaming'
GROUP BY sys.tables.name
ORDER BY Cantidad_de_Indices ASC;

SELECT count (sys.tables.name) AS Total_de_Tablas
FROM sys.tables 
JOIN sys.schemas ON sys.tables.schema_id = sys.schemas.schema_id
WHERE sys.schemas.name = 'streaming';


--3. Indicar las restricciones existentes en el esquema, señalando su nombre, tabla asociada y tipo de restricción.

SELECT 
    CONSTRAINT_NAME AS Nombre_Restriccion,
    TABLE_NAME AS Tabla_Asociada,
    CONSTRAINT_TYPE AS Tipo_Restriccion
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = 'streaming';

--4. Para cada índice creado en el esquema, listar las columnas que lo
--conforman, indicar si es único o no, y mostrar información
--relevante del índice disponible en el Diccionario de Datos de SQL
--Server.


SELECT
    tbl.name AS Tabla,
    ind.name AS Indice,
    STRING_AGG(col.name, ', ') AS Columnas,
    ind.type_desc AS TipoIndice,
    CASE
        WHEN ind.is_unique = 1 THEN 'SI'
        ELSE 'NO'
    END AS EsUnico
FROM sys.indexes ind
JOIN sys.index_columns indcol
    ON ind.object_id = indcol.object_id
    AND ind.index_id = indcol.index_id
JOIN sys.columns col
    ON indcol.object_id = col.object_id
    AND indcol.column_id = col.column_id
JOIN sys.tables tbl
    ON ind.object_id = tbl.object_id
WHERE SCHEMA_NAME(tbl.schema_id) = 'streaming'
    AND ind.name IS NOT NULL
GROUP BY tbl.name, ind.name, ind.type_desc, ind.is_unique
ORDER BY tbl.name, ind.name;

--5. Por cada trigger existente en el esquema, indicar su nombre, tipo, 
--estado y tabla que lo activa. 

SELECT 
    trigg.name AS Nombre_Trigger,
    IIF(trigg.is_instead_of_trigger = 1, 'INSTEAD OF', 'AFTER / FOR') AS Tipo_Trigger,
    IIF(trigg.is_disabled = 1, 'Deshabilitado', 'Habilitado') AS Estado_Trigger,
    tbl.name AS Tabla_Activa
FROM sys.triggers trigg
JOIN sys.tables tbl ON trigg.parent_id = tbl.object_id
JOIN sys.schemas sch ON tbl.schema_id = sch.schema_id
WHERE sch.name = 'streaming';

--6. Indicar el tamaño ocupado por cada tabla.

SELECT tbl.name AS Tabla, 
part.rows AS 'Numero de Filas', 
CAST(ROUND((SUM(alocu.total_pages)*8.0) / 1024, 2) AS DECIMAL(10,2)) AS 'Espacio Reservado en MB',
CAST(ROUND((SUM(alocu.used_pages)*8.0) / 1024, 2) AS DECIMAL(10,2)) AS 'Espacio Usado en MB'
FROM sys.tables AS tbl
JOIN sys.indexes AS ind ON tbl.object_id = ind.object_id
JOIN sys.partitions AS part ON ind.object_id = part.object_id AND ind.index_id = part.index_id
JOIN sys.allocation_units AS alocu ON part.partition_id = alocu.container_id
WHERE SCHEMA_NAME(tbl.schema_id) = 'streaming' AND tbl.is_ms_shipped = 0 AND ind.index_id <= 1
GROUP BY tbl.name, part.rows
ORDER BY [Espacio Usado en MB] DESC

--7. Calcular o estimar el tamaño de cada registro en bytes.

SELECT
    tbl.name AS Tabla,
    SUM(col.max_length) AS [TamañoTotalFilaBytes]
FROM sys.tables tbl
JOIN sys.columns col ON tbl.object_id = col.object_id
WHERE SCHEMA_NAME(tbl.schema_id) = 'streaming' 
GROUP BY tbl.name;

--8. Indicar el tamaño de cada columna en bytes, según su tipo de dato
SELECT tbl.name AS Tabla, 
col.name AS Columna,
typ.name AS TipoDato,
col.max_length
FROM sys.tables tbl
JOIN sys.columns col ON tbl.object_id = col.object_id
JOIN sys.types typ  ON col.user_type_id = typ.user_type_id
WHERE SCHEMA_NAME(tbl.schema_id) = 'streaming'
ORDER BY tbl.name, col.column_id;

--9. Calcular el factor de bloqueo de las tablas e índices. Para este
--cálculo se asumirá que los registros son fijos y no extensibles.

SELECT
    tbl.name AS Tabla,
    SUM(col.max_length) AS TamanoRegistro,
    FLOOR(
        8192.0 / SUM(col.max_length)
    ) AS FactorBloqueo
FROM sys.tables tbl
JOIN sys.columns col
    ON tbl.object_id = col.object_id
WHERE SCHEMA_NAME(tbl.schema_id) = 'streaming'
GROUP BY tbl.name;

SELECT
    ind.name AS Indice,
    tbl.name AS Tabla,
    SUM(col.max_length) AS TamanoClaveBytes,
    FLOOR(8192.0 / SUM(col.max_length)) AS FactorBloqueoIndice
FROM sys.indexes ind
JOIN sys.tables tbl
    ON ind.object_id = tbl.object_id
JOIN sys.index_columns indcol
    ON ind.object_id = indcol.object_id
    AND ind.index_id = indcol.index_id
JOIN sys.columns col
    ON indcol.object_id = col.object_id
    AND indcol.column_id = col.column_id
WHERE SCHEMA_NAME(tbl.schema_id) = 'streaming'
  AND ind.name IS NOT NULL
GROUP BY ind.name, tbl.name;

--10. Dada una consulta de igualdad sobre un campo de una tabla,
--indicar si existe un índice que pueda ser utilizado y estimar el
--costo en cantidad de accesos a disco y en tiempo.



--Lista de tablas del esquema, para poblar el combo de selección.
 SELECT tbl.name
    FROM sys.tables tbl
    JOIN sys.schemas sch ON tbl.schema_id = sch.schema_id
    WHERE sch.name = '{ESQUEMA}'
    ORDER BY tbl.name;
--Esta consulta se realiza para buscar si la columna de la tabla dada tiene un índice
   SELECT 1
FROM sys.indexes ind
JOIN sys.index_columns indcol
    ON ind.object_id = indcol.object_id AND ind.index_id = indcol.index_id
JOIN sys.columns col
    ON indcol.object_id = col.object_id AND indcol.column_id = col.column_id
JOIN sys.tables tbl
    ON ind.object_id = tbl.object_id
WHERE SCHEMA_NAME(tbl.schema_id) = '{ESQUEMA}'
    AND tbl.name = ?
    AND col.name = ?;
--Consulta para buscar toda la información requerida para realizar los cálculos en la app.
--Nombre de la tabla, N° de Registros, Tamaño de Registro, Factor de Bloqueo y N° de páginas
WITH DatosTabla AS (
        SELECT
            tbl.object_id,
            tbl.name AS Tabla,
            MAX(part.rows) AS Registros,
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