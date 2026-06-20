"""
config.py
==========
Parámetros de conexión a SQL Server y supuestos de cálculo del proyecto.

Modifica estos valores para ejecutar la aplicación en otro equipo:
- SERVER:   nombre o IP de la instancia de SQL Server (ej: "localhost", "DESKTOP-ABC\\SQLEXPRESS")
- DATABASE: nombre de la base de datos (no debe cambiarse: StreamUCV)
- USERNAME: usuario de SQL Server
- PASSWORD: contraseña del usuario
- DRIVER:   driver ODBC instalado en el equipo (revisar con `pyodbc.drivers()`)
"""

# ------------------------------------------------------------------
# DATOS DE CONEXIÓN — modificar aquí, no en otras partes del código

# ------------------------------------------------------------------
SERVER = "localhost\SQLEXPRESS"
DATABASE = "StreamUCV"
USERNAME = "sa"
PASSWORD = "tu_password"
DRIVER = "ODBC Driver 17 for SQL Server"

# ------------------------------------------------------------------
# SUPUESTOS DE CÁLCULO (según enunciado del Proyecto #1)
# ------------------------------------------------------------------
TAMANO_PAGINA_BYTES = 8192          # SQL Server usa páginas de 8 KB
VELOCIDAD_TRANSFERENCIA_MBPS = 17   # Velocidad de transferencia asumida para costo en tiempo
ESQUEMA = "streaming"
