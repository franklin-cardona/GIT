import streamlit as st
import pandas as pd
from datetime import datetime
from database import DatabaseManager
from logger import setup_logging


logger = setup_logging()

class AdminInterface:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        logger.info("AdminInterface inicializado.")
    
    @st.cache_data(ttl=300)
    def _get_cached_data(_self, table_name: str, columns: list = None) -> pd.DataFrame:
        """Obtiene datos con caché para mejorar rendimiento"""
        return _self.db_manager.get_data(table_name)
    
    def show_admin_dashboard(self):
        """Muestra el dashboard principal del administrador"""
        st.title("📊 Panel de Administración")

        # Sidebar para navegación
        with st.sidebar:
            st.header("Navegación")
            page = st.selectbox(
                "Seleccionar página:",
                ["Dashboard", "Gestión de Empleados", "Gestión de Contratos",
                 "Gestión de Actividades", "Gestión de Reportes", "Enviar Notificaciones"]
            )

        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Gestión de Empleados":
            self.manage_employees()
        elif page == "Gestión de Contratos":
            self.manage_contracts()
        elif page == "Gestión de Actividades":
            self.manage_activities()
        elif page == "Gestión de Reportes":
            self.manage_reports()
        elif page == "Enviar Notificaciones":
            self.send_notifications()

    def show_dashboard(self):
        """Muestra el dashboard principal con resúmenes"""
        st.header("📈 Resumen General")

        # Obtener datos con caché
        empleados_df = self._get_cached_data('Empleados')
        reportes_df = self._get_cached_data('Reportes')
        actividades_df = self._get_cached_data('Actividades')

        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Empleados", len(empleados_df))

        with col2:
            empleados_activos = len(empleados_df[empleados_df['activo'] == True])
            st.metric("Empleados Activos", empleados_activos)

        with col3:
            st.metric("Total Actividades", len(actividades_df))

        with col4:
            reportes_mes = len(reportes_df)  # Simplificado para el ejemplo
            st.metric("Reportes del Mes", reportes_mes)

        # ... (resto del dashboard) ...

    def manage_employees(self):
        """Gestión de empleados con búsqueda y paginación"""
        st.header("👥 Gestión de Empleados")

        # Barra de búsqueda
        search_term = st.text_input("Buscar empleado por nombre o correo")
        
        empleados_df = self._get_cached_data('Empleados')
        
        # Filtrar por término de búsqueda
        if search_term:
            mask = empleados_df['nombre'].str.contains(search_term, case=False) | \
                   empleados_df['correo'].str.contains(search_term, case=False)
            empleados_df = empleados_df[mask]
        
        # Paginación
        page_size = st.selectbox("Registros por página", [5, 10, 20], index=1)
        total_pages = max(1, (len(empleados_df) // page_size) + (1 if len(empleados_df) % page_size > 0 else 0))
        page = st.number_input('Página', min_value=1, max_value=total_pages, value=1)
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(empleados_df))
        
        # Mostrar tabla paginada
        st.subheader(f"Empleados ({start_idx+1}-{end_idx} de {len(empleados_df)})")
        if not empleados_df.empty:
            st.dataframe(empleados_df.iloc[start_idx:end_idx], use_container_width=True)
        else:
            st.info("No se encontraron empleados")

        # ... (formulario para agregar empleado con validaciones) ...

        if not empleados_df.empty:
            # Agregar botones de acción
            for idx, empleado in empleados_df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])

                with col1:
                    st.write(empleado['nombre'])
                with col2:
                    st.write(empleado['correo'])
                with col3:
                    st.write(empleado['rol'])
                with col4:
                    if st.button("✏️", key=f"edit_{empleado['id_empleado']}"):
                        st.session_state[f'editing_employee_{empleado["id_empleado"]}'] = True
                with col5:
                    if st.button("🗑️", key=f"delete_{empleado['id_empleado']}"):
                        # Aquí iría la lógica de eliminación
                        st.warning(
                            f"Eliminar empleado {empleado['nombre']} (funcionalidad pendiente)")

        # Formulario para agregar nuevo empleado
        st.subheader("➕ Agregar Nuevo Empleado")
        with st.form("add_employee"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre")
                correo = st.text_input("Correo")
            with col2:
                rol = st.selectbox("Rol", ["empleado", "administrador"])
                activo = st.checkbox("Activo", value=True)

            if st.form_submit_button("Agregar Empleado"):
                if nombre and correo:
                    # Obtener el próximo ID
                    # max_id = empleados_df['id_empleado'].max() if not empleados_df.empty else 0
                    # nuevo_id = max_id + 1

                    nuevo_empleado = {
                        # 'id_empleado': nuevo_id,
                        'nombre': nombre,
                        'correo': correo,
                        'rol': rol,
                        'activo': activo
                    }

                    if self.db_manager.insert_data('Empleados', nuevo_empleado):
                        st.success("Empleado agregado exitosamente")
                        st.rerun()
                    else:
                        st.error("Error al agregar empleado")
                else:
                    st.error("Complete todos los campos obligatorios")

    def manage_contracts(self):
        """Gestión de contratos"""
        st.header("📄 Gestión de Contratos")

        contratos_df = self.db_manager.get_data('Contratos')
        empleados_df = self.db_manager.get_data('Empleados')

        # Mostrar contratos existentes
        if not contratos_df.empty:
            st.subheader("Contratos Existentes")
            st.dataframe(contratos_df, use_container_width=True)

        # Formulario para nuevo contrato
        st.subheader("➕ Nuevo Contrato")
        with st.form("add_contract"):
            nombre_contrato = st.text_input("Nombre del Contrato")
            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input("Fecha de Inicio")
            with col2:
                fecha_fin = st.date_input("Fecha de Fin")

            if not empleados_df.empty:
                empleado_options = {f"{emp['nombre']} ({emp['correo']})": emp['id_empleado']
                                    for _, emp in empleados_df.iterrows()}
                empleado_seleccionado = st.selectbox(
                    "Empleado Asignado", list(empleado_options.keys()))

            if st.form_submit_button("Crear Contrato"):
                if nombre_contrato and fecha_inicio and fecha_fin:
                    # max_id = contratos_df['id_contrato'].max(
                    # ) if not contratos_df.empty else 0
                    nuevo_contrato = {
                        # 'id_contrato': max_id + 1,
                        'nombre_contrato': nombre_contrato,
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                        'id_empleado': empleado_options[empleado_seleccionado]
                    }

                    if self.db_manager.insert_data('Contratos', nuevo_contrato):
                        st.success("Contrato creado exitosamente")
                        st.rerun()
                    else:
                        st.error("Error al crear contrato")

    def manage_activities(self):
        """Gestión de actividades"""
        st.header("📋 Gestión de Actividades")

        actividades_df = self.db_manager.get_data('Actividades')
        contratos_df = self.db_manager.get_data('Contratos')

        # Mostrar actividades existentes
        if not actividades_df.empty:
            st.subheader("Actividades Existentes")
            st.dataframe(actividades_df, use_container_width=True)

        # Formulario para nueva actividad
        st.subheader("➕ Nueva Actividad")
        with st.form("add_activity"):
            col1, col2 = st.columns(2)
            with col1:
                nro = st.number_input("Número", min_value=1, step=1)
                descripcion = st.text_area("Descripción")
            with col2:
                if not contratos_df.empty:
                    contrato_options = {contrato['nombre_contrato']: contrato['id_contrato']
                                        for _, contrato in contratos_df.iterrows()}
                    contrato_seleccionado = st.selectbox(
                        "Contrato", list(contrato_options.keys()))
                porcentaje = st.slider("Porcentaje", 0, 100, 0)

            if st.form_submit_button("Crear Actividad"):
                if descripcion and contrato_seleccionado:
                    # max_id = actividades_df['id_actividad'].max(
                    # ) if not actividades_df.empty else 0
                    nueva_actividad = {
                        # 'id_actividad': max_id + 1,
                        'Nro': nro,
                        'descripcion': descripcion,
                        'id_contrato': contrato_options[contrato_seleccionado],
                        'porcentaje': porcentaje
                    }

                    if self.db_manager.insert_data('Actividades', nueva_actividad):
                        st.success("Actividad creada exitosamente")
                        st.rerun()
                    else:
                        st.error("Error al crear actividad")

    def manage_reports(self):
        """Gestión de reportes"""
        st.header("📊 Gestión de Reportes")

        reportes_df = self.db_manager.get_data('Reportes')

        if not reportes_df.empty:
            st.dataframe(reportes_df, use_container_width=True)
        else:
            st.info("No hay reportes disponibles")

    def send_notifications(self):
        """Envío de notificaciones"""
        st.header("📧 Enviar Notificaciones")

        empleados_df = self.db_manager.get_data('Empleados')

        with st.form("send_notification"):
            if not empleados_df.empty:
                empleado_options = ["Todos"] + [f"{emp['nombre']} ({emp['correo']})"
                                                for _, emp in empleados_df.iterrows()]
                destinatario = st.selectbox("Destinatario", empleado_options)

            mensaje = st.text_area("Mensaje")

            if st.form_submit_button("Enviar Notificación"):
                if mensaje:
                    # Aquí iría la lógica de envío de notificaciones
                    st.success(f"Notificación enviada a: {destinatario}")
                else:
                    st.error("Escriba un mensaje")
