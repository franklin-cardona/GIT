import pandas as pd
# from logger import logger
import os
from typing import Optional, Dict, Any, List

# Importar pyodbc de forma opcional
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False
    print("pyodbc no está disponible. Solo se usará Excel como fuente de datos.")


class DatabaseManager:
    def __init__(self, excel_path: str = None):
        self.excel_path = excel_path or "Basedatos.xlsx"
        self.sql_connection = None
        self.use_excel = False

    def connect_to_sql_server(self, server: str = "localhost", database: str = "GAR",
                              username: str = "sa", password: str = "Password123456") -> bool:
        """Intenta conectar a SQL Server"""
        if not PYODBC_AVAILABLE:
            print("pyodbc no está disponible. Usando archivo Excel como fallback")
            # logger.info(
            #     "pyodbc no está disponible. Usando archivo Excel como fallback")
            self.use_excel = True
            return False

        try:
            if username and password:
                connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
            else:
                connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"

            self.sql_connection = pyodbc.connect(connection_string)
            self.use_excel = False
            print("Conexión exitosa a SQL Server")
            # logger.info("Conexión exitosa a SQL Server")
            return True
        except Exception as e:
            print(f"Error conectando a SQL Server: {e}")
            print("Usando archivo Excel como fallback")
            # logger.error(f"Error conectando a SQL Server: {e}")
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
            df = pd.read_sql(query, self.sql_connection)
            return df
        except Exception as e:
            print(f"Error leyendo SQL: {e}")
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
        """Inserta datos en SQL Server"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data.values()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            cursor = self.sql_connection.cursor()
            cursor.execute(query, list(data.values()))
            self.sql_connection.commit()
            return True
        except Exception as e:
            print(f"Error insertando en SQL: {e}")
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
        """Actualiza datos en SQL Server"""
        try:
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"

            cursor = self.sql_connection.cursor()
            cursor.execute(query, list(data.values()))
            self.sql_connection.commit()
            return True
        except Exception as e:
            print(f"Error actualizando en SQL: {e}")
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
        """Elimina datos de SQL Server"""
        try:
            query = f"DELETE FROM {table_name} WHERE {condition}"
            cursor = self.sql_connection.cursor()
            cursor.execute(query)
            self.sql_connection.commit()
            return True
        except Exception as e:
            print(f"Error eliminando en SQL: {e}")
            return False

    def close_connection(self):
        """Cierra la conexión a la base de datos"""
        if self.sql_connection:
            self.sql_connection.close()
