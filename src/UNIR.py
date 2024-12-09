from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
import configparser
import math


class UNIR:
    meses_numeros = {
        "enero": "01",
        "febrero": "02",
        "marzo": "03",
        "abril": "04",
        "mayo": "05",
        "junio": "06",
        "julio": "07",
        "agosto": "08",
        "septiembre": "09",
        "octubre": "10",
        "noviembre": "11",
        "diciembre": "12",
    }
    def __init__(self, file: str, config_file: str):
        '''
        file: EL NOMBRE DEBE SER "unir-<mes>-<año>.pdf"
        por ejemplo   "unir-enero-2021.pdf" el mes y empresa en minusculas
        '''
        self.__prechecks(Path(file))

        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.__l_neto = int(self.config["salario_neto_UNIR_bbox"]["l"])
        self.__t_neto = int(self.config["salario_neto_UNIR_bbox"]["t"])
        self.__r_neto = int(self.config["salario_neto_UNIR_bbox"]["r"])
        self.__b_neto = int(self.config["salario_neto_UNIR_bbox"]["b"])

        self.__l_bruto = int(self.config["salario_bruto_UNIR_bbox"]["l"])
        self.__t_bruto = int(self.config["salario_bruto_UNIR_bbox"]["t"])
        self.__r_bruto = int(self.config["salario_bruto_UNIR_bbox"]["r"])
        self.__b_bruto = int(self.config["salario_bruto_UNIR_bbox"]["b"])

        self.source_path = Path(file)
        pipeline_options = PdfPipelineOptions(do_table_structure=True)
        pipeline_options.table_structure_options.mode = (
            TableFormerMode.ACCURATE
        )  # use more accurate TableFormer model

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        result = converter.convert(self.source_path)
        self.data = result.document.export_to_dict()

    def __prechecks(self, file):
        file_name = file.name
        assert file_name.endswith(".pdf"), "El archivo no es un PDF"
        assert len(file_name.split('-')) == 3, "El archivo no tiene el formato correcto"
        assert file_name.split('-')[0] == "unir", "El archivo no es de UNIR"
        assert file_name.split('-')[1] in UNIR.meses_numeros.keys(), "El mes no es válido"
        assert file_name.split('-')[2].replace('.pdf','').isdigit(), "El año no es válido"

    @property
    def salario_neto(self: float) -> float:
        return self.extraerSalarioNeto()

    @property
    def salario_bruto(self: float) -> float:
        return self.extraerSalarioBruto()

    @property
    def mes(self):
        return self.extraerMes()

    def extraerSalarioNeto(self):
        resultado = None
        resultado = self.__find_on_texts()
        if resultado is None:
            resultado = self.__find_on_table_cells()
        return resultado

    def __find_on_table_cells(self, l, t, r, b):
        diccionario = self.data["tables"][0]
        for item in diccionario["data"]["table_cells"]:
            for k, v in item.items():
                if k == "bbox":
                    match_count = sum(
                        math.floor(v[key]) == value
                        for key, value in zip(["l", "t", "r", "b"], [l, t, r, b])
                    )
                    if match_count >= 3:
                        return float(
                            item["text"].replace(".", "").replace(",", ".").split()[0]
                        )
        return None

    def __find_on_texts(self, l, t, r, b):
        for item in self.data["texts"]:
            for _, v in item.items():
                if isinstance(v, list) and len(v) > 0:
                    match_count = sum(
                        math.floor(v[0]["bbox"][key]) == value
                        for key, value in zip(["l", "t", "r", "b"], [l, t, r, b])
                    )
                    if match_count >= 3:
                        return float(
                            item["text"].replace(".", "").replace(",", ".").split()[0]
                        )
        return None

    def extraerSalarioNeto(self):
        resultado = self.__find_on_texts(
            self.__l_neto, self.__t_neto, self.__r_neto, self.__b_neto
        )
        if resultado is None:
            resultado = self.__find_on_table_cells(
                self.__l_neto, self.__t_neto, self.__r_neto, self.__b_neto
            )
        return resultado

    def extraerSalarioBruto(self):
        resultado = self.__find_on_texts(
            self.__l_bruto, self.__t_bruto, self.__r_bruto, self.__b_bruto
        )
        if resultado is None:
            resultado = self.__find_on_table_cells(
                self.__l_bruto, self.__t_bruto, self.__r_bruto, self.__b_bruto
            )
        return resultado
        

    def extraerMes(self):
        import re

        pattern = r"'text':\s*'(\d{2})/(\d{2})/(\d{4})\s+(\d{2})/(\d{2})/(\d{4})\s*-\s*PERIODO\s+LIQUIDACION"
        found = re.search(pattern, str(self.data))

        if found:
            # Extracting the first date
            first_day = found.group(1)
            first_month = found.group(2)
            first_year = found.group(3)

            return f"{first_day}-{first_month}-{first_year}"
        else:
            value = self.source_path.stem.split("-")
            return f"01-{UNIR.meses_numeros.get(value[1])}-{value[2]}"

    def export_to_json(self):
        import json
        import random

        with open(
            f"unir_data{self.source_path.stem}{random.random()}.json", "w"
        ) as json_file:
            json.dump(self.data, json_file)
