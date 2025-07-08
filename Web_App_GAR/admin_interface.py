import streamlit as st
from streamlit_modal import Modal
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
            empleados_activos = len(
                empleados_df[empleados_df['activo'] == True])
            st.metric("Empleados Activos", empleados_activos)

        with col3:
            st.metric("Total Actividades", len(actividades_df))

        with col4:
            reportes_mes = len(reportes_df)  # Simplificado para el ejemplo
            st.metric("Reportes del Mes", reportes_mes)

        # ... (resto del dashboard) ...

    def mostrar_formulario_agregar(self, nombre_tabla: str, df: pd.DataFrame):
        # """Muestra un formulario dinámico para agregar registros a una tabla.
        #     Parámetros:- nombre_tabla: str -> nombre de la tabla en la base de datos.
        # - df: pd.DataFrame -> DataFrame con la estructura de la tabla.
        # - db_manager: objeto con método insert_data(nombre_tabla, dict_datos)
        # """
        toggle_key = f"mostrar_formulario_{nombre_tabla}"

        if st.button(f"➕ Agregar nuevo registro a {nombre_tabla}", key=f"btn_toggle_{nombre_tabla}"):
            st.session_state[toggle_key] = not st.session_state.get(
                toggle_key, False)

        if st.session_state.get(toggle_key, False):
            st.subheader(f"Formulario para nuevo registro en {nombre_tabla}")
            with st.form(f"form_agregar_{nombre_tabla}"):
                nuevo_registro = {}

                for col in df.columns:
                    if col.lower() == "id" or col.startswith("id_"):
                        continue  # Omitir campos ID si se generan automáticamente

                    ejemplo_valor = df[col].dropna(
                    ).iloc[0] if not df[col].dropna().empty else ""

                    if isinstance(ejemplo_valor, bool):
                        nuevo_registro[col] = st.checkbox(col, value=True)
                    elif isinstance(ejemplo_valor, str) and ejemplo_valor.lower() in ["sí", "no"]:
                        nuevo_registro[col] = st.selectbox(col, ["Sí", "No"])
                    else:
                        nuevo_registro[col] = st.text_input(
                            col, value=str(ejemplo_valor))

                if st.form_submit_button("Agregar"):
                    if self.db_manager.insert_data(nombre_tabla, nuevo_registro):
                        st.success("Registro agregado exitosamente")
                        st.session_state[toggle_key] = False
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

    def mostrar_formulario_eliminar(self, nombre_tabla: str, df: pd.DataFrame, edit_key: str, row):
        edit_key = edit_key
        logger.info(f"eliminar a : {edit_key} => {row.to_dict()}")
        st.subheader(edit_key)
        condiciones = {}

        for col in df.columns:
            valor_actual = row[col]

            if col.lower() == "id" or col.startswith("id_"):
                # Usar como condición para actualizar
                condiciones[col] = valor_actual
                continue

            eliminar = st.form_submit_button("Sí, Eliminar")
            cancelar = st.form_submit_button("Cancelar")
            if eliminar:
                if self.db_manager.delete_data(nombre_tabla, condiciones):
                    st.success("Registro eliminado exitosamente")
                    st.session_state.show_confirm = False
                    del st.session_state.delete_id
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Error al eliminar empleado")
            if cancelar:
                st.session_state.show_confirm = False
                del st.session_state.delete_id
                st.rerun()

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
        total_pages = max(1, (len(empleados_df) // page_size) +
                          (1 if len(empleados_df) % page_size > 0 else 0))
        page = st.number_input('Página', min_value=1,
                               max_value=total_pages, value=1)
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(empleados_df))

        empleados_df = empleados_df.iloc[start_idx:end_idx]

        # Mostrar tabla con botones Editar y Eliminar
        if not empleados_df.empty:
            st.title("Tabla de Empleados")

            # Mostrar encabezados
            # +2 para Editar y Eliminar
            cols = st.columns(len(empleados_df.columns) + 2)
            for i, col in enumerate(empleados_df.columns):
                cols[i].markdown(f"**{col}**")
            cols[-2].markdown("**Editar**")
            cols[-1].markdown("**Eliminar**")

            # Mostrar filas con botones
            for index, empleado in empleados_df.iterrows():
                cols = st.columns(len(empleado) + 2)
                for i, value in enumerate(empleado):
                    cols[i].write(value)

                # Botón Editar
                if cols[-2].button("✏️", key=f"edit_{empleado['id_empleado']}"):
                    edit_key = f'Editando_Empleado_{empleado["id_empleado"]}'
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
                if cols[-1].button("🗑️", key=f"delete_{empleado['id_empleado']}"):
                    st.session_state.show_confirm = True
                    st.session_state.delete_id = empleado['id_empleado']
                    st.warning(f"Eliminar fila {index}: {empleado.to_dict()}")

                if st.session_state.get(f'Editando_Empleado_{empleado["id_empleado"]}', False):
                    # Si estamos editando, mostrar formulario de edición

                    st.subheader("Editar Empleado")
                    logger.info(
                        f"Editando empleado...{st.session_state[f'edit_index']}")
                    # logger.info(f"Editando empleado: {row.to_dict()}")
                    # # Formulario para editar empleado
                    with st.form(f"edit_employee_{empleado['id_empleado']}"):

                        logger.info(
                            f"Formulario de edición para empleado: {empleado['id_empleado']}")
                        self.mostrar_formulario_edicion(
                            "Empleados", empleados_df, f'Editando_Empleado_{empleado["id_empleado"]}', empleado)

                if st.session_state.get('show_confirm', False) and st.session_state.get('delete_id') == empleado['id_empleado']:
                    with st.form(f"confirm_delete_{empleado['id_empleado']}"):
                        st.warning(
                            f"¿Estás seguro de eliminar a {empleado['nombre']}?")
                        self.mostrar_formulario_eliminar(
                            "Empleados", empleados_df,  f'Eliminando_Empleado_{empleado["id_empleado"]}', empleado)

        else:
            st.info("No hay empleados registrados")

        # Formulario para agregar nuevo empleado
        self.mostrar_formulario_agregar(
            nombre_tabla="Empleados", df=empleados_df)

    def manage_contracts(self):
        """Gestión de contratos con búsqueda y paginación"""
        st.header("👥 Gestión de Contratos")

        # Barra de búsqueda
        search_term = st.text_input("Buscar contrato por nombre")

        contratos_df = self._get_cached_data('Contratos')

        # Filtrar por término de búsqueda
        if search_term:
            mask = contratos_df['nombre_contrato'].str.contains(
                search_term, case=False)
            contratos_df = contratos_df[mask]

        # Paginación
        page_size = st.selectbox("Registros por página", [5, 10, 20], index=1)
        total_pages = max(1, (len(contratos_df) // page_size) +
                          (1 if len(contratos_df) % page_size > 0 else 0))
        page = st.number_input('Página', min_value=1,
                               max_value=total_pages, value=1)
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(contratos_df))

        contratos_df = contratos_df.iloc[start_idx:end_idx]

        # Mostrar tabla con botones Editar y Eliminar
        if not contratos_df.empty:
            st.title("Tabla de Contratos")

            # Mostrar encabezados
            # +2 para Editar y Eliminar
            cols = st.columns(len(contratos_df.columns) + 2)
            for i, col in enumerate(contratos_df.columns):
                cols[i].markdown(f"**{col}**")
            cols[-2].markdown("**Editar**")
            cols[-1].markdown("**Eliminar**")

            # Mostrar filas con botones
            for index, contrato in contratos_df.iterrows():
                cols = st.columns(len(contrato) + 2)
                for i, value in enumerate(contrato):
                    cols[i].write(value)

                # Botón Editar
                if cols[-2].button("✏️", key=f"edit_{contrato['id_contrato']}"):
                    edit_key = f'Editando_Contrato_{contrato["id_contrato"]}'
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
                if cols[-1].button("🗑️", key=f"delete_{contrato['id_contrato']}"):
                    st.session_state.show_confirm = True
                    st.session_state.delete_id = contrato['id_contrato']
                    st.warning(f"Eliminar fila {index}: {contrato.to_dict()}")

                if st.session_state.get(f'Editando_Contrato_{contrato["id_contrato"]}', False):
                    # Si estamos editando, mostrar formulario de edición

                    st.subheader("Editar Contrato")
                    logger.info(
                        f"Editando contrato...{st.session_state[f'edit_index']}")
                    # logger.info(f"Editando contrato: {row.to_dict()}")
                    # # Formulario para editar contrato
                    with st.form(f"edit_employee_{contrato['id_contrato']}"):

                        logger.info(
                            f"Formulario de edición para contrato: {contrato['id_contrato']}")
                        self.mostrar_formulario_edicion(
                            "Contratos", contratos_df, f'Editando_Contrato_{contrato["id_contrato"]}', contrato)

                if st.session_state.get('show_confirm', False) and st.session_state.get('delete_id') == contrato['id_contrato']:
                    with st.form(f"confirm_delete_{contrato['id_contrato']}"):
                        st.warning(
                            f"¿Estás seguro de eliminar a {contrato['nombre']}?")
                        self.mostrar_formulario_eliminar(
                            "Contratos", contratos_df,  f'Eliminando_Contrato_{contrato["id_contrato"]}', contrato)

        else:
            st.info("No hay contratos registrados")

        # Formulario para agregar nuevo contrato
        self.mostrar_formulario_agregar(
            nombre_tabla="Contratos", df=contratos_df)

    def manage_activities(self):
        """Gestión de actividads con búsqueda y paginación"""
        st.header("👥 Gestión de Actividades")

        # Barra de búsqueda
        search_term = st.text_input(
            "Buscar actividad por numero o descripción")

        actividades_df = self._get_cached_data('Actividades')

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
                    st.session_state.delete_id = actividad['id_actividad']
                    st.warning(
                        f"Eliminar fila {index}: {actividad.to_dict()}")

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

                if st.session_state.get('show_confirm', False) and st.session_state.get('delete_id') == actividad['id_actividad']:
                    with st.form(f"confirm_delete_{actividad['id_actividad']}"):
                        st.warning(
                            f"¿Estás seguro de eliminar a {actividad['nombre']}?")
                        self.mostrar_formulario_eliminar(
                            "Actividades", actividades_df,  f'Eliminando_Actividad_{actividad["id_actividad"]}', actividad)

        else:
            st.info("No hay actividads registrados")

        # Formulario para agregar nuevo actividad
        self.mostrar_formulario_agregar(
            nombre_tabla="Actividades", df=actividades_df)

    def manage_reports(self):
        """Gestión de reportes"""
        st.header("📊 Gestión de Reportes")

        reportes_df = self.db_manager.get_data('Reportes')

        # Barra de búsqueda
        search_term = st.text_input(
            "Buscar reporte por numero o descripción")

        # Filtrar por término de búsqueda
        if search_term:
            mask = reportes_df['Nro'].astype(str).str.contains(search_term, case=False) | \
                reportes_df['descripcion'].str.contains(
                search_term, case=False)
            reportes_df = reportes_df[mask]

        # Paginación
        page_size = st.selectbox("Registros por página", [5, 10, 20], index=1)
        total_pages = max(1, (len(reportes_df) // page_size) +
                          (1 if len(reportes_df) % page_size > 0 else 0))
        page = st.number_input('Página', min_value=1,
                               max_value=total_pages, value=1)
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(reportes_df))

        reportes_df = reportes_df.iloc[start_idx:end_idx]

        if not reportes_df.empty:
            # st.dataframe(reportes_df, use_container_width=True)
            st.title("Tabla de Reportes")

            # Mostrar encabezados
            # +2 para Editar y Eliminar
            cols = st.columns(len(reportes_df.columns))
            for i, col in enumerate(reportes_df.columns):
                cols[i].markdown(f"**{col}**")

            # Mostrar filas con botones
            for index, reporte in reportes_df.iterrows():
                cols = st.columns(len(reporte))
                for i, value in enumerate(reporte):
                    cols[i].write(value)
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
