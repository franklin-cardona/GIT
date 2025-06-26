
CREATE TABLE Empleados (
    id_empleado INT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    correo VARCHAR(255) UNIQUE NOT NULL,
    rol VARCHAR(50) NOT NULL, -- 'administrador' o 'empleado'
    activo BOOLEAN NOT NULL
);

CREATE TABLE Contratos (
    id_contrato INT PRIMARY KEY,
    nombre_contrato VARCHAR(255) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    id_empleado INT NOT NULL,
    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
);

CREATE TABLE Actividades (
    id_actividad INT PRIMARY KEY,
    Nro INT NOT NULL,
    descripcion TEXT NOT NULL,
    id_contrato INT NOT NULL,
    porcentaje INT NOT NULL, -- Porcentaje de completado o asignado
    FOREIGN KEY (id_contrato) REFERENCES Contratos(id_contrato)
);

CREATE TABLE Notificaciones (
    id_notificacion INT PRIMARY KEY,
    id_empleado INT NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_envio DATETIME NOT NULL,
    leido BOOLEAN NOT NULL,
    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
);

CREATE TABLE Reportes (
    id_reporte INT PRIMARY KEY,
    id_empleado INT NOT NULL,
    id_actividad INT NOT NULL,
    fecha_reporte DATETIME NOT NULL,
    acciones_realizadas TEXT,
    comentarios TEXT,
    calidad INT, -- Calificación de 1 a 5, por ejemplo
    porcentaje INT,
    entregable VARCHAR(255),
    estado BOOLEAN,
    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado),
    FOREIGN KEY (id_actividad) REFERENCES Actividades(id_actividad)
);


