"""
app.py
=======
Interfaz gráfica de StreamUCV.

Ejecutar con:  python app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

import customtkinter as ctk

import db

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

REPORTES = [
    "1. Tablas e índices del esquema",
    "2. Cantidad de tablas y índices por tabla",
    "3. Restricciones del esquema",
    "4. Detalle de índices (columnas y unicidad)",
    "5. Triggers del esquema",
    "6. Tamaño ocupado por cada tabla",
    "7. Tamaño estimado de cada registro",
    "8. Tamaño de cada columna",
    "9a. Factor de bloqueo - Tablas",
    "9b. Factor de bloqueo - Índices",
    "10. Costo de acceso por igualdad",
]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("StreamUCV — Explorador del Diccionario de Datos")
        self.geometry("1150x650")
        self.minsize(950, 550)

        self._build_layout()
        self._on_report_change(REPORTES[0])

    
    # Construcción de la interfaz
    def _build_layout(self):
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#111827")
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="📊  StreamUCV — Diccionario de Datos",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left", padx=20, pady=15)

        control = ctk.CTkFrame(self)
        control.pack(fill="x", padx=20, pady=(15, 5))

        self.selected_report = ctk.StringVar(value=REPORTES[0])
        ctk.CTkOptionMenu(
            control,
            values=REPORTES,
            variable=self.selected_report,
            command=self._on_report_change,
            width=420,
        ).pack(side="left", padx=(10, 10), pady=10)

        ctk.CTkButton(
            control,
            text="▶ Ejecutar",
            command=self._ejecutar_reporte,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            width=120,
        ).pack(side="left", padx=(0, 10), pady=10)

        # Contenedor para parámetros dinámicos (usado por el requerimiento 10)
        self.params_frame = ctk.CTkFrame(control, fg_color="transparent")
        self.params_frame.pack(side="left", padx=10)

        self.status_label = ctk.CTkLabel(control, text="", text_color="#9ca3af")
        self.status_label.pack(side="right", padx=15)

        # Banner informativo (totales, resumen del requerimiento 10, etc.)
        self.info_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#60a5fa", anchor="w", justify="left",
        )
        self.info_label.pack(fill="x", padx=22, pady=(2, 5))

        table_container = ctk.CTkFrame(self)
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self._setup_treeview(table_container)

    def _setup_treeview(self, parent):
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#1e1e1e", foreground="#e5e7eb",
            fieldbackground="#1e1e1e", bordercolor="#1e1e1e",
            rowheight=28, font=("Segoe UI", 11),
        )
        style.configure(
            "Treeview.Heading",
            background="#2b2b2b", foreground="#60a5fa",
            font=("Segoe UI", 11, "bold"),
        )
        style.map("Treeview", background=[("selected", "#2563eb")])

        self.tree = ttk.Treeview(parent, show="headings")
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y", pady=10)
        self.tree.configure(yscrollcommand=vsb.set)

   
    # Manejo de parámetros dinámicos (requerimiento 10)
    def _on_report_change(self, value):
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        self.info_label.configure(text="")
        self._clear_tree()

        if value.startswith("10."):
            self._build_req10_params()

    def _build_req10_params(self):
        try:
            tablas = db.req10_listar_tablas()
        except Exception as e:
            tablas = []
            self.status_label.configure(text="Sin conexión")
            messagebox.showerror("Error de conexión", str(e))

        ctk.CTkLabel(self.params_frame, text="Tabla:").pack(side="left", padx=(0, 5))
        self.tabla_var = ctk.StringVar(value=tablas[0] if tablas else "")
        self.tabla_combo = ctk.CTkOptionMenu(
            self.params_frame,
            values=tablas if tablas else ["(sin datos)"],
            variable=self.tabla_var,
            width=150,
        )
        self.tabla_combo.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(self.params_frame, text="Columna:").pack(side="left", padx=(0, 5))
        self.columna_entry = ctk.CTkEntry(self.params_frame, width=140, placeholder_text="nombre_columna")
        self.columna_entry.pack(side="left")

   
    # Utilidades de la tabla
    def _clear_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = []

    def _fill_tree(self, columnas, filas):
        self._clear_tree()
        self.tree["columns"] = columnas
        ancho = max(90, int(950 / max(len(columnas), 1)))
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor="center")
        for fila in filas:
            self.tree.insert("", "end", values=fila)

    
    # Ejecución de reportes
    def _ejecutar_reporte(self):
        reporte = self.selected_report.get()
        self.status_label.configure(text="Ejecutando...")
        self.update_idletasks()
        try:
            if reporte == REPORTES[0]:
                self._fill_tree(*db.req1_tablas_e_indices())

            elif reporte == REPORTES[1]:
                total = db.req2_total_tablas()
                self.info_label.configure(text=f"Total de tablas en el esquema 'streaming': {total}")
                self._fill_tree(*db.req2_cantidad_indices_por_tabla())

            elif reporte == REPORTES[2]:
                self._fill_tree(*db.req3_restricciones())

            elif reporte == REPORTES[3]:
                self._fill_tree(*db.req4_detalle_indices())

            elif reporte == REPORTES[4]:
                self._fill_tree(*db.req5_triggers())

            elif reporte == REPORTES[5]:
                self._fill_tree(*db.req6_tamano_tablas())

            elif reporte == REPORTES[6]:
                self._fill_tree(*db.req7_tamano_registro())

            elif reporte == REPORTES[7]:
                self._fill_tree(*db.req8_tamano_columnas())

            elif reporte == REPORTES[8]:
                self._fill_tree(*db.req9_factor_bloqueo_tablas())

            elif reporte == REPORTES[9]:
                self._fill_tree(*db.req9_factor_bloqueo_indices())

            elif reporte == REPORTES[10]:
                self._ejecutar_req10()

            self.status_label.configure(text="Listo ✓")
        except Exception as e:
            self.status_label.configure(text="Error")
            messagebox.showerror("Error al ejecutar la consulta", str(e))

    def _ejecutar_req10(self):
        tabla = self.tabla_var.get()
        columna = self.columna_entry.get().strip()
        if not tabla or not columna:
            messagebox.showwarning("Datos incompletos", "Selecciona una tabla y escribe el nombre de la columna.")
            self.status_label.configure(text="")
            return

        resultado = db.req10_calcular_costo(tabla, columna)
        if "error" in resultado:
            self.info_label.configure(text=resultado["error"])
            self._clear_tree()
            return

        existe = "SÍ existe índice ✅" if resultado["existe_indice"] else "NO existe índice ❌"
        self.info_label.configure(
            text=(
                f"Tabla: {resultado['tabla']}  |  Columna: {resultado['columna']}  |  {existe}  |  "
                f"Accesos a disco: {resultado['accesos_disco_estimados']}  |  "
                f"Tiempo estimado: {resultado['tiempo_estimado_segundos']} s"
            )
        )

        columnas = ["Campo", "Valor"]
        filas = [
            ["Registros en la tabla", resultado["registros"]],
            ["Tamaño de registro (bytes)", resultado["tamano_registro"]],
            ["Factor de bloqueo", resultado["factor_bloqueo"]],
            ["Páginas totales (escaneo completo)", resultado["paginas_totales"]],
            ["¿Existe índice sobre la columna?", "Sí" if resultado["existe_indice"] else "No"],
            ["Accesos a disco estimados", resultado["accesos_disco_estimados"]],
            ["Tiempo estimado (segundos)", resultado["tiempo_estimado_segundos"]],
        ]
        self._fill_tree(columnas, filas)


if __name__ == "__main__":
    app = App()
    app.mainloop()
