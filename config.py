"""
config.py

Parámetros de conexión a SQL Server.

Se modifica estos valores para ejecutar la aplicación en otro equipo:
- SERVER:   nombre o IP de la instancia de SQL Server (ej: "localhost", "DESKTOP-ABC\\SQLEXPRESS")
- DATABASE: nombre de la base de datos (no debe cambiarse: StreamUCV)
- USERNAME: usuario de SQL Server
- PASSWORD: contraseña del usuario
- DRIVER:   driver ODBC instalado en el equipo (revisar con `pyodbc.drivers()`)
"""


# Datos de conexón a SQL Server 
SERVER = "localhost"
DATABASE = "StreamUCV"
USERNAME = "sa"
PASSWORD = "tu_password"
DRIVER = "ODBC Driver 17 for SQL Server"

# Parámetros asumidos para los cálculos.
TAMANO_PAGINA_BYTES = 8192          # SQL Server usa páginas de 8 KB
VELOCIDAD_TRANSFERENCIA_MBPS = 17   # Velocidad de transferencia asumida para costo en tiempo
ESQUEMA = "streaming"
