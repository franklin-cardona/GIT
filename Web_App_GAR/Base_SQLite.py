import sqlite3

# Crear o conectar a la base de datos
conn = sqlite3.connect("db_gpc.db")
cursor = conn.cursor()

# Crear tablas adaptadas a SQLite
# cursor.executescript("""
# CREATE TABLE Empleados (
#     id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
#     nombre TEXT,
#     correo TEXT UNIQUE,
#     rol TEXT CHECK(rol IN ('administrador', 'empleado')),
#     activo INTEGER DEFAULT 1
# );

# CREATE TABLE Contratos (
#     id_contrato INTEGER PRIMARY KEY AUTOINCREMENT,
#     nombre_contrato TEXT,
#     fecha_inicio DATE,
#     fecha_fin DATE,
#     id_empleado INTEGER,
#     FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
# );

# CREATE TABLE Actividades (
#     id_actividad INTEGER PRIMARY KEY AUTOINCREMENT,
#     Nro INTEGER,
#     descripcion TEXT NOT NULL,
#     id_contrato INTEGER NOT NULL,
#     porcentaje INTEGER,
#     FOREIGN KEY (id_contrato) REFERENCES Contratos(id_contrato)
# );

# CREATE TABLE Notificaciones (
#     id_notificacion INTEGER PRIMARY KEY AUTOINCREMENT,
#     id_empleado INTEGER,
#     mensaje TEXT,
#     fecha_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
#     leido INTEGER DEFAULT 0,
#     FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
# );

# CREATE TABLE Reportes (
#     id_reporte INTEGER PRIMARY KEY AUTOINCREMENT,
#     id_empleado INTEGER NOT NULL,
#     id_actividad INTEGER NOT NULL,
#     fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
#     acciones_realizadas TEXT NOT NULL,
#     comentarios TEXT,
#     porcentaje INTEGER,
#     entregable TEXT NOT NULL,
#     estado INTEGER,
#     FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado),
#     FOREIGN KEY (id_actividad) REFERENCES Actividades(id_actividad)
# );
# """)


# Guardar cambios y cerrar conexión

insert_empleados = """
INSERT INTO Empleados (nombre, correo, rol, activo) VALUES
('Empleado 1', 'empleado1@example.com', 'administrador', 1),
('Empleado 2', 'empleado2@example.com', 'empleado', 1);
"""

cursor.executescript(insert_empleados)

insert_contratos = """
INSERT INTO Contratos (nombre_contrato, fecha_inicio, fecha_fin, id_empleado) VALUES
('Contrato A', '2023-01-01', '2023-12-31', 1),
('Contrato B', '2023-06-01', '2024-05-31', 2);
"""

cursor.executescript(insert_contratos)

insert_actividades = """
INSERT INTO Actividades (Nro, descripcion, id_contrato, porcentaje) VALUES
(101, 'Actividad 1', 1, 50),
(102, 'Actividad 2', 1, 75),
(3, 'Actividad 3', 2, 100);
"""
cursor.executescript(insert_actividades)

insert_notificaciones = """
INSERT INTO Notificaciones (id_empleado, mensaje, fecha_envio, leido) VALUES
(1, 'Mensaje 1', '2023-01-01 10:00:00', ),
(2, 'Mensaje 2', '2023-01-02 11:00:00', 0);
"""
cursor.executescript(insert_notificaciones)

insert_reportes = """
INSERT INTO Reportes (id_empleado, id_actividad, fecha, acciones_realizadas, comentarios, porcentaje, entregable, estado) VALUES
(1, 1, '2023-01-01 9:00:00', 'Acciones realizadas 1', 'Comentarios 1', 50, 'Entregable 1', 1),
(2, 2, '2023-01-02 10:00:00','Acciones realizadas 2', 'Comentarios 2', 75, 'Entregable 2', 1);
"""
cursor.executescript(insert_reportes)

conn.commit()
conn.close()
