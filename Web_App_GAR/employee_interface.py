import streamlit as st
import pandas as pd
from datetime import datetime
from database import DatabaseManager
from logger import setup_logging


logger = setup_logging()


class EmployeeInterface:
    def __init__(self, db_manager: DatabaseManager, user_data: dict):
        self.db_manager = db_manager
        self.user_data = user_data
        self.employee_id = user_data['id_empleado']
        logger.info(
            f"EmployeeInterface inicializado para {user_data['nombre']}")

    @st.cache_data(ttl=300)
    def _get_cached_data(_self, table_name: str, employee_id: int = None, columns: list = None) -> pd.DataFrame:
        """Obtiene datos con caché para mejorar rendimiento"""
        filters = {'id_empleado': employee_id} if employee_id else None
        return _self.db_manager.get_data(table_name, filters=filters)

    def show_employee_dashboard(self):
        """Muestra el dashboard del empleado"""
        st.title(f"👤 Panel de {self.user_data['nombre']}")

        # Sidebar para navegación
        with st.sidebar:
            st.header("Navegación")
            page = st.selectbox(
                "Seleccionar página:",
                ["Dashboard", "Agregar Acción", "Mis Reportes", "Notificaciones"]
            )

        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Agregar Acción":
            self.add_action()
        elif page == "Mis Reportes":
            self.show_my_reports()
        elif page == "Notificaciones":
            self.show_notifications()

    def show_dashboard(self):
        """Muestra el dashboard principal del empleado"""
        st.header("📊 Mi Resumen")

        # Obtener datos del empleado con caché
        reportes_df = self._get_cached_data('Reportes', self.employee_id)
        actividades_df = self._get_cached_data('Actividades')
        contratos_df = self._get_cached_data('Contratos')

        # Filtrar reportes del empleado actual
        mis_reportes = reportes_df[reportes_df['id_empleado']
                                   == self.employee_id]

        # Obtener contratos del empleado
        mis_contratos = contratos_df[contratos_df['id_empleado']
                                     == self.employee_id]

        # Métricas del empleado
        col1, col2, col3 = st.columns(3)

        with col1:
            total_actividades = len(mis_reportes)
            st.metric("Total de Actividades", total_actividades)

        with col2:
            reportadas_con_acciones = len(
                mis_reportes[mis_reportes['acciones_realizadas'].notna()])
            st.metric("Reportadas con Acciones", reportadas_con_acciones)

        with col3:
            porcentaje = (reportadas_con_acciones /
                          total_actividades * 100) if total_actividades > 0 else 0
            st.metric("Porcentaje Completado", f"{porcentaje:.1f}%")

        # ... (resto del dashboard) ...

        # Botón para agregar acción
        if st.button("➕ Agregar Nueva Acción", type="primary"):
            st.session_state['page'] = 'Agregar Acción'
            st.rerun()

        # Resumen de actividades por contrato
        st.subheader("📋 Mis Contratos y Actividades")

        if not mis_contratos.empty:
            for _, contrato in mis_contratos.iterrows():
                with st.expander(f"📄 {contrato['nombre_contrato']}"):
                    # Obtener actividades del contrato
                    actividades_contrato = actividades_df[actividades_df['id_contrato']
                                                          == contrato['id_contrato']]

                    if not actividades_contrato.empty:
                        for _, actividad in actividades_contrato.iterrows():
                            # Verificar si hay reporte para esta actividad
                            reporte_actividad = mis_reportes[mis_reportes['id_actividad']
                                                             == actividad['id_actividad']]

                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.write(f"**{actividad['descripcion']}**")
                            with col2:
                                if not reporte_actividad.empty:
                                    st.success("✅ Reportada")
                                else:
                                    st.warning("⏳ Pendiente")
                            with col3:
                                st.write(f"{actividad['porcentaje']}%")
                    else:
                        st.info("No hay actividades asignadas a este contrato")
        else:
            st.info("No tienes contratos asignados")

    def add_action(self):
        """Formulario para agregar una nueva acción"""
        st.header("➕ Agregar Nueva Acción")

        # Obtener datos necesarios
        contratos_df = self.db_manager.get_data('Contratos')
        actividades_df = self.db_manager.get_data('Actividades')
        reportes_df = self.db_manager.get_data('Reportes')

        # Filtrar contratos del empleado
        mis_contratos = contratos_df[contratos_df['id_empleado']
                                     == self.employee_id]

        if mis_contratos.empty:
            st.warning("No tienes contratos asignados")
            return

        with st.form("add_action_form"):
            # Seleccionar contrato
            contrato_options = {contrato['nombre_contrato']: contrato['id_contrato']
                                for _, contrato in mis_contratos.iterrows()}
            contrato_seleccionado = st.selectbox(
                "Seleccionar Contrato", list(contrato_options.keys()))

            # Obtener actividades del contrato seleccionado
            if contrato_seleccionado:
                id_contrato = contrato_options[contrato_seleccionado]
                actividades_contrato = actividades_df[actividades_df['id_contrato'] == id_contrato]

                if not actividades_contrato.empty:
                    actividad_options = {f"{act['descripcion']} (Nro: {act['Nro']})": act['id_actividad']
                                         for _, act in actividades_contrato.iterrows()}
                    actividad_seleccionada = st.selectbox(
                        "Seleccionar Actividad", list(actividad_options.keys()))

                    # Campos del reporte
                    st.subheader("Detalles de la Acción")

                    col1, col2 = st.columns(2)
                    with col1:
                        acciones_realizadas = st.text_area(
                            "Acciones Realizadas", height=150)
                        porcentaje = st.slider(
                            "Porcentaje de Avance", 0, 100, 0)

                    with col2:
                        comentarios = st.text_area("Comentarios", height=100)
                        calidad = st.select_slider("Calificar Calidad",
                                                   options=[1, 2, 3, 4, 5],
                                                   value=3,
                                                   format_func=lambda x: "⭐" * x)
                        entregable = st.text_input("Entregable (opcional)")
                        estado = st.checkbox(
                            "Marcar como completado", value=False)

                    if st.form_submit_button("💾 Guardar Acción", type="primary"):
                        if acciones_realizadas:
                            # Verificar si ya existe un reporte para esta actividad
                            id_actividad = actividad_options[actividad_seleccionada]
                            reporte_existente = reportes_df[
                                (reportes_df['id_empleado'] == self.employee_id) &
                                (reportes_df['id_actividad'] == id_actividad)
                            ]

                            if not reporte_existente.empty:
                                st.warning(
                                    "Ya existe un reporte para esta actividad. ¿Desea actualizarlo?")
                                if st.button("Sí, actualizar"):
                                    # Lógica de actualización
                                    datos_actualizacion = {
                                        'acciones_realizadas': acciones_realizadas,
                                        'comentarios': comentarios,
                                        'calidad': calidad,
                                        'porcentaje': porcentaje,
                                        'entregable': entregable,
                                        'estado': estado,
                                        'fecha_reporte': datetime.now()
                                    }

                                    condicion = f"id_reporte = {reporte_existente.iloc[0]['id_reporte']}"
                                    if self.db_manager.update_data('Reportes', datos_actualizacion, condicion):
                                        st.success(
                                            "Reporte actualizado exitosamente")
                                        st.rerun()
                                    else:
                                        st.error(
                                            "Error al actualizar el reporte")
                            else:
                                # Crear nuevo reporte
                                max_id = reportes_df['id_reporte'].max(
                                ) if not reportes_df.empty else 0
                                nuevo_reporte = {
                                    'id_reporte': max_id + 1,
                                    'id_empleado': self.employee_id,
                                    'id_actividad': id_actividad,
                                    'fecha_reporte': datetime.now(),
                                    'acciones_realizadas': acciones_realizadas,
                                    'comentarios': comentarios,
                                    'calidad': calidad,
                                    'porcentaje': porcentaje,
                                    'entregable': entregable,
                                    'estado': estado
                                }

                                if self.db_manager.insert_data('Reportes', nuevo_reporte):
                                    st.success("Acción guardada exitosamente")
                                    st.rerun()
                                else:
                                    st.error("Error al guardar la acción")
                        else:
                            st.error(
                                "Por favor, describe las acciones realizadas")
                else:
                    st.warning(
                        "No hay actividades disponibles para este contrato")
                    if st.form_submit_button(""):
                        st.rerun()

    def show_my_reports(self):
        """Muestra los reportes del empleado con paginación"""
        st.header("📊 Mis Reportes")

        reportes_df = self._get_cached_data('Reportes', self.employee_id)
        actividades_df = self._get_cached_data('Actividades')

        # Filtrar reportes del empleado
        mis_reportes = reportes_df[reportes_df['id_empleado']
                                   == self.employee_id]

        # Paginación
        page_size = st.selectbox("Registros por página", [5, 10, 20], index=1)
        total_pages = max(1, (len(mis_reportes) // page_size) +
                          (1 if len(mis_reportes) % page_size > 0 else 0))
        page = st.number_input('Página', min_value=1,
                               max_value=total_pages, value=1)
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(mis_reportes))

        if not mis_reportes.empty:
            # Combinar con información de actividades
            reportes_detallados = []
            for idx in range(start_idx, end_idx):
                reporte = mis_reportes.iloc[idx]
                actividad = actividades_df[actividades_df['id_actividad']
                                           == reporte['id_actividad']]
                if not actividad.empty:
                    actividad_info = actividad.iloc[0]
                    reportes_detallados.append({
                        'Fecha': reporte['fecha_reporte'],
                        'Actividad': actividad_info['descripcion'],
                        'Acciones': reporte['acciones_realizadas'][:100] + "..." if len(str(reporte['acciones_realizadas'])) > 100 else reporte['acciones_realizadas'],
                        'Porcentaje': f"{reporte['porcentaje']}%",
                        'Calidad': "⭐" * reporte['calidad'] if pd.notna(reporte['calidad']) else "N/A",
                        'Estado': "✅ Completado" if reporte['estado'] else "⏳ En progreso"
                    })

            if reportes_detallados:
                reportes_df_display = pd.DataFrame(reportes_detallados)
                st.dataframe(reportes_df_display, use_container_width=True)
            else:
                st.info("No se pudieron cargar los detalles de los reportes")
        else:
            st.info("No tienes reportes registrados")

    def show_notifications(self):
        """Muestra las notificaciones del empleado"""
        st.header("📧 Mis Notificaciones")

        notificaciones_df = self.db_manager.get_data('Notificaciones')

        # Filtrar notificaciones del empleado
        mis_notificaciones = notificaciones_df[notificaciones_df['id_empleado']
                                               == self.employee_id]

        if not mis_notificaciones.empty:
            for _, notif in mis_notificaciones.iterrows():
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if notif['leido']:
                            st.info(f"📧 {notif['mensaje']}")
                        else:
                            st.warning(f"📧 **{notif['mensaje']}** (Nueva)")
                    with col2:
                        st.caption(str(notif['fecha_envio']))

                    if not notif['leido']:
                        if st.button("Marcar como leída", key=f"read_{notif['id_notificacion']}"):
                            # Marcar como leída
                            condicion = f"id_notificacion = {notif['id_notificacion']}"
                            if self.db_manager.update_data('Notificaciones', {'leido': True}, condicion):
                                st.rerun()
        else:
            st.info("No tienes notificaciones")
