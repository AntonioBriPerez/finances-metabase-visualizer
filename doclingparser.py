from src.UNIR import UNIR
from src.UST import UST
from src.aux_functions import list_files_recursive


def main():
    source_path = "/mnt/c/Users/anton/OneDrive/Escritorio/nominas"
    for nomina in list_files_recursive(source_path, [".pdf"]):
        print("*" * 40)
        nomina_str = str(nomina)
        # if "unir" in nomina_str:
        #     print("analyzing: ", nomina_str)
        #     nomina_unir = UNIR(nomina_str)
        #     print("salario neto: ", nomina_unir.salario_neto)
        #     print("salario bruto: ", nomina_unir.salario_bruto)
        #     print("mes: ", nomina_unir.mes)
        #     nomina_unir.export_to_json()
        if "ust" in nomina_str:
            nomina_ust = UST(nomina, config_file="config.ini")
            print("analyzing: ", nomina_str)
            # print("salario neto: ", nomina_ust.salario_neto)
            # print("salario bruto: ", nomina_ust.salario_bruto)
            print("mes: ", nomina_ust.mes)
            nomina_ust.export_to_json()


if __name__ == "__main__":
    main()
