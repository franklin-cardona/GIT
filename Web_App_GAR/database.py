from logger import setup_logging
import streamlit as st
from typing import Optional, Dict, Any, List
import pandas as pd
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import sqlite3

logger = setup_logging()
# Importar pyodbc de forma opcional
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    logger.warning(
        "pyodbc no está disponible. Solo se usará Excel como fuente de datos.")
    st.warning(
        "pyodbc no está disponible. Solo se usará Excel como fuente de datos.")


class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, excel_path: str = "") -> None:
        if self._initialized:
            return
        self.path = excel_path or "Basedatos.xlsx"
        self.use_excel = False
        self.sql_engine = None
        self.sql_lite_connection = None
        self.cursor = None
        logger.info("DatabaseManager inicializado.")
        self._initialized = True

    def connect_to_sql_lite(self, db_path: str = "db_gpc.db") -> bool:
        """Intenta conectar a SQLite"""
        self.path = db_path
        if not os.path.exists(db_path):
            logger.error(f"Archivo SQLite no encontrado: {self.path}")
            st.warning(f"Archivo SQLite no encontrado: {self.path}")
            return False
        try:
            self.sql_lite_connection = sqlite3.connect(self.path)
            with self.sql_lite_connection:
                self.sql_lite_connection.execute("SELECT 1")
                logger.info("Conexión exitosa a SQLite")
                # st.success("Conexión exitosa a SQLite")
                self.use_excel = False
                self.sql_engine = None
                return True
        except Exception as e:
            logger.error(f"Error conectando a SQLite: {e}")
            st.error(f"Error conectando a SQLite: {e}")
            self.sql_lite_connection = None
            self.cursor = None
            return False

    def connect_to_sql_server(
        self,
        server: str = "P18PPAD20\\SQLEXPRESS",
        database: str = "db_gpc",
        port: Optional[int] = 1433,
        username: str = None,
        password: str = None
    ) -> bool:
        """Intenta conectar a SQL Server"""
        logger.info("Intenta conectar a SQL Server")
        if not PYODBC_AVAILABLE:
            st.write(
                "pyodbc no está disponible. Usando archivo Excel como fallback")
            print("pyodbc no está disponible. Usando archivo Excel como fallback")
            logger.info(
                "pyodbc no está disponible. Usando archivo Excel como fallback")
            self.use_excel = True
            return False

        try:

            connection_string = (
                'DRIVER={ODBC Driver 17 for SQL Server};'
                f'SERVER={server};'  # Mantén el formato con doble backslash
                f'DATABASE={database};'
            )

            # Añadir método de autenticación
            if username and password:
                connection_string += f'UID={username};PWD={password};'
            else:
                connection_string += 'Trusted_Connection=yes;'
            logger.info(f"connection_string: {connection_string}")
            print("connection_string:", connection_string)

            # Crear motor SQLAlchemy
            self.sql_engine = create_engine(
                f"mssql+pyodbc:///?odbc_connect={connection_string}",
                pool_size=5,
                max_overflow=10,
                pool_timeout=30
            )

            # Probar la conexión
            with self.sql_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                print("Conexión exitosa a SQL Server usando SQLAlchemy")
                st.write("Conexión exitosa a SQL Server usando SQLAlchemy")
                self.path = "MSSQL Server"
                self.use_excel = False
                return True

        except Exception as e:
            print(f"Error conectando a SQL Server con SQLAlchemy: {e}")
            logger.error(f"Error de conexión: {e}")
            self.sql_engine = None
            return False

    def get_data(self, table_name: str, filters: dict = None, limit: int = None) -> pd.DataFrame:
        """Obtiene datos de la tabla especificada con opciones de filtrado"""
        try:
            if self.use_excel:
                return self._get_data_from_excel(table_name)
            elif self.sql_engine:
                return self._get_data_from_sql(table_name, filters, limit)
            elif self.sql_lite_connection:
                return self._get_data_from_sql_lite(table_name, filters, limit)
            else:
                logger.warning("No hay conexión a base de datos.")
                st.warning("No hay conexión a ninguna base de datos.")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error obteniendo datos: {e}")
            return pd.DataFrame()

    def _get_data_from_excel(self, sheet_name: str) -> pd.DataFrame:
        """Lee datos del archivo Excel"""
        try:
            return pd.read_excel(self.path, sheet_name=sheet_name)
        except Exception as e:
            logger.error(f"Error leyendo Excel: {e}")
            return pd.DataFrame()

    def _get_data_from_sql(self, table_name: str, filters: dict, limit: int) -> pd.DataFrame:
        """Lee datos de SQL Server con filtros opcionales"""
        if not self.sql_engine:
            logger.warning("No hay conexión a SQL Server.")
            return pd.DataFrame()
        try:
            query = f"SELECT * FROM {table_name}"

            if filters:
                conditions = " AND ".join(
                    [f"{k} = '{v}'" for k, v in filters.items()])
                query += f" WHERE {conditions}"

            logger.info(f"Consulta SQL: {query} con filtros {filters}")

            return pd.read_sql(query, self.sql_engine)
        except Exception as e:
            logger.error(f"Error leyendo SQL: {e}")
            return pd.DataFrame()

    def _get_data_from_sql_lite(self, table_name: str, filters: dict, limit: int) -> pd.DataFrame:
        """Lee datos de SQLite con filtros opcionales"""
        if not self.sql_lite_connection:
            logger.warning("No hay conexión a SQLite.")
            return pd.DataFrame()
        try:
            self.connect_to_sql_lite(self.path)
            logger.info(f"Conectado a SQLite en {self.path}")
            self.cursor = self.sql_lite_connection.cursor()
            query = f"SELECT * FROM {table_name}"

            if filters:
                conditions = " AND ".join(
                    [f"{k} = '{v}'" for k, v in filters.items()])
                query += f" WHERE {conditions}"

            if limit:
                query += f" LIMIT {limit}"
            logger.info(
                f"Consulta ejecutada: {query} con parámetros {filters}")
            self.cursor.execute(query)
            logger.info(
                f"Consulta ejecutada en la tabla {table_name} de SQLite")
            # Obtener los datos
            data = self.cursor.fetchall()
            logger.info(
                f"Datos obtenidos de la tabla {table_name} en SQLite [{len(data)} filas]")
            # Leer los resultados y convertirlos a DataFrame
            df = pd.DataFrame(data, columns=[col[0]
                                             for col in self.cursor.description])
            logger.info(
                f"DataFrame creado con {len(df)} filas y {len(df.columns)} columnas")
            self.sql_lite_connection.commit()
            self.cursor.close()

            return df
        except Exception as e:
            logger.error(f"Error leyendo SQLite: {e}")
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
            logger.warning("No hay conexión a ninguna base de datos.")
            st.warning("No hay conexión a ninguna base de datos.")
            return False

    def _insert_data_to_excel(self, sheet_name: str, data: Dict[str, Any]) -> bool:
        """Inserta datos en Excel (simulado - en realidad solo lee)"""
        # Para Excel, solo simulamos la inserción ya que es complejo modificar archivos Excel
        logger.info(
            f"Simulando inserción en Excel - Tabla: {sheet_name}, Datos: {data}")
        return True

    def _insert_data_to_sql(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Inserta datos en SQL Server usando SQLAlchemy"""
        if not self.sql_engine:
            logger.warning("No hay conexión a SQL Server.")
            st.warning("No hay conexión a SQL Server.")
            return False
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join([f"'{v}'" for v in data.values()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            with self.sql_engine.connect() as connection:
                connection.execute(text(query), data)
                connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error insertando en SQL con SQLAlchemy: {e}")
            st.error(f"Error insertando en SQL con SQLAlchemy: {e}")
            return False

    def _insert_data_to_sql_lite(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Inserta datos en SQLite usando SQLAlchemy"""
        if not self.sql_lite_connection:
            logger.warning("No hay conexión a SQLite.")
            st.warning("No hay conexión a SQLite.")
            return False
        try:
            self.connect_to_sql_lite(self.path)
            self.cursor = self.sql_lite_connection.cursor()
            columns = ", ".join(data.keys())
            placeholders = ", ".join([f"'{v}'" for v in data.values()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            logger.info(
                f"Ejecutando consulta SQLite: {query}")

            with self.sql_lite_connection:
                self.cursor.execute(query, data)
                self.sql_lite_connection.commit()
                logger.info(f"Datos insertados en SQLite: {data}")
            self.cursor.close()
            return True
        except Exception as e:
            logger.error(f"Error insertando en SQLite: {e}")
            return False

    def update_data(self, table_name: str, data: Dict[str, Any], condition: Dict[str, Any]) -> bool:
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

    def _update_data_in_excel(self, sheet_name: str, data: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """Actualiza datos en Excel (simulado)"""
        print(
            f"Simulando actualización en Excel - Tabla: {sheet_name}, Datos: {data}, Condición: {condition}")
        return True

    def _update_data_in_sql(self, table_name: str, data: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """Actualiza datos en SQL Server usando SQLAlchemy"""
        if not self.sql_engine:
            print("No hay conexión a SQL Server.")
            st.write("No hay conexión a SQL Server.")
            return False
        try:
            set_clause = ", ".join([f"{k} = '{v}'" for k, v in data.items()])
            logger.info(set_clause)
            condiciones = " AND ".join(
                [f"{k} = '{v}'" for k, v in condition.items()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condiciones}"
            logger.info(query)

            with self.sql_engine.connect() as connection:
                connection.execute(text(query), data)
                connection.commit()
            return True
        except Exception as e:
            print(f"Error actualizando en SQL con SQLAlchemy: {e}")
            return False

    def _update_data_sql_lite(self, table_name: str, data: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """Actualiza datos en SQLite usando SQLAlchemy"""
        if not self.sql_lite_connection:
            print("No hay conexión a SQLite.")
            st.write("No hay conexión a SQLite.")
            return False
        try:
            self.connect_to_sql_lite(self.path)
            logger.info(f"Conectado a SQLite en {self.path}")
            self.cursor = self.sql_lite_connection.cursor()
            set_clause = ", ".join([f"{k} = '{v}'" for k, v in data.items()])
            condiciones = " AND ".join(
                [f"{k} = '{v}'" for k, v in condition.items()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condiciones}"
            logger.info(query)

            with self.sql_lite_connection:
                self.cursor.execute(query)
                self.cursor.connection.commit()
                self.cursor.close()
            return True
        except Exception as e:
            logger.info(f"Error actualizando en SQLite: {e}")
            return False

    def delete_data(self, table_name: str, condition: Dict[str, Any]) -> bool:
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

    def _delete_data_from_excel(self, sheet_name: str, condition: Dict[str, Any]) -> bool:
        """Elimina datos de Excel (simulado)"""
        print(
            f"Simulando eliminación en Excel - Tabla: {sheet_name}, Condición: {condition}")
        return True

    def _delete_data_from_sql_lite(self, table_name: str, condition: Dict[str, Any]) -> bool:
        """Elimina datos de SQLite usando SQLAlchemy"""
        if not self.sql_lite_connection:
            print("No hay conexión a SQLite.")
            st.write("No hay conexión a SQLite.")
            return False
        try:
            self.connect_to_sql_lite(self.path)
            self.cursor = self.sql_lite_connection.cursor()
            condiciones = " AND ".join(
                [f"{k} = '{v}'" for k, v in condition.items()])
            query = f"DELETE FROM {table_name} WHERE {condiciones}"
            logger.info(query)
            with self.sql_lite_connection:
                self.cursor.execute(query)
                self.sql_lite_connection.commit()
                self.cursor.close()
            return True
        except Exception as e:
            print(f"Error eliminando en SQLite: {e}")
            return False

    def _delete_data_from_sql(self, table_name: str, condition: Dict[str, Any]) -> bool:
        """Elimina datos de SQL Server usando SQLAlchemy"""
        if not self.sql_engine:
            print("No hay conexión a SQL Server.")
            st.write("No hay conexión a SQL Server.")
            return False
        try:
            condiciones = " AND ".join(
                [f"{k} = '{v}'" for k, v in condition.items()])
            query = f"DELETE FROM {table_name} WHERE {condiciones}"
            logger.info(query)
            with self.sql_engine.connect() as connection:
                connection.execute(text(query))
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
            if self.cursor:
                self.cursor.close()
            self.sql_lite_connection.close()
        logger.info("Conexiones cerradas.")

    def __del__(self):
        """Asegura que la conexión se cierre al eliminar la instancia"""
        self.close_connection()
