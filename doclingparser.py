from src.UNIR import UNIR
from src.UST import UST
from src.aux_functions import list_files_recursive
import pandas as pd


def main():
    source_path = "/mnt/c/Users/anton/OneDrive/Escritorio/nominas"
    dataframe = pd.DataFrame(
        columns=["Fichero", "Empresa", "salario_neto", "salario_bruto", "mes"]
    )
    for i, nomina in enumerate(list_files_recursive(source_path, [".pdf"])):
        print("*" * 40)
        nomina_str = str(nomina)
        if "unir" in nomina_str:
            print("analyzing: ", nomina_str)
            nomina_unir = UNIR(nomina_str, config_file="config.ini")
            dataframe.loc[i] = [
                nomina.stem,
                "UNIR",
                nomina_unir.salario_neto,
                nomina_unir.salario_bruto,
                nomina_unir.mes,
            ]

        if "ust" in nomina_str:
            nomina_ust = UST(nomina, config_file="config.ini")
            dataframe.loc[i] = [
                nomina.stem,
                "UST",
                nomina_ust.salario_neto,
                nomina_ust.salario_bruto,
                nomina_ust.mes,
            ]
        if i == 10:
            break
    print(dataframe)


if __name__ == "__main__":
    main()
