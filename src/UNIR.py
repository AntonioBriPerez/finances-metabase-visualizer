from pathlib import Path
from .BoundingBox import BoundingBox
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
import configparser
import math
import os

os.environ["TQDM_DISABLE"] = "1"


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
        """
        file: EL NOMBRE DEBE SER "unir-<mes>-<año>.pdf"
        por ejemplo   "unir-enero-2021.pdf" el mes y empresa en minusculas
        """
        self.__prechecks(Path(file))

        self.config = configparser.ConfigParser()
        self.config.read(config_file)

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
        try:
            assert file_name.endswith(".pdf"), f"El archivo {file_name} no es un PDF"
            assert (
                len(file_name.split("-")) == 3
            ), f"El archivo {file_name} no tiene el formato correcto"
            assert (
                file_name.split("-")[0] == "unir"
            ), f"El archivo {file_name} no es de UNIR"
            assert (
                file_name.split("-")[1] in UNIR.meses_numeros.keys()
            ), "El mes no es válido"
            assert (
                file_name.split("-")[2].replace(".pdf", "").isdigit()
            ), "El año no es válido"
        except AssertionError as e:
            raise AssertionError(e)

    @property
    def posicion_interna(self) -> str:
        return self.extraerPosicionInterna()

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
        resultado = self.__find_on_texts(
            BoundingBox(self.config["salario_neto_UNIR_bbox"])
        )
        if resultado is None:
            resultado = self.__find_on_table_cells(
                BoundingBox(self.config["salario_neto_UNIR_bbox"])
            )
        return resultado

    def __find_on_table_cells(self, bbox: BoundingBox):
        l, t, r, b = (
            bbox.l,
            bbox.t,
            bbox.r,
            bbox.b,
        )
        diccionario = self.data["tables"][0]
        for item in diccionario["data"]["table_cells"]:
            for k, v in item.items():
                if k == "bbox":
                    match_count = sum(
                        math.floor(v[key]) == value
                        for key, value in zip(["l", "t", "r", "b"], [l, t, r, b])
                    )
                    if match_count >= 3:
                        return item["text"]

        return None

    def __find_on_texts(self, bbox: BoundingBox):
        l, t, r, b = (
            bbox.l,
            bbox.t,
            bbox.r,
            bbox.b,
        )
        for item in self.data["texts"]:
            for _, v in item.items():
                if isinstance(v, list) and len(v) > 0:
                    match_count = sum(
                        math.floor(v[0]["bbox"][key]) == value
                        for key, value in zip(["l", "t", "r", "b"], [l, t, r, b])
                    )
                    if match_count >= 3:
                        return item["text"]

        return None

    def extraerPosicionInterna(self):
        resultado = self.__find_on_texts(
            BoundingBox(self.config["posicion_interna_UNIR_bbox"])
        )
        if resultado is None:
            resultado = self.__find_on_table_cells(
                BoundingBox(self.config["posicion_interna_UNIR_bbox"])
            )
        return resultado

    def extraerSalarioNeto(self):
        resultado = self.__find_on_texts(
            BoundingBox(self.config["salario_neto_UNIR_bbox"])
        )
        if resultado is None:
            return float(
                self.__find_on_table_cells(
                    BoundingBox(self.config["salario_neto_UNIR_bbox"])
                )
                .replace(".", "")
                .replace(",", ".")
                .split()[0]
            )
        return float(resultado.replace(".", "").replace(",", ".").split()[0])

    def extraerSalarioBruto(self):
        resultado = self.__find_on_texts(
            BoundingBox(self.config["salario_bruto_UNIR_bbox"])
        )
        if resultado is None:
            return float(
                self.__find_on_table_cells(
                    BoundingBox(self.config["salario_bruto_UNIR_bbox"])
                )
                .replace(".", "")
                .replace(",", ".")
                .split()[0]
            )
        # if resultado is float
        if isinstance(resultado, float):
            return resultado
        return float(resultado.replace(".", "").replace(",", ".").split()[0])

    def extraerMes(self):
        import re

        pattern = r"'text':\s*'(\d{2})/(\d{2})/(\d{4})\s+(\d{2})/(\d{2})/(\d{4})\s*-\s*PERIODO\s+LIQUIDACION"
        found = re.search(pattern, str(self.data))

        if found:
            # Extracting the first date
            first_day = found.group(1)
            first_month = found.group(2)
            first_year = found.group(3)

            return f"{first_year} {first_month} {first_day}"
        else:
            value = self.source_path.stem.split("-")
            return f"{value[2]} {UNIR.meses_numeros.get(value[1])} 01"

    def export_to_json(self):
        import json
        import random

        with open(
            f"unir_data{self.source_path.stem}{random.random()}.json", "w"
        ) as json_file:
            json.dump(self.data, json_file)
