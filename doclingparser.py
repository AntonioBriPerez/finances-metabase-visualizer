from src.UNIR import UNIR
from src.UST import UST
from src.aux_functions import list_files_recursive, generar_hash_archivo
import pandas as pd
from pathlib import Path

def parse_nomina(nomina_path: str) -> pd.DataFrame:
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

    print("analyzing: ", nomina_path)
    if "unir" in nomina_path.lower():
        nomina_unir = UNIR(nomina_path, config_file="config.ini")
        new_df = pd.DataFrame(
            {
                "Fichero": Path(nomina_path).stem,
                "Hash": generar_hash_archivo(nomina_path),
                "Empresa": "UNIR",
                "salario_neto": nomina_unir.salario_neto,
                "salario_bruto": nomina_unir.salario_bruto,
                "mes": nomina_unir.mes,
                "Tipo": "Nomina",
            },
            index=[0],
        )
        dataframe = pd.concat([dataframe, new_df])

    elif "ust" in nomina_path.lower():
        nomina_ust = UST(nomina_path, config_file="config.ini")
        new_df = pd.DataFrame(
            {
                "Fichero": Path(nomina_path).stem,
                "Hash": generar_hash_archivo(nomina_path),
                "Empresa": "UST",
                "salario_neto": nomina_ust.salario_neto,
                "salario_bruto": nomina_ust.salario_bruto,
                "mes": nomina_ust.mes,
                "Tipo": "Nomina",
            },
            index=[0],
        )
        dataframe = pd.concat([dataframe, new_df])
    return dataframe

