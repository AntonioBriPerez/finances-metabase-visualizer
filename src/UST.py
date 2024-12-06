import pandas as pd
from .aux_functions import transform_date, convertir_fecha
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
import math
import configparser


class UST:
    def __init__(self, file: str, config_file: str):
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
        for item in self.data["texts"]:
            for k, v in item.items():
                if (isinstance(v, list)) and len(v) > 0:
                    if (
                        math.floor(v[0]["bbox"]["l"])
                        == int(self.config["salario_neto_UST_bbox"]["l"])
                        and math.floor(v[0]["bbox"]["t"])
                        == int(self.config["salario_neto_UST_bbox"]["t"])
                        and math.floor(v[0]["bbox"]["r"])
                        == int(self.config["salario_neto_UST_bbox"]["r"])
                        and math.floor(v[0]["bbox"]["b"])
                        == int(self.config["salario_neto_UST_bbox"]["b"])
                    ):
                        return float(item["text"].replace(".", "").replace(",", "."))

    def extraerSalarioBruto(self):
        diccionario = self.data["tables"][0]
        for item in diccionario["data"]["table_cells"]:
            for k, v in item.items():
                if k == "bbox":
                    if (
                        math.floor(v["l"])
                        == int(self.config["salario_bruto_UST_bbox"]["l"])
                        and math.floor(v["t"])
                        == int(self.config["salario_bruto_UST_bbox"]["t"])
                        and math.floor(v["r"])
                        == int(self.config["salario_bruto_UST_bbox"]["r"])
                        and math.floor(v["b"])
                        == int(self.config["salario_bruto_UST_bbox"]["b"])
                    ):
                        return float(item["text"].replace(".", "").replace(",", "."))

    def extraerMes(self):
        import re
        string_data = str(self.data)
        patron = r'Mensual - (\d{1,2}) (\w+) (\d{4}) a (\d{1,2}) (\w+) (\d{4})'

        # Buscar el patrón en la cadena
        coincidencia = re.search(patron, string_data)

        # Comprobar si se ha encontrado la coincidencia
        if coincidencia:
            dia_fin = coincidencia.group(4)
            mes_fin = coincidencia.group(5)
            año_fin = coincidencia.group(6)
                # Imprimir el resultado
            return convertir_fecha(f"{dia_fin} {mes_fin} {año_fin}")

    def convert_to_pd():
        pass

    def export_to_json(self):
        import json
        import random

        with open(
            f"ust_data{self.source_path.stem}{random.random()}.json", "w"
        ) as json_file:
            json.dump(self.data, json_file)
