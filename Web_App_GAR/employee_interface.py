from dateutil.relativedelta import relativedelta
from logger import setup_logging
import time
from database import DatabaseManager
from datetime import datetime
import streamlit as st
import pandas as pd
import locale
# Setea la variable LC_ALL al conjunto de código UTF-8 con descripción español Colombia
locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')


logger = setup_logging()


class EmployeeInterface:
    def __init__(self, db_manager: DatabaseManager, user_data: dict):
        self.db_manager = db_manager
        self.user_data = user_data
        self.employee_id = user_data['id_empleado']
        logger.info(
            f"EmployeeInterface inicializado para {user_data['nombre']}")

    @st.cache_data(ttl=300)
    def _get_cached_data(_self, table_name: str, filters: dict = None) -> pd.DataFrame:
        """Obtiene datos con caché para mejorar rendimiento"""
        return _self.db_manager.get_data(table_name, filters=filters)

    def show_employee_dashboard(self):
        """Muestra el dashboard del empleado"""
        st.title(
            f"👤 Panel de {self.user_data['nombre']} para el mes de {datetime.now().strftime('%B')}")

        # Sidebar para navegación
        with st.sidebar:
            st.header("Navegación")
            page = st.selectbox(
                "Seleccionar página:",
                ["Dashboard", "Mis Actividades", "Agregar Acción",
                    "Mis Reportes", "Notificaciones"]
            )

        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Mis Actividades":
            self.show_my_activities()
        elif page == "Agregar Acción":
            self.add_action()
        elif page == "Mis Reportes":
            self.show_my_reports()
        elif page == "Notificaciones":
            self.show_notifications()

    def show_dashboard(self):
        """Muestra el dashboard principal del empleado"""
        st.header("📊 Mi Resumen")

        mes_actual = 6  # datetime.now().month

        # Obtener datos del empleado con caché
        reportes_df = self._get_cached_data(
            'Reportes', {'id_empleado': self.employee_id})
        contratos_df = self._get_cached_data(
            'Contratos', {'id_empleado': self.employee_id})
        actividades_df = self._get_cached_data('Actividades')
       # Filtrar reportes del empleado actual
        mis_reportes = reportes_df[reportes_df['id_empleado']
                                   == self.employee_id]

        # Obtener contratos del empleado
        mis_contratos = contratos_df.copy()

        # Métricas del empleado
        col1, col2, col3 = st.columns(3)

        with col1:
            total_actividades = len(
                actividades_df[actividades_df['id_contrato'].isin(mis_contratos['id_contrato'])])
            st.metric("Total de Actividades", total_actividades)

        with col2:
            reportadas_con_acciones = len(
                mis_reportes[(mis_reportes['acciones_realizadas'].notna()) & (mis_reportes['fecha'].dt.month == mes_actual)])
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
                            reporte_actividad = mis_reportes[(mis_reportes['id_actividad']
                                                             == actividad['id_actividad']) & (mis_reportes['fecha'].dt.month == datetime.now().month)]

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

    def mostrar_formulario_agregar(self, nombre_tabla: str, df: pd.DataFrame, column_id: str):
        # """Muestra un formulario dinámico para agregar registros a una tabla.
        #     Parámetros:- nombre_tabla: str -> nombre de la tabla en la base de datos.
        # - df: pd.DataFrame -> DataFrame con la estructura de la tabla.
        # - db_manager: objeto con método insert_data(nombre_tabla, dict_datos)
        # """
        toggle_key = f"mostrar_formulario_{nombre_tabla}"

        texto_ejemplo = {'nombre': 'James David Rodríguez Rubio',
                         'correo': 'james.rodriguez@example.com',
                         'password': '123456',
                         'nombre_contrato': '001-2025',
                         'fecha_inicio': str(datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")),
                         'fecha_fin': str((datetime.fromtimestamp(time.time()) + relativedelta(months=8)).strftime("%Y-%m-%d")),
                         'descripcion': 'Efectuar las demás actividades derivadas del objeto y naturaleza del contrato, según lo designe la entidad',
                         'Obligación contractual': 'Efectuar las demás actividades derivadas del objeto y naturaleza del contrato, según lo designe la entidad',
                         'Actividad desarrollada': 'No aplica para el periodo evaluado',
                         }

        if st.button(f"➕ Agregar nuevo registro a {nombre_tabla}", key=f"btn_toggle_{nombre_tabla}"):
            st.session_state[toggle_key] = not st.session_state.get(
                toggle_key, False)

        if st.session_state.get(toggle_key, False):
            st.subheader(f"Formulario para nuevo registro en {nombre_tabla}")
            with st.form(f"form_agregar_{nombre_tabla}"):
                nuevo_registro = {}

                logger.info(df.columns)

                for col in df.columns:
                    if col.lower() == column_id:
                        continue  # Omitir campos ID si se generan automáticamente

                    col_lower = col.lower()

                    if col_lower in texto_ejemplo:
                        ejemplo_valor = f"{texto_ejemplo[col_lower]}"
                    elif not df[col].dropna().empty:
                        ejemplo_valor = df[col].dropna().iloc[0]
                    else:
                        ejemplo_valor = None  # o algún valor por defecto
                    logger.info(f"{col}:{ejemplo_valor}")

                    if isinstance(ejemplo_valor, bool):
                        nuevo_registro[col] = st.checkbox(col, value=True)
                    elif isinstance(ejemplo_valor, str) and ejemplo_valor.lower() in ["sí", "no"]:
                        nuevo_registro[col] = st.selectbox(col, ["Sí", "No"])
                    else:
                        nuevo_registro[col] = st.text_input(
                            col, value="", placeholder=str(ejemplo_valor))

                if st.form_submit_button("Agregar"):
                    if self.db_manager.insert_data(nombre_tabla, nuevo_registro):
                        st.success("Registro agregado exitosamente")
                        st.session_state[toggle_key] = False
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Error al agregar registro")
                cancelar = st.form_submit_button("Cancelar")
                if cancelar:
                    st.session_state[toggle_key] = None
                    st.rerun()

    def mostrar_formulario_edicion(self, nombre_tabla: str, df: pd.DataFrame, edit_key: str, row):
        edit_key = edit_key
        logger.info(f"editando: {edit_key} => {row.to_dict()}")
        st.subheader(edit_key)
        valores_actualizados = {}
        condiciones = {}

        for col in df.columns:
            valor_actual = row[col]

            if col.lower() == "id" or col.startswith("id_"):
                # Usar como condición para actualizar
                condiciones[col] = valor_actual
                continue

            if isinstance(valor_actual, bool):
                valores_actualizados[col] = st.checkbox(
                    col, value=valor_actual)
            elif isinstance(valor_actual, str) and valor_actual.lower() in ["sí", "no"]:
                valores_actualizados[col] = st.selectbox(
                    col, ["Sí", "No"], index=["Sí", "No"].index(valor_actual))
            else:
                valores_actualizados[col] = st.text_input(
                    col, value=str(valor_actual))

        col1, col2 = st.columns(2)
        with col1:
            guardar = st.form_submit_button("Guardar Cambios")
        with col2:
            cancelar = st.form_submit_button("Cancelar")

        if guardar:
            if self.db_manager.update_data(nombre_tabla, valores_actualizados, condiciones):
                st.success("Registro actualizado exitosamente")
                st.session_state[edit_key] = False
                st.session_state['edit_index'] = None
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Error al actualizar registro")

        if cancelar:
            st.session_state[edit_key] = False
            st.info("Edición cancelada")
            st.rerun()

    def show_my_activities(self):
        """Gestión de actividads con búsqueda y paginación"""
        st.header("📋 Gestión de Actividades")

        # Barra de búsqueda
        search_term = st.text_input(
            "Buscar actividad por numero o descripción")

        logger.info(f"Buscando actividades de: {self.employee_id}")

        contratos_df = self._get_cached_data(
            'Contratos', {'id_empleado': self.employee_id})
        if contratos_df.empty:
            st.warning("No tienes contratos asignados")
        actividades_df = self._get_cached_data('Actividades')
        actividades_df = actividades_df[actividades_df['id_contrato'].isin(
            contratos_df['id_contrato'].unique())]

        # Filtrar por término de búsqueda
        if search_term:
            mask = actividades_df['Nro'].astype(str).str.contains(search_term, case=False) | \
                actividades_df['descripcion'].str.contains(
                search_term, case=False)
            actividades_df = actividades_df[mask]

        # Paginación
        page_size = st.selectbox("Registros por página", [5, 10, 20], index=1)
        total_pages = max(1, (len(actividades_df) // page_size) +
                          (1 if len(actividades_df) % page_size > 0 else 0))
        page = st.number_input('Página', min_value=1,
                               max_value=total_pages, value=1)
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(actividades_df))

        actividades_df = actividades_df.iloc[start_idx:end_idx]

        # Mostrar tabla con botones Editar y Eliminar
        if not actividades_df.empty:
            st.title("Tabla de Actividades")

            # Mostrar encabezados
            # +2 para Editar y Eliminar
            cols = st.columns(len(actividades_df.columns) + 2)
            for i, col in enumerate(actividades_df.columns):
                cols[i].markdown(f"**{col}**")
            cols[-2].markdown("**Editar**")
            cols[-1].markdown("**Eliminar**")

            # Mostrar filas con botones
            for index, actividad in actividades_df.iterrows():
                cols = st.columns(len(actividad) + 2)
                for i, value in enumerate(actividad):
                    cols[i].write(value)

                # Botón Editar
                if cols[-2].button("✏️", key=f"edit_{actividad['id_actividad']}"):
                    edit_key = f'Editando_Actividad_{actividad["id_actividad"]}'
                    if st.session_state.get(edit_key, False):
                        # Si ya está en modo edición, cancelar
                        st.session_state[edit_key] = False
                        st.session_state['edit_index'] = None
                        st.success("Edición cancelada")
                        st.rerun()
                    else:
                        # Activar modo edición
                        st.session_state[edit_key] = True
                        st.session_state[f"edit_index"] = index

                # Botón Eliminar
                if cols[-1].button("🗑️", key=f"delete_{actividad['id_actividad']}"):
                    st.session_state.show_confirm = True
                    st.session_state.activitie_to_delete = actividad['id_actividad']
                    st.warning(f"Eliminar fila {index}: {actividad.to_dict()}")

                if st.session_state.get(f'Editando_Actividad_{actividad["id_actividad"]}', False):
                    # Si estamos editando, mostrar formulario de edición

                    st.subheader("Editar Actividad")
                    logger.info(
                        f"Editando actividad...{st.session_state[f'edit_index']}")
                    # logger.info(f"Editando actividad: {row.to_dict()}")
                    # # Formulario para editar actividad
                    with st.form(f"edit_employee_{actividad['id_actividad']}"):

                        logger.info(
                            f"Formulario de edición para actividad: {actividad['id_actividad']}")
                        self.mostrar_formulario_edicion(
                            "Actividades", actividades_df, f'Editando_Actividad_{actividad["id_actividad"]}', actividad)

                if st.session_state.get('show_confirm', False) and st.session_state.get('activitie_to_delete') == actividad['id_actividad']:
                    with st.form(f"confirm_delete_actividad_{actividad['id_actividad']}"):

                        st.warning(
                            f"¿Estás seguro de eliminar a {actividad['Nro']}?")
                        eliminar = st.form_submit_button("Sí, Eliminar")
                        cancelar = st.form_submit_button("Cancelar")
                        if eliminar:
                            if self.db_manager.delete_data('Contratos', {"id_actividad": actividad['id_actividad']}):
                                st.success("actividad eliminada exitosamente")
                                st.session_state.show_confirm = False
                                del st.session_state['activitie_to_delete']
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("Error al eliminar actividad")
                        if cancelar:
                            st.session_state.show_confirm = False
                            del st.session_state['activitie_to_delete']
                            st.rerun()

        else:
            st.info("No hay actividads registrados")

        # Formulario para agregar nuevo actividad
        self.mostrar_formulario_agregar(
            nombre_tabla="Actividades", df=actividades_df, column_id="id_actividad")

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
                                        'porcentaje': porcentaje,
                                        'entregable': entregable,
                                        'estado': estado,
                                        'fecha': datetime.now()
                                    }

                                    condicion = f"id_reporte = {reporte_existente.iloc[0]['id_reporte']}"
                                    if self.db_manager.update_data('Reportes', datos_actualizacion, condicion):
                                        st.success(
                                            "Reporte actualizado exitosamente")
                                        st.cache_data.clear()
                                        st.rerun()
                                    else:
                                        st.error(
                                            "Error al actualizar el reporte")
                            else:
                                # Crear nuevo reporte
                                max_id = reportes_df['id_reporte'].max(
                                ) if not reportes_df.empty else 0
                                nuevo_reporte = {
                                    'id_empleado': self.employee_id,
                                    'id_actividad': id_actividad,
                                    'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'acciones_realizadas': acciones_realizadas,
                                    'comentarios': comentarios,
                                    'porcentaje': porcentaje,
                                    'entregable': entregable,
                                    'estado': estado
                                }

                                if self.db_manager.insert_data('Reportes', nuevo_reporte):
                                    st.success("Acción guardada exitosamente")
                                    st.cache_data.clear()
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

        reportes_df = self._get_cached_data(
            'Reportes', {'id_empleado': self.employee_id})
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
                        'Fecha': reporte['fecha'].strftime("%Y-%m-%d %H:%M:%S"),
                        'Actividad': actividad_info['descripcion'],
                        'Acciones': reporte['acciones_realizadas'][:100] + "..." if len(str(reporte['acciones_realizadas'])) > 100 else reporte['acciones_realizadas'],
                        'Porcentaje': f"{reporte['porcentaje']}%",
                        'Estado': "✅ Aprobado" if reporte['estado'] else "⏳ En Revisión",
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
                                st.cache_data.clear()
                                st.rerun()
        else:
            st.info("No tienes notificaciones")
