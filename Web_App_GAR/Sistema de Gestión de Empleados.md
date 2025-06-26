# Sistema de Gestión de Empleados

Una aplicación web completa desarrollada con Streamlit y Python para la gestión integral de empleados, contratos, actividades y reportes.

## 🚀 Características Principales

- ✅ **Autenticación de usuarios** con roles diferenciados (Administrador/Empleado)
- 📊 **Panel de administración** completo con métricas en tiempo real
- 👤 **Interfaz de empleado** intuitiva para registro de actividades
- 🔄 **Conexión dual** a SQL Server y Excel como respaldo
- 📱 **Interfaz responsiva** que funciona en desktop y móvil
- 📧 **Sistema de notificaciones** integrado

## 🛠️ Tecnologías Utilizadas

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **Base de Datos**: SQL Server (con fallback a Excel)
- **Librerías**: pandas, pyodbc, openpyxl

## 📦 Instalación Rápida

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd employee_app
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**
   ```bash
   streamlit run app.py
   ```

4. **Acceder al sistema**
   - Abrir navegador en `http://localhost:8501`
   - Usar credenciales de prueba:
     - **Admin**: empleado1@example.com / 123456
     - **Empleado**: empleado2@example.com / 123456

## 📋 Estructura del Proyecto

```
employee_app/
├── app.py                 # Aplicación principal
├── database.py           # Gestor de base de datos
├── auth.py              # Sistema de autenticación
├── admin_interface.py   # Interfaz de administrador
├── employee_interface.py # Interfaz de empleado
├── requirements.txt     # Dependencias
├── Basedatos.xlsx      # Datos de ejemplo
├── schema.sql          # Esquema de BD
├── documentacion.md    # Documentación completa
└── README.md           # Este archivo
```

## 🎯 Funcionalidades

### Para Administradores
- Dashboard con métricas de empleados y actividades
- Gestión completa de empleados (CRUD)
- Administración de contratos y actividades
- Visualización de reportes de empleados
- Sistema de envío de notificaciones

### Para Empleados
- Dashboard personal con progreso de actividades
- Registro de acciones realizadas
- Autoevaluación de calidad del trabajo
- Visualización de reportes personales
- Recepción de notificaciones

## 🔧 Configuración

### Base de Datos SQL Server (Opcional)
```bash
# Instalar drivers ODBC (Linux)
sudo apt-get install unixodbc unixodbc-dev

# Crear base de datos usando schema.sql
sqlcmd -S localhost -i schema.sql
```

### Variables de Entorno
```bash
export DB_SERVER="localhost"
export DB_NAME="EmployeeDB"
export DB_USER="usuario"
export DB_PASSWORD="contraseña"
```

## 📖 Documentación

La documentación completa está disponible en:
- **Markdown**: `documentacion.md`
- **PDF**: `documentacion.pdf`

Incluye:
- Manual de usuario detallado
- Documentación técnica completa
- Guía de instalación y configuración
- Solución de problemas comunes

## 🧪 Usuarios de Prueba

| Usuario | Email | Rol | Contraseña |
|---------|-------|-----|------------|
| Empleado 1 | empleado1@example.com | Administrador | 123456 |
| Empleado 2 | empleado2@example.com | Empleado | 123456 |

## 🚀 Despliegue

### Local
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Producción
- Configurar proxy reverso (nginx/Apache)
- Habilitar HTTPS
- Configurar base de datos SQL Server
- Implementar medidas de seguridad adicionales

## 🔒 Seguridad

**Nota**: La versión actual utiliza autenticación simplificada para desarrollo. Para producción se recomienda:
- Implementar hashing de contraseñas
- Agregar autenticación de dos factores
- Configurar HTTPS
- Implementar auditoría de acciones

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para nueva funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Revisar la documentación completa en `documentacion.pdf`
- Consultar la sección de solución de problemas
- Crear un issue en el repositorio

## 🎉 Agradecimientos

Desarrollado con ❤️ usando herramientas modernas de Python y la potencia de Streamlit para crear interfaces web intuitivas.

---

**Versión**: 1.0  
**Fecha**: Junio 2025  
**Autor**: Manus AI

