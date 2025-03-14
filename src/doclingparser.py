from src.UNIR import UNIR
from src.UST import UST
from src.aux_functions import generar_hash_archivo
import pandas as pd
from pathlib import Path
import os


def parse_nomina(nomina_path: str) -> pd.DataFrame:
    if "unir" in nomina_path.lower():
        nomina_unir = UNIR(nomina_path, config_file="config.ini")
        df = pd.DataFrame(
            {
                "fichero": Path(nomina_path).stem,
                "hash_fichero": generar_hash_archivo(nomina_path),
                "empresa": "UNIR",
                "salario_neto": nomina_unir.salario_neto,
                "salario_bruto": nomina_unir.salario_bruto,
                "mes": nomina_unir.mes,
                "posicion_interna": nomina_unir.posicion_interna,
            },
            index=[0],
        )
        print(df)
        return df

    elif "ust" in nomina_path.lower():
        nomina_ust = UST(nomina_path, config_file="config.ini")
        df = pd.DataFrame(
            {
                "fichero": Path(nomina_path).stem,
                "hash_fichero": generar_hash_archivo(nomina_path),
                "empresa": "UST",
                "salario_neto": nomina_ust.salario_neto,
                "salario_bruto": nomina_ust.salario_bruto,
                "mes": nomina_ust.mes,
                "posicion_interna": nomina_ust.posicion_interna,
                "salario_base": nomina_ust.salario_base,
            },
            index=[0],
        )

        return df
    os.remove(nomina_path)
