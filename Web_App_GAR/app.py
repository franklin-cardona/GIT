import streamlit as st
from database import DatabaseManager
from auth import AuthManager
from admin_interface import AdminInterface
from employee_interface import EmployeeInterface

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Gestión de Empleados",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Inicializar el gestor de base de datos
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager("Basedatos.xlsx")
        # Intentar conectar a SQL Server (fallback a Excel si falla)
        st.session_state.db_manager.connect_to_sql_server()
        if st.session_state.db_manager.use_excel:
            st.session_state.db_manager.excel_path = "Basedatos.xlsx"
            st.write("Usando archivo Excel como base de datos.")
        elif st.session_state.db_manager.sql_connection:
            st.write(f"Conectado a SQL Server exitosamente. Usando la base de datos: {st.session_state.db_manager.sql_connection.getinfo(pyodbc.SQL_DBMS_NAME)}")
    else:
        # Si ya existe, verificar la conexión
        if not st.session_state.db_manager.sql_connection:
            st.session_state.db_manager.connect_to_sql_server()

    # Inicializar el gestor de autenticación
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager(
            st.session_state.db_manager)

    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🏢 Sistema de Gestión de Empleados</h1>
        <p>Plataforma integral para la gestión de actividades y reportes</p>
    </div>
    """, unsafe_allow_html=True)

    # Verificar autenticación
    if not st.session_state.auth_manager.require_auth():
        # Mostrar formulario de login
        st.session_state.auth_manager.login_form()
    else:
        # Usuario autenticado
        user_data = st.session_state.auth_manager.get_current_user()

        # Sidebar con información del usuario
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**👤 Usuario:** {user_data['nombre']}")
            st.markdown(f"**📧 Email:** {user_data['correo']}")
            st.markdown(f"**🔑 Rol:** {user_data['rol'].title()}")
            st.markdown("---")

            # Información de conexión
            if st.session_state.db_manager.use_excel:
                st.warning("📁 Usando archivo Excel")
            else:
                st.success("🗄️ Conectado a SQL Server")

            st.markdown("---")

            # Botón de logout
            if st.button("🚪 Cerrar Sesión", type="secondary"):
                st.session_state.auth_manager.logout()

        # Mostrar interfaz según el rol
        if st.session_state.auth_manager.is_admin(user_data):
            # Interfaz de administrador
            admin_interface = AdminInterface(st.session_state.db_manager)
            admin_interface.show_admin_dashboard()
        else:
            # Interfaz de empleado
            employee_interface = EmployeeInterface(
                st.session_state.db_manager, user_data)
            employee_interface.show_employee_dashboard()


if __name__ == "__main__":
    main()
