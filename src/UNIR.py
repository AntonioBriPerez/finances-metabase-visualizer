import pandas as pd
from .aux_functions import transform_date
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode


class UNIR:
    def __init__(self, file: str, config_file: str):
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
        # using regex search for string "LiQUIDO TOTAL A PERCIBIR" and return the whole line
        import re

        pattern = r"(?:'orig'|'text'):\s*['\"]([\d,\.]+)\s*(?:€|\\u20ac)\s*LiQUIDO TOTAL A PERCIBIR"

        found = re.search(pattern, str(self.data))
        if found:
            return float(found.group(1).replace(",", "."))
        else:
            print("No se ha encontrado el salario neto")

    def extraerMes(self):
        import re

        pattern = r"'text':\s*'(\d{2})/(\d{2})/(\d{4})\s+(\d{2})/(\d{2})/(\d{4})\s*-\s*PERIODO\s+LIQUIDACION"
        found = re.search(pattern, str(self.data))

        if found:
            # Extracting the first date
            first_day = found.group(1)
            first_month = found.group(2)
            first_year = found.group(3)

            return transform_date(f"{first_day}/{first_month}/{first_year}")
        else:
            return self.source_path.stem

    def extraerSalarioBruto(self):
        import re

        pattern_dase = r"'text':\s*'([\d,\.]+)\s*DASE\sLRPF"
        pattern_000 = r"'text':\s*'([\d,\.]+)\s*0,00"

        # First try DASE LRPF
        found = re.search(pattern_dase, str(self.data))
        if found:
            amount_str = found.group(1)
        else:
            # If not found, try 0,00
            found = re.search(pattern_000, str(self.data))
            if found:
                amount_str = found.group(1)
            else:
                amount_str = None

        if amount_str is not None:
            return float(amount_str.replace(",", "."))

        else:
            print("No match found")

    def convert_to_pd(self):
        pass

    def export_to_json(self):
        import json
        import random

        with open(
            f"unir_data{self.source_path.stem}{random.random()}.json", "w"
        ) as json_file:
            json.dump(self.data, json_file)
