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
    def __init__(self, excel_path: str = "") -> None:
        self.path = excel_path or "Basedatos.xlsx"
        self.use_excel = False
        self.sql_engine = None
        self.sql_lite_connection = None
        self.cursor = None
        logger.info("DatabaseManager inicializado.")

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
                st.success("Conexión exitosa a SQLite")
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
        server: str = "LAPTOP-V6LUQTIO\\SQLEXPRESS",
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
            st.write(f"Error de conexión: {e}")
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
            params = {}

            if filters:
                conditions = " AND ".join(
                    [f"{k} = :{k}" for k in filters.keys()])
                query += f" WHERE {conditions}"
                params = filters

            if limit:
                query += f" LIMIT {limit}"

            return pd.read_sql(query, self.sql_engine, params=params)
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
            params = []

            if filters:
                conditions = " AND ".join(
                    [f"{k} = '{v}'" for k, v in filters.items()])
                query += f" WHERE {conditions}"
                # params = list(filters.values())

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

    # ... (resto de métodos con logging similar) ...

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
