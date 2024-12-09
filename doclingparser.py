from src.UNIR import UNIR
from src.UST import UST
from src.aux_functions import list_files_recursive, generar_hash_archivo
import pandas as pd
from pathlib import Path
import os


def parse_nomina(nomina_path: str) -> pd.DataFrame:
    print("Creating new DataFrame...")
    dataframe = pd.DataFrame(
        columns=[
            "fichero",
            "hash_fichero",
            "empresa",
            "salario_neto",
            "salario_bruto",
            "mes",
        ]
    )

    print("analyzing: ", nomina_path)
    if "unir" in nomina_path.lower():
        nomina_unir = UNIR(nomina_path, config_file="config.ini")
        new_df = pd.DataFrame(
            {
                "fichero": Path(nomina_path).stem,
                "hash_fichero": generar_hash_archivo(nomina_path),
                "empresa": "UNIR",
                "salario_neto": nomina_unir.salario_neto,
                "salario_bruto": nomina_unir.salario_bruto,
                "mes": nomina_unir.mes,
            },
            index=[0],
        )
        dataframe = pd.concat([dataframe, new_df])

    elif "ust" in nomina_path.lower():
        nomina_ust = UST(nomina_path, config_file="config.ini")
        new_df = pd.DataFrame(
            {
                "fichero": Path(nomina_path).stem,
                "hash_fichero": generar_hash_archivo(nomina_path),
                "empresa": "UST",
                "salario_neto": nomina_ust.salario_neto,
                "salario_bruto": nomina_ust.salario_bruto,
                "mes": nomina_ust.mes,
            },
            index=[0],
        )
        dataframe = pd.concat([dataframe, new_df])
    os.remove(nomina_path)
    return dataframe