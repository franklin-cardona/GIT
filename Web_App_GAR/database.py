import streamlit as st
from typing import Optional, Dict, Any, List
import pandas as pd
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# Importar pyodbc de forma opcional
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    print("pyodbc no está disponible. Solo se usará Excel como fuente de datos.")
    st.write("pyodbc no está disponible. Solo se usará Excel como fuente de datos.")


class DatabaseManager:
    def __init__(self, excel_path: str = None):
        self.excel_path = excel_path or "Basedatos.xlsx"
        self.sql_connection = None
        self.use_excel = False

    def connect_to_sql_server(self, server: str = "localhost", database: str = "db_gpc", port: Optional[int] = '1433',
                              username: str = "sa", password: str = "Password123456") -> bool:
        """Intenta conectar a SQL Server"""
        if not PYODBC_AVAILABLE:
            st.write("pyodbc no está disponible. Usando archivo Excel como fallback")
            print("pyodbc no está disponible. Usando archivo Excel como fallback")
            # logger.info(
            #     "pyodbc no está disponible. Usando archivo Excel como fallback")
            self.use_excel = True
            return False

        try:
            if username and password:
                #connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
                connection_url = URL.create(
                    'mssql+pyodbc',
                    username=username,
                    password=password,
                    host=server,
                    port=port,
                    database=database,
                    query={"driver": "ODBC Driver 17 for SQL Server"}
                )
            else:
                #connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
                # Para autenticación de Windows (Trusted_Connection)
                connection_url = URL.create(
                    'mssql+pyodbc',
                    host=server,
                    port=port,
                    database=database,
                    query={
                        "driver": "ODBC Driver 17 for SQL Server",
                        "Trusted_Connection": "yes"
                    }
                )
            
            st.write("connection_string:", connection_url)
            print("connection_string:", connection_url)

            self.sql_engine = create_engine(connection_url)
            # Probar la conexión
            with self.sql_engine.connect() as connection:
                print(f"Conectando a SQL Server usando SQLAlchemy...{connection}")
                connection.execute(text("SELECT 1"))

            #print(f"Conexión exitosa a SQL Server {self.sql_connection}" if self.sql_connection else "No se pudo conectar a SQL Server")
            #st.write(f"Conexión exitosa a SQL Server {self.sql_connection}" if self.sql_connection else "No se pudo conectar a SQL Server")
            # logger.info("Conexión exitosa a SQL Server")
            self.use_excel = False
            print("Conexión exitosa a SQL Server usando SQLAlchemy")
            return True
        except Exception as e:
            print(f"Error conectando a SQL Server con SQLAlchemy: {e}")
            print("Usando archivo Excel como fallback")
            self.use_excel = True
            return False

    def get_data(self, table_name: str) -> pd.DataFrame:
        """Obtiene datos de la tabla especificada"""
        if self.use_excel:
            return self._get_data_from_excel(table_name)
        else:
            return self._get_data_from_sql(table_name)

    def _get_data_from_excel(self, sheet_name: str) -> pd.DataFrame:
        """Lee datos del archivo Excel"""
        try:
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            return df
        except Exception as e:
            print(f"Error leyendo Excel: {e}")
            return pd.DataFrame()

    def _get_data_from_sql(self, table_name: str) -> pd.DataFrame:
        """Lee datos de SQL Server"""
        try:
            query = f"SELECT * FROM {table_name}"
            #st.write(f"Ejecutando consulta SQL: {query}")
            #st.write(f"Conexión SQL: {self.sql_connection}")
            df = pd.read_sql(query, self.sql_engine)
            return df
        except Exception as e:
            print(f"Error leyendo SQL con SQLAlchemy: {e}")
            return pd.DataFrame()

    def insert_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Inserta datos en la tabla especificada"""
        if self.use_excel:
            return self._insert_data_to_excel(table_name, data)
        else:
            return self._insert_data_to_sql(table_name, data)

    def _insert_data_to_excel(self, sheet_name: str, data: Dict[str, Any]) -> bool:
        """Inserta datos en Excel (simulado - en realidad solo lee)"""
        # Para Excel, solo simulamos la inserción ya que es complejo modificar archivos Excel
        print(
            f"Simulando inserción en Excel - Tabla: {sheet_name}, Datos: {data}")
        return True

    def _insert_data_to_sql(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Inserta datos en SQL Server usando SQLAlchemy"""
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join([f":{key}" for key in data.keys()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            with self.sql_engine.connect() as connection:
                connection.execute(query, data)
                connection.commit()
            return True
        except Exception as e:
            print(f"Error insertando en SQL con SQLAlchemy: {e}")
            return False

    def update_data(self, table_name: str, data: Dict[str, Any], condition: str) -> bool:
        """Actualiza datos en la tabla especificada"""
        if self.use_excel:
            return self._update_data_in_excel(table_name, data, condition)
        else:
            return self._update_data_in_sql(table_name, data, condition)

    def _update_data_in_excel(self, sheet_name: str, data: Dict[str, Any], condition: str) -> bool:
        """Actualiza datos en Excel (simulado)"""
        print(
            f"Simulando actualización en Excel - Tabla: {sheet_name}, Datos: {data}, Condición: {condition}")
        return True

    
    def _update_data_in_sql(self, table_name: str, data: Dict[str, Any], condition: str) -> bool:
        """Actualiza datos en SQL Server usando SQLAlchemy"""
        try:
            set_clause = ", ".join([f"{key} = :{key}" for key in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
            
            with self.sql_engine.connect() as connection:
                connection.execute(query, data)
                connection.commit()
            return True
        except Exception as e:
            print(f"Error actualizando en SQL con SQLAlchemy: {e}")
            return False

    def delete_data(self, table_name: str, condition: str) -> bool:
        """Elimina datos de la tabla especificada"""
        if self.use_excel:
            return self._delete_data_from_excel(table_name, condition)
        else:
            return self._delete_data_from_sql(table_name, condition)

    def _delete_data_from_excel(self, sheet_name: str, condition: str) -> bool:
        """Elimina datos de Excel (simulado)"""
        print(
            f"Simulando eliminación en Excel - Tabla: {sheet_name}, Condición: {condition}")
        return True

    def _delete_data_from_sql(self, table_name: str, condition: str) -> bool:
        """Elimina datos de SQL Server usando SQLAlchemy"""
        try:
            query = f"DELETE FROM {table_name} WHERE {condition}"
            with self.sql_engine.connect() as connection:
                connection.execute(query)
                connection.commit()
            return True
        except Exception as e:
            print(f"Error eliminando en SQL con SQLAlchemy: {e}")
            return False

    def close_connection(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self, 'sql_engine') and self.sql_engine:
            self.sql_engine.dispose()
