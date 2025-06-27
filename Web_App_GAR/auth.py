import streamlit as st
import hashlib
# from logger import logger
from database import DatabaseManager


class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def hash_password(self, password: str) -> str:
        """Genera un hash de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate_user(self, email: str, password: str) -> dict:
        """Autentica un usuario y retorna sus datos"""
        try:
            empleados_df = self.db_manager.get_data('Empleados')
            st.chat_message("user")
            st.write(f"Autenticando usuario...{len(empleados_df)}" if st.session_state.get('authenticated') else "Iniciando sesión...")

            # Buscar el usuario por email
            user = empleados_df[empleados_df['correo'] == email]
            st.write(f"Usuario encontrado: {user.shape[0]} coincidencias")

            if user.empty:
                st.write("No se encontró el usuario.")
                return None

            user_data = user.iloc[0]

            # Verificar si el usuario está activo
            if not user_data['activo']:
                # logger.info("Usuario inactivo.")
                return None

            # Para este ejemplo, usaremos una contraseña simple
            # En producción, deberías tener contraseñas hasheadas en la BD
            if password == "123456":  # Contraseña temporal para todos
                # logger.info("Usuario autenticado exitosamente.")
                st.chat_message("system").markdown(
                    f"**Bienvenido, {user_data['nombre']}!**\n"
                    "Tienes acceso a todas las funcionalidades de la aplicación."
                )
                return {
                    'id_empleado': user_data['id_empleado'],
                    'nombre': user_data['nombre'],
                    'correo': user_data['correo'],
                    'rol': user_data['rol']
                }

            # logger.info("Contraseña incorrecta.")

            return None

        except Exception as e:
            st.error(f"Error en autenticación: {e}")
            return None

    def is_admin(self, user_data: dict) -> bool:
        """Verifica si el usuario es administrador"""
        return user_data and user_data.get('rol') == 'administrador'

    def login_form(self):
        """Muestra el formulario de login"""
        st.title("🔐 Iniciar Sesión")

        with st.form("login_form"):
            email = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            submit_button = st.form_submit_button("Iniciar Sesión")

            if submit_button:
                if email and password:
                    user_data = self.authenticate_user(email, password)
                    if user_data:
                        st.session_state['user'] = user_data
                        st.session_state['authenticated'] = True
                        st.success("¡Inicio de sesión exitoso!")
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas o usuario inactivo")
                else:
                    st.error("Por favor, complete todos los campos")

        # Información de usuarios de prueba
        st.info("""
        **Usuarios de prueba:**
        - empleado1@example.com (Administrador)
        - empleado2@example.com (Empleado)
        
        **Contraseña:** 123456
        """)

    def logout(self):
        """Cierra la sesión del usuario"""
        for key in ['user', 'authenticated']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    def require_auth(self):
        """Verifica si el usuario está autenticado"""
        return st.session_state.get('authenticated', False)

    def get_current_user(self):
        """Obtiene los datos del usuario actual"""
        return st.session_state.get('user', None)
