
import pandas as pd

excel_file = '/home/ubuntu/upload/Basedatos.xlsx'

def analyze_excel(file_path):
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    print(f"Hojas encontradas: {sheet_names}")

    for sheet_name in sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        print(f"\n--- Contenido de la hoja: {sheet_name} ---")
        print(df.head())

analyze_excel(excel_file)


