from sqlalchemy import Null
import streamlit as st
from streamlit_modal import Modal
import pandas as pd
import numpy as np
from datetime import datetime
from database import DatabaseManager
from logger import setup_logging
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


logger = setup_logging()


class AdminInterface:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AdminInterface, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_manager: DatabaseManager, user_data: dict = None):
        if self._initialized:
            return
        self.db_manager = db_manager
        self.user_data = user_data
        self.employee_id = user_data['id_empleado']
        logger.info("AdminInterface inicializado.")
        self._initialized = True

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
                ["Dashboard", "Gestión de Colaboradores", "Gestión de Contratos",
                 "Gestión de Actividades", "Gestión de Reportes", "Enviar Notificaciones"]
            )

        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Gestión de Colaboradores":
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
            st.metric("Total Colaboradores", len(empleados_df))

        with col2:
            empleados_activos = len(
                empleados_df[empleados_df['activo'] == True])
            st.metric("Colaboradores Activos", empleados_activos)

        with col3:
            st.metric("Total Actividades", len(actividades_df))

        with col4:
            reportes_mes = len(reportes_df)  # Simplificado para el ejemplo
            st.metric("Reportes del Mes", reportes_mes)

        # ... (resto del dashboard) ...

    def mostrar_formulario_agregar(self, nombre_tabla: str, df: pd.DataFrame, column_id: str):
        # """Muestra un formulario dinámico para agregar registros a una tabla.
        #     Parámetros:- nombre_tabla: str -> nombre de la tabla en la base de datos.
        # - df: pd.DataFrame -> DataFrame con la estructura de la tabla.
        # - db_manager: objeto con método insert_data(nombre_tabla, dict_datos)
        # """
        toggle_key = f"mostrar_formulario_{nombre_tabla}"

        if nombre_tabla != "Empleados":
            df_2 = self._get_cached_data("Empleados")
            df_3 = df_2[df_2['rol'] == 'administrador'].copy()
        else:
            df_2 = pd.DataFrame(
                columns=['id_empleado', 'nombre', 'correo', 'rol', 'activo'])
            df_3 = df_2.copy()

        texto_ejemplo = {'nombre': 'James David Rodríguez Rubio',
                         'correo': 'james.rodriguez@example.com',
                         'password': '123456',
                         'nombre_contrato': 'CPS-001-2025',
                         'fecha_inicio': str(datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")),
                         'fecha_fin': str((datetime.fromtimestamp(time.time()) + relativedelta(months=8)).strftime("%Y-%m-%d")),
                         'descripcion': 'Efectuar las demás actividades derivadas del objeto y naturaleza del contrato, según lo designe la entidad',
                         'obligación contractual': 'Efectuar las demás actividades derivadas del objeto y naturaleza del contrato, según lo designe la entidad',
                         'actividad desarrollada': 'No aplica para el periodo evaluado',
                         'rol': ['Administrador', 'Empleado'],
                         'id_validador': {f"{emp['nombre']} ": emp['id_empleado'] for _, emp in df_3.iterrows()},
                         'id_empleado': {f"{emp['nombre']} ": emp['id_empleado'] for _, emp in df_2.iterrows()}
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
                        ejemplo_valor = texto_ejemplo[col_lower]
                    elif not df[col].dropna().empty:
                        ejemplo_valor = df[col].dropna().iloc[0]
                    else:
                        ejemplo_valor = None  # o algún valor por defecto

                    if isinstance(ejemplo_valor, (list, tuple, np.ndarray)):
                        nuevo_registro[col] = st.selectbox(
                            col, ejemplo_valor, index=1 if len(ejemplo_valor) > 1 else 0)
                    elif isinstance(ejemplo_valor, (dict)):
                        opcion_seleccionada = st.selectbox(
                            col, list(ejemplo_valor.keys()))
                        nuevo_registro[col] = ejemplo_valor[opcion_seleccionada]
                    elif isinstance(ejemplo_valor, (bool, np.bool)):
                        nuevo_registro[col] = st.checkbox(col, value=True)
                    elif isinstance(ejemplo_valor, str) and ejemplo_valor.lower() in ["sí", "no"]:
                        nuevo_registro[col] = st.selectbox(col, ["Sí", "No"])
                    elif isinstance(ejemplo_valor, (int, float)):
                        step = 1 if isinstance(ejemplo_valor, int) else 1
                        nuevo_registro[col] = st.number_input(
                            col, value=int(ejemplo_valor), step=step)
                    elif isinstance(ejemplo_valor, datetime):
                        nuevo_registro[col] = st.date_input(
                            col, value=ejemplo_valor.date())
                    elif isinstance(ejemplo_valor, pd.Timestamp):
                        nuevo_registro[col] = st.date_input(
                            col, value=ejemplo_valor.to_pydatetime().date())
                    elif isinstance(ejemplo_valor, type(None) or ejemplo_valor is Null):
                        nuevo_registro[col] = st.text_input(
                            col, value="", placeholder="Ingrese un valor")
                    else:
                        nuevo_registro[col] = st.text_input(
                            col, value="", placeholder=str(ejemplo_valor))

                if st.form_submit_button("Agregar"):
                    logger.info(
                        f"Nuevo registro para {nombre_tabla}: {nuevo_registro}")
                    # if self.db_manager.insert_data(nombre_tabla, nuevo_registro):
                    #     st.success("Registro agregado exitosamente")
                    #     st.session_state[toggle_key] = False
                    #     st.cache_data.clear()
                    #     st.rerun()
                    # else:
                    #     st.error("Error al agregar registro")
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

        if nombre_tabla != "Empleados":
            df_2 = self._get_cached_data("Empleados")
            df_3 = df_2[df_2['rol'] == 'administrador'].copy()
        else:
            df_2 = pd.DataFrame(
                columns=['id_empleado', 'nombre', 'correo', 'rol', 'activo'])
            df_3 = df_2.copy()

        texto_ejemplo = {'rol': ['Administrador', 'Empleado'],
                         'id_validador': {f"{emp['nombre']} ": emp['id_empleado'] for _, emp in df_3.iterrows()},
                         'id_empleado': {f"{emp['nombre']} ": emp['id_empleado'] for _, emp in df_2.iterrows()}
                         }

        for col in df.columns:
            valor_actual = row[col]
            logger.info(f"Columna: {col}, Valor actual: {valor_actual}")

            col_lower = col.lower()

            if col_lower == next(iter(df.columns)).lower():
                condiciones[col] = valor_actual
                continue

            if col_lower in texto_ejemplo:
                valor_actual = texto_ejemplo[col_lower]
            elif not df[col].dropna().empty:
                valor_actual = df[col].dropna().iloc[0]
            else:
                valor_actual = None

            if isinstance(valor_actual,  (bool, np.bool)):
                valores_actualizados[col] = st.checkbox(
                    col, value=bool(valor_actual))
            elif isinstance(valor_actual, str) and valor_actual.lower() in ["sí", "no"]:
                valores_actualizados[col] = st.selectbox(
                    col, ["Sí", "No"], index=["Sí", "No"].index(valor_actual))
            elif isinstance(valor_actual, (list, tuple, np.ndarray)):
                valores_actualizados[col] = st.selectbox(
                    col, valor_actual, index=1 if len(valor_actual) > 1 else 0)
            elif isinstance(valor_actual, (dict)):
                opcion_seleccionada = st.selectbox(
                    col, list(valor_actual.keys()))
                valores_actualizados[col] = valor_actual[opcion_seleccionada]
            elif isinstance(valor_actual, (int, float)):
                valores_actualizados[col] = st.number_input(
                    col, value=int(valor_actual), step=1 if isinstance(valor_actual, int) else 1)
            elif isinstance(valor_actual, datetime):
                valores_actualizados[col] = st.date_input(
                    col, value=valor_actual.date())
            elif isinstance(valor_actual, pd.Timestamp):
                valores_actualizados[col] = st.date_input(
                    col, value=valor_actual.to_pydatetime().date())
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
            st.title("Tabla de Colaboradores")

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
                for i, (col_name, value) in enumerate(empleado.items()):
                    if 'password' in col_name.lower():
                        cols[i].write(f'**')
                    else:
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
                    st.session_state.employee_to_delete = empleado['id_empleado']
                    st.warning(f"Eliminar fila {index}: {empleado.to_dict()}")

                if st.session_state.get(f'Editando_Empleado_{empleado["id_empleado"]}', False):
                    # Si estamos editando, mostrar formulario de edición

                    st.subheader("Editar Empleado")
                    logger.info(
                        f"Editando empleado...{st.session_state[f'edit_index']}")
                    # logger.info(f"Editando empleado: {row.to_dict()}")
                    # # Formulario para editar empleado
                    with st.form(f"edit_employee_{empleado['id_empleado']}"):
                        self.mostrar_formulario_edicion(
                            "Empleados", empleados_df, f'Editando_Empleado_{empleado["id_empleado"]}', empleado)

                if st.session_state.get('show_confirm', False) and st.session_state.get('employee_to_delete') == empleado['id_empleado']:
                    with st.form(f"confirm_delete_empleado_{empleado['id_empleado']}"):

                        st.warning(
                            f"¿Estás seguro de eliminar a {empleado['nombre']}?")
                        eliminar = st.form_submit_button("Sí, Eliminar")
                        cancelar = st.form_submit_button("Cancelar")
                        if eliminar:
                            if self.db_manager.delete_data('Empleados', {"id_empleado": empleado['id_empleado']}):
                                st.success("Empleado eliminado exitosamente")
                                st.session_state.show_confirm = False
                                del st.session_state['employee_to_delete']
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("Error al eliminar empleado")
                        if cancelar:
                            st.session_state.show_confirm = False
                            del st.session_state['employee_to_delete']
                            st.rerun()

        else:
            st.info("No hay empleados registrados")

        # Formulario para agregar nuevo empleado
        self.mostrar_formulario_agregar(
            nombre_tabla="Empleados", df=empleados_df, column_id="id_empleado")

    def manage_contracts(self):
        """Gestión de contratos con nombres de empleados visibles"""
        st.header("📄 Gestión de Contratos")

        # Obtener datos
        contratos_df = self._get_cached_data('Contratos')
        empleados_df = self._get_cached_data('Empleados')

        # Renombrar columnas para evitar conflictos
        empleados_validador_df = empleados_df.copy()
        empleados_df = empleados_df.rename(
            columns={'id_empleado': 'id_empleado_fk', 'nombre': 'colaborador'})
        empleados_validador_df = empleados_validador_df.rename(
            columns={'id_empleado': 'id_validador_fk', 'nombre': 'validador'})

        # Merge para mostrar nombres
        contratos_df = contratos_df.merge(
            empleados_df[['id_empleado_fk', 'colaborador']],
            left_on='id_empleado', right_on='id_empleado_fk', how='left'
        )
        contratos_df = contratos_df.merge(
            empleados_validador_df[['id_validador_fk', 'validador']],
            left_on='id_validador', right_on='id_validador_fk', how='left'
        )

        contratos_df = contratos_df.drop(
            columns=['id_empleado', 'id_validador', 'id_empleado_fk', 'id_validador_fk'])
        # Mostrar tabla con nombres
        st.subheader("📋 Lista de Contratos")
        if not contratos_df.empty:
            cols = st.columns(len(contratos_df.columns) + 2)
            for i, col in enumerate(contratos_df.columns):
                cols[i].markdown(f"**{col}**")
            cols[-2].markdown("**Editar**")
            cols[-1].markdown("**Eliminar**")

            for index, contrato in contratos_df.iterrows():
                cols = st.columns(len(contrato) + 2)
                for i, (col_name, value) in enumerate(contrato.items()):
                    cols[i].write(value)

                # Botón Editar
                if cols[-2].button("✏️", key=f"edit_{contrato['id_contrato']}"):
                    edit_key = f'Editando_Contrato_{contrato["id_contrato"]}'
                    st.session_state[edit_key] = not st.session_state.get(
                        edit_key, False)
                    st.session_state['edit_index'] = index
                    st.rerun()

                # Botón Eliminar
                if cols[-1].button("🗑️", key=f"delete_{contrato['id_contrato']}"):
                    st.session_state.show_confirm = True
                    st.session_state.contrato_to_delete = contrato['id_contrato']
                    st.warning(f"Eliminar contrato {contrato['id_contrato']}")

                # Formulario de edición
                if st.session_state.get(f'Editando_Contrato_{contrato["id_contrato"]}', False):
                    st.subheader("Editar Contrato")
                    with st.form(f"edit_contrato_{contrato['id_contrato']}"):
                        # Usar el contrato original sin los nombres
                        contrato_original = self._get_cached_data('Contratos')
                        self.mostrar_formulario_edicion(
                            "Contratos", contrato_original, f'Editando_Contrato_{contrato["id_contrato"]}', contrato_original.iloc[st.session_state['edit_index']])

                # Confirmación de eliminación
                if st.session_state.get('show_confirm', False) and st.session_state.get('contrato_to_delete') == contrato['id_contrato']:
                    with st.form(f"confirm_delete_contrato_{contrato['id_contrato']}"):
                        st.warning(
                            f"¿Estás seguro de eliminar el contrato {contrato['id_contrato']}?")
                        eliminar = st.form_submit_button("Sí, Eliminar")
                        cancelar = st.form_submit_button("Cancelar")
                        if eliminar:
                            if self.db_manager.delete_data('Contratos', {"id_contrato": contrato['id_contrato']}):
                                st.success("Contrato eliminado exitosamente")
                                st.session_state.show_confirm = False
                                del st.session_state['contrato_to_delete']
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("Error al eliminar contrato")
                        if cancelar:
                            st.session_state.show_confirm = False
                            del st.session_state['contrato_to_delete']
                            st.rerun()
        else:
            st.info("No hay contratos registrados")

        # Formulario para agregar nuevo contrato
        self.mostrar_formulario_agregar(
            nombre_tabla="Contratos", df=self._get_cached_data('Contratos'), column_id="id_contrato")

    def manage_activities(self):
        """Gestión de actividades con búsqueda y paginación"""

        contratos_df = self._get_cached_data('Contratos')
        actividades_df = self._get_cached_data('Actividades')

        st.header("📋 Gestión de Actividades")

        # Barra de búsqueda
        search_term = st.text_input(
            "Buscar actividad por numero o descripción")

        # Filtrar por término de búsqueda
        # if search_term:
        #     mask = actividades_df['Nro'].astype(str).str.contains(search_term, case=False) | \
        #         actividades_df['descripcion'].str.contains(
        #         search_term, case=False)
        #     actividades_df = actividades_df[mask]

        # # Paginación
        # page_size = st.selectbox("Registros por página", [5, 10, 20], index=1)
        # total_pages = max(1, (len(actividades_df) // page_size) +
        #                   (1 if len(actividades_df) % page_size > 0 else 0))
        # page = st.number_input('Página', min_value=1,
        #                        max_value=total_pages, value=1)
        # start_idx = (page - 1) * page_size
        # end_idx = min(start_idx + page_size, len(actividades_df))

        # actividades_df = actividades_df.iloc[start_idx:end_idx]

        # Mostrar filas de actividades por contrato
        if not contratos_df.empty:
            for _, contrato in contratos_df.iterrows():
                with st.expander(f"📄 {contrato['nombre_contrato']}"):
                    # Obtener actividades del contrato
                    actividades_contrato = actividades_df[actividades_df['id_contrato']
                                                          == contrato['id_contrato']]
                    if not actividades_contrato.empty:
                        for index, actividad in actividades_contrato.iterrows():
                            actividad = actividad[[
                                'Nro', 'descripcion', 'porcentaje']]
                            # cols = st.columns(len(actividad))
                            # for i, value in enumerate(actividad):
                            #     cols[i].write(value)
                            col1, col2, col3 = st.columns([1, 3, 1])
                            with col1:
                                st.write(actividad['Nro'])
                            with col2:
                                st.write(actividad['descripcion'])
                            with col3:
                                st.write(actividad['porcentaje'])
                    else:
                        st.info(
                            f"No hay actividades registradas para el contrato {contrato['nombre_contrato']}")

    def manage_reports(self):
        """Gestión de reportes"""
        st.header("📊 Gestión de Reportes")

        reportes_df = self.db_manager.get_data('Reportes')
        reportes_df = reportes_df[['id_reporte', 'id_empleado', 'id_actividad', 'acciones_realizadas',
                                   'comentarios', 'porcentaje', 'entregable', 'estado']]

        with st.container():
            st.subheader("🔍 Buscar reportes")
            search_term = st.text_input(
                "Buscar por número de reporte o comentario")

            if search_term:
                mask = reportes_df['id_reporte'].astype(str).str.contains(search_term, case=False) | \
                    reportes_df['comentarios'].str.contains(
                        search_term, case=False)
                reportes_df = reportes_df[mask]

        st.divider()

        with st.container():
            st.subheader("📄 Configuración de tabla")
            page_size = st.selectbox(
                "Registros por página", [5, 10, 20], index=1)
            total_pages = max(1, (len(reportes_df) // page_size) +
                              (1 if len(reportes_df) % page_size > 0 else 0))
            page = st.number_input('Página', min_value=1,
                                   max_value=total_pages, value=1)
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, len(reportes_df))
            reportes_df = reportes_df.iloc[start_idx:end_idx]

        if not reportes_df.empty:
            st.divider()
            st.subheader("📋 Tabla de Reportes")

            modal = Modal(key="confirm_modal",
                          title="Confirmación de Guardado")

            for reporte in reportes_df.itertuples():
                key = f"approve_{reporte.id_reporte}"
                if key not in st.session_state:
                    st.session_state[key] = False

            # Botones de acción grupal
            st.markdown("### ✅ Acciones grupales")
            col_all1, col_all2 = st.columns(2)
            with col_all1:
                if st.button("✅ Marcar todos"):
                    for reporte in reportes_df.itertuples():
                        st.session_state[f"approve_{reporte.id_reporte}"] = True
            with col_all2:
                if st.button("❌ Desmarcar todos"):
                    for reporte in reportes_df.itertuples():
                        st.session_state[f"approve_{reporte.id_reporte}"] = False

            st.divider()

            # Encabezados
            cols = st.columns(len(reportes_df.columns) + 3)
            for i, col in enumerate(reportes_df.columns):
                cols[i].markdown(f"**{col}**")
            cols[-3].markdown("**Comentarios**")
            cols[-2].markdown("**Aprobar**")
            cols[-1].markdown("**Guardar**")

            # Filas de reportes
            for index, reporte in reportes_df.iterrows():
                cols = st.columns(len(reporte) + 3)
                for i, value in enumerate(reporte):
                    cols[i].write(value)

                comentario = cols[-3].text_area(
                    "💬", key=f"comment_{reporte['id_reporte']}", placeholder="Escriba un comentario")

                key = f"approve_{reporte['id_reporte']}"
                aprobacion = cols[-2].checkbox("Aprobar", key=key)

                key_save = f"save_{reporte['id_reporte']}"
                if cols[-1].button("💾", key=key_save, disabled=all(st.session_state[f"approve_{r.id_reporte}"] for r in reportes_df.itertuples())):
                    st.session_state.selected_report = reporte['id_reporte']
                    st.session_state.selected_action = "save"
                    modal.open()

                if modal.is_open() and st.session_state.selected_report == reporte['id_reporte'] and st.session_state.selected_action == "save":
                    registro = {
                        "comentarios": comentario,
                        "estado": aprobacion
                    }
                    with modal.container():
                        st.write(
                            f"¿Desea guardar el reporte **{reporte['id_reporte']}** con los siguientes datos?")
                        st.write(f"📝 Comentarios: {comentario}")
                        st.write(
                            f"✅ Aprobación: {'Sí' if aprobacion else 'No'}")
                        if st.button("✅ Confirmar"):
                            if self.db_manager.update_data('Reportes', registro, {"id_reporte": reporte['id_reporte']}):
                                st.success("Reporte actualizado exitosamente")
                            st.session_state.selected_report = None
                            st.session_state.selected_action = None
                            modal.close()
                            st.rerun()
                        if st.button("❌ Cancelar"):
                            st.session_state.selected_report = None
                            st.session_state.selected_action = None
                            st.info("Guardado cancelado")
                            modal.close()
                            st.rerun()

            st.divider()

            # Botón para guardar todos
            st.subheader("💾 Guardado masivo")
            if all(st.session_state[f"approve_{r.id_reporte}"] for r in reportes_df.itertuples()):
                if st.button("💾 Guardar todos los reportes"):
                    for reporte in reportes_df.itertuples():
                        comentario = st.session_state.get(
                            f"comment_{reporte.id_reporte}", "")
                        registro = {
                            "comentarios": comentario,
                            "estado": True
                        }
                        self.db_manager.update_data('Reportes', registro, {
                                                    "id_reporte": reporte.id_reporte})
                    st.success("✅ Todos los reportes han sido guardados.")
                    st.rerun()
            else:
                st.button("💾 Guardar todos los reportes", disabled=True)

        else:
            st.info("🔎 No hay reportes disponibles para mostrar.")

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
