from src.UNIR import UNIR
from src.UST import UST
from src.aux_functions import list_files_recursive, generar_hash_archivo
import pandas as pd
import os


def main():
    source_path = "/mnt/c/Users/anton/OneDrive/Escritorio/nominas"
    excel_file = "nominas.xlsx"

    # Intenta cargar el DataFrame desde el archivo Excel si existe
    if os.path.exists(excel_file):
        print("Loading existing data...")
        dataframe = pd.read_excel(excel_file)
    else:
        print("Creating new DataFrame...")
        dataframe = pd.DataFrame(
            columns=[
                "Fichero",
                "Hash",
                "Empresa",
                "salario_neto",
                "salario_bruto",
                "mes",
                "Tipo",
            ]
        )

    existing_hashes = set(dataframe["Hash"])

    for i, nomina in enumerate(list_files_recursive(source_path, [".pdf"])):
        print("*" * 40)
        nomina_str = str(nomina)
        file_hash = generar_hash_archivo(nomina_str)

        # Si el hash ya existe y no se fuerza la actualización, no analizar el fichero
        if file_hash in existing_hashes:
            print(f"Skipping {nomina_str}, hash already exists.")
            continue

        if "unir" in nomina_str:
            print("analyzing: ", nomina_str)
            nomina_unir = UNIR(nomina_str, config_file="config.ini")
            new_df = pd.DataFrame(
                {
                    "Fichero": nomina.stem,
                    "Hash": file_hash,
                    "Empresa": "UNIR",
                    "salario_neto": nomina_unir.salario_neto,
                    "salario_bruto": nomina_unir.salario_bruto,
                    "mes": nomina_unir.mes,
                    "Tipo": "Nomina",
                },
                index=[0],
            )
            dataframe = pd.concat([dataframe, new_df])

        if "ust" in nomina_str:
            print("analyzing: ", nomina_str)
            nomina_ust = UST(nomina, config_file="config.ini")
            new_df = pd.DataFrame(
                {
                    "Fichero": nomina.stem,
                    "Hash": file_hash,
                    "Empresa": "UST",
                    "salario_neto": nomina_ust.salario_neto,
                    "salario_bruto": nomina_ust.salario_bruto,
                    "mes": nomina_ust.mes,
                    "Tipo": "Nomina",
                },
                index=[0],
            )
            dataframe = pd.concat([dataframe, new_df])

        # Save the updated DataFrame to the Excel file
        dataframe.to_excel(excel_file, index=False)


if __name__ == "__main__":
    main()
