import streamlit as st
from typing import Optional, Dict, Any, List
import pandas as pd
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import sqlite3


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
        self.use_excel = False
        self.sql_engine = None
        self.sql_lite_connection = None

    def connect_to_sql_server(self, server: str = "localhost", database: str = "db_gpc", port: Optional[int] = '1433',
                              username: str = "sa", password: str = "Password123456") -> bool:
        """Intenta conectar a SQL Server"""
        if not PYODBC_AVAILABLE:
            st.write(
                "pyodbc no está disponible. Usando archivo Excel como fallback")
            print("pyodbc no está disponible. Usando archivo Excel como fallback")
            # logger.info(
            #     "pyodbc no está disponible. Usando archivo Excel como fallback")
            self.use_excel = True
            return False

        try:
            if username and password:
                # connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
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
                # connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
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

            # st.write("connection_string:", connection_url)
            print("connection_string:", connection_url)

            self.sql_engine = create_engine(connection_url)
            # Probar la conexión
            with self.sql_engine.connect() as connection:
                print(
                    f"Conectando a SQL Server usando SQLAlchemy...{connection}")
                connection.execute(text("SELECT 1"))
                print("Conexión exitosa a SQL Server usando SQLAlchemy")
                st.write("Conexión exitosa a SQL Server usando SQLAlchemy")
                self.use_excel = False
                # logger.info("Conexión exitosa a SQL Server usando SQLAlchemy")
                self.sql_lite_connection = None  # Asegurarse de que no se use
            return True
        except Exception as e:
            print(f"Error conectando a SQL Server con SQLAlchemy: {e}")
            try:
                self.sql_lite_connection = sqlite3.connect("db_gpc.db")
                with self.sql_lite_connection:
                    print("Conectando a SQLite...")
                    self.sql_lite_connection.execute("SELECT 1")
                    print("Conexión exitosa a SQLite")
                    st.write("Conexión exitosa a SQLite")
                    self.use_excel = False
                    self.sql_engine = None
                    # logger.info("Conexión exitosa a SQLite")
                return True
            except Exception as e:
                print(f"Error conectando a SQLite: {e}")
                self.sql_lite_connection = None  # Asegurarse de que no se use
                self.use_excel = True
                self.sql_engine = None
                st.write(
                    "No se pudo conectar a SQL Server ni a SQLite. Usando archivo Excel como fallback.")
                # logger.info("No se pudo conectar a SQL Server ni a SQLite. Usando archivo
                print("Usando archivo Excel como fallback")

            return False

    def get_data(self, table_name: str) -> pd.DataFrame:
        """Obtiene datos de la tabla especificada"""
        if self.use_excel:
            print(f"Obteniendo datos de Excel - Tabla: {table_name}")
            return self._get_data_from_excel(table_name)
        elif self.sql_engine:
            print(f"Obteniendo datos de SQL Server - Tabla: {table_name}")
            return self._get_data_from_sql(table_name)
        elif self.sql_lite_connection:
            print(f"Obteniendo datos de SQLite - Tabla: {table_name}")
            return self.get_data_from_sql_lite(table_name)
        else:
            print("No hay conexión a ninguna base de datos.")
            st.write("No hay conexión a ninguna base de datos.")
            return pd.DataFrame()

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
            # st.write(f"Ejecutando consulta SQL: {query}")
            # st.write(f"Conexión SQL: {self.sql_connection}")
            df = pd.read_sql(query, self.sql_engine)
            return df
        except Exception as e:
            print(f"Error leyendo SQL con SQLAlchemy: {e}")
            return pd.DataFrame()

    def get_data_from_sql_lite(self, table_name: str) -> pd.DataFrame:
        """Lee datos de SQLite"""
        try:
            with self.sql_lite_connection:
                print(
                    f"Conectando a SQLite para leer datos de la tabla: {table_name}")
                query = f"SELECT * FROM {table_name}"
                print(
                    f"Ejecutando consulta SQLite: {query} en {self.sql_lite_connection}")
                df = pd.read_sql_query(query, self.sql_lite_connection)
                return df
        except Exception as e:
            print(f"Error leyendo SQLite: {e}")
            return pd.DataFrame()

    def insert_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Inserta datos en la tabla especificada"""
        if self.use_excel:
            return self._insert_data_to_excel(table_name, data)
        elif self.sql_engine:
            return self._insert_data_to_sql(table_name, data)
        elif self.sql_lite_connection:
            return self._insert_data_to_sql_lite(table_name, data)
        else:
            print("No hay conexión a ninguna base de datos.")
            st.write("No hay conexión a ninguna base de datos.")
            return False

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

    def _insert_data_to_sql_lite(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Inserta datos en SQLite usando SQLAlchemy"""
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join([f":{key}" for key in data.keys()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            with self.sql_lite_connection:
                self.sql_lite_connection.execute(query, data)
            return True
        except Exception as e:
            print(f"Error insertando en SQLite: {e}")
            return False

    def update_data(self, table_name: str, data: Dict[str, Any], condition: str) -> bool:
        """Actualiza datos en la tabla especificada"""
        if self.use_excel:
            return self._update_data_in_excel(table_name, data, condition)
        elif self.sql_engine:
            return self._update_data_in_sql(table_name, data, condition)
        elif self.sql_lite_connection:
            return self._update_data_sql_lite(table_name, data, condition)
        else:
            print("No hay conexión a ninguna base de datos.")
            st.write("No hay conexión a ninguna base de datos.")
            return False

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

    def _update_data_sql_lite(self, table_name: str, data: Dict[str, Any], condition: str) -> bool:
        """Actualiza datos en SQLite usando SQLAlchemy"""
        try:
            set_clause = ", ".join([f"{key} = :{key}" for key in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"

            with self.sql_lite_connection:
                self.sql_lite_connection.execute(query, data)
            return True
        except Exception as e:
            print(f"Error actualizando en SQLite: {e}")
            return False

    def delete_data(self, table_name: str, condition: str) -> bool:
        """Elimina datos de la tabla especificada"""
        if self.use_excel:
            return self._delete_data_from_excel(table_name, condition)
        elif self.sql_engine:
            return self._delete_data_from_sql(table_name, condition)
        elif self.sql_lite_connection:
            return self._delete_data_from_sql_lite(table_name, condition)
        else:
            print("No hay conexión a ninguna base de datos.")
            st.write("No hay conexión a ninguna base de datos.")
            return False

    def _delete_data_from_excel(self, sheet_name: str, condition: str) -> bool:
        """Elimina datos de Excel (simulado)"""
        print(
            f"Simulando eliminación en Excel - Tabla: {sheet_name}, Condición: {condition}")
        return True

    def _delete_data_from_sql_lite(self, table_name: str, condition: str) -> bool:
        """Elimina datos de SQLite usando SQLAlchemy"""
        try:
            query = f"DELETE FROM {table_name} WHERE {condition}"
            with self.sql_lite_connection:
                self.sql_lite_connection.execute(query)
            return True
        except Exception as e:
            print(f"Error eliminando en SQLite: {e}")
            return False

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
        if hasattr(self, 'sql_lite_connection') and self.sql_lite_connection:
            self.sql_lite_connection.close()

    def __del__(self):
        """Asegura que la conexión se cierre al eliminar la instancia"""
        self.close_connection()
        print("Conexión cerrada correctamente.")
        # logger.info("Conexión cerrada correctamente.")
