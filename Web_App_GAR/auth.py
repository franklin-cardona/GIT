import streamlit as st
import hashlib
import bcrypt
from database import DatabaseManager
from logger import setup_logging
import re

logger = setup_logging()


class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        logger.info("AuthManager inicializado.")

    def hash_password(self, password: str) -> str:
        """Genera un hash seguro de la contraseña usando bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def authenticate_user(self, email: str, password: str) -> dict:
        """Autentica un usuario y retorna sus datos"""
        try:
            empleados_df = self.db_manager.get_data(
                'Empleados', filters={'correo': email}, limit=1)

            if empleados_df.empty:
                logger.warning(f"Usuario no encontrado: {email}")
                return None

            user_data = empleados_df.iloc[0].to_dict()

            # Verificar si el usuario está activo
            if not user_data.get('activo', False):
                logger.info(f"Usuario inactivo: {email}")
                return None

            # Verificar contraseña (suponiendo que tenemos un campo 'password_hash' en la BD)
            if password == "123456":
                # if 'password_hash' in user_data and user_data['password_hash']:
                # if bcrypt.checkpw(password.encode(), user_data['password_hash'].encode()):
                st.chat_message("system").markdown(
                    f"**Bienvenido, {user_data['nombre']}!**\n"
                    "Tienes acceso a todas las funcionalidades de la aplicación."
                )
                if password == "123456":  # linea a borrar posterior a produccion
                    logger.info(f"Usuario autenticado: {email}")
                    return {
                        'id_empleado': user_data['id_empleado'],
                        'nombre': user_data['nombre'],
                        'correo': user_data['correo'],
                        'rol': user_data['rol']
                    }

            logger.warning("Contraseña incorrecta.")
            return None

        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            return None

    def is_admin(self, user_data: dict) -> bool:
        """Verifica si el usuario es administrador"""
        return user_data and user_data.get('rol') == 'administrador'

    def login_form(self):
        """Muestra el formulario de login con validación de email"""
        st.title("🔐 Iniciar Sesión")

        with st.form("login_form"):
            email = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            submit_button = st.form_submit_button("Iniciar Sesión")

            if submit_button:
                if not email or not password:
                    st.error("Por favor, complete todos los campos")
                    return

                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    st.error("Formato de correo electrónico inválido")
                    return

                user_data = self.authenticate_user(email, password)
                if user_data:
                    st.session_state['user'] = user_data
                    st.session_state['authenticated'] = True
                    st.success("¡Inicio de sesión exitoso!")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas o usuario inactivo")

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
