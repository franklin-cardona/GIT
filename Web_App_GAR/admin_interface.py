import streamlit as st
import pandas as pd
from datetime import datetime
from database import DatabaseManager

class AdminInterface:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
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
        
        # Obtener datos
        empleados_df = self.db_manager.get_data('Empleados')
        reportes_df = self.db_manager.get_data('Reportes')
        actividades_df = self.db_manager.get_data('Actividades')
        
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
        
        # Resumen por empleado
        st.subheader("📋 Resumen por Empleado")
        
        if not reportes_df.empty and not empleados_df.empty:
            # Combinar datos de empleados y reportes
            resumen = []
            for _, empleado in empleados_df.iterrows():
                reportes_empleado = reportes_df[reportes_df['id_empleado'] == empleado['id_empleado']]
                total_actividades = len(reportes_empleado)
                reportadas_con_acciones = len(reportes_empleado[reportes_empleado['acciones_realizadas'].notna()])
                
                resumen.append({
                    'Empleado': empleado['nombre'],
                    'Total Actividades': total_actividades,
                    'Reportadas con Acciones': reportadas_con_acciones,
                    'Porcentaje': f"{(reportadas_con_acciones/total_actividades*100):.1f}%" if total_actividades > 0 else "0%"
                })
            
            resumen_df = pd.DataFrame(resumen)
            st.dataframe(resumen_df, use_container_width=True)
        else:
            st.info("No hay datos de reportes disponibles")
    
    def manage_employees(self):
        """Gestión de empleados"""
        st.header("👥 Gestión de Empleados")
        
        empleados_df = self.db_manager.get_data('Empleados')
        
        # Mostrar tabla de empleados
        st.subheader("Lista de Empleados")
        
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
                        st.warning(f"Eliminar empleado {empleado['nombre']} (funcionalidad pendiente)")
        
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
                    max_id = empleados_df['id_empleado'].max() if not empleados_df.empty else 0
                    nuevo_id = max_id + 1
                    
                    nuevo_empleado = {
                        'id_empleado': nuevo_id,
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
                empleado_seleccionado = st.selectbox("Empleado Asignado", list(empleado_options.keys()))
            
            if st.form_submit_button("Crear Contrato"):
                if nombre_contrato and fecha_inicio and fecha_fin:
                    max_id = contratos_df['id_contrato'].max() if not contratos_df.empty else 0
                    nuevo_contrato = {
                        'id_contrato': max_id + 1,
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
                    contrato_seleccionado = st.selectbox("Contrato", list(contrato_options.keys()))
                porcentaje = st.slider("Porcentaje", 0, 100, 0)
            
            if st.form_submit_button("Crear Actividad"):
                if descripcion and contrato_seleccionado:
                    max_id = actividades_df['id_actividad'].max() if not actividades_df.empty else 0
                    nueva_actividad = {
                        'id_actividad': max_id + 1,
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

