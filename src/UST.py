from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
import math
import configparser


class UST:
    meses_numeros = {
        "Enero": "01",
        "Febrero": "02",
        "Marzo": "03",
        "Abril": "04",
        "Mayo": "05",
        "Junio": "06",
        "Julio": "07",
        "Agosto": "08",
        "Septiembre": "09",
        "Octubre": "10",
        "Noviembre": "11",
        "Diciembre": "12",
    }

    def __init__(self, file: str, config_file: str):
        """
        file: EL NOMBRE DEBE SER "ust-<mes>-<año>.pdf"
        por ejemplo   "ust-enero-2021.pdf" el mes y empresa en minusculas
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
        assert file_name.endswith(".pdf"), "El archivo no es un PDF"
        assert len(file_name.split("-")) == 3, "El archivo no tiene el formato correcto"
        assert file_name.split("-")[0] == "ust", "El archivo no es de UST"
        assert (
            file_name.split("-")[1].capitalize() in UST.meses_numeros.keys()
        ), "El mes no es válido"
        assert (
            file_name.split("-")[2].replace(".pdf", "").isdigit()
        ), "El año no es válido"

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
                if isinstance(v, list) and len(v) > 0:
                    bbox = v[0]["bbox"]
                    match_count = sum(
                        math.floor(bbox[dim])
                        == int(self.config["salario_neto_UST_bbox"][dim])
                        for dim in ["l", "t", "r", "b"]
                    )
                    if match_count >= 3:
                        return float(item["text"].replace(".", "").replace(",", "."))

    def extraerSalarioBruto(self):
        diccionario = self.data["tables"][0]
        for item in diccionario["data"]["table_cells"]:
            bbox = item.get("bbox", {})
            match_count = sum(
                math.floor(bbox.get(dim, -1))
                == int(self.config["salario_bruto_UST_bbox"][dim])
                for dim in ["l", "t", "r", "b"]
            )
            if match_count >= 3:
                return float(item["text"].replace(".", "").replace(",", "."))

    def extraerMes(self):
        import re

        string_data = str(self.data)
        patron = r"Mensual - (\d{1,2}) (\w+) (\d{4}) a (\d{1,2}) (\w+) (\d{4})"

        # Buscar el patrón en la cadena
        coincidencia = re.search(patron, string_data)

        # Comprobar si se ha encontrado la coincidencia
        if coincidencia:
            dia_fin = coincidencia.group(4)
            mes_fin = coincidencia.group(5)
            año_fin = coincidencia.group(6)
            # Imprimir el resultado
            return self.__convertir_fecha(f"{dia_fin} {mes_fin} {año_fin}")

    @staticmethod
    def __convertir_fecha(fecha):
        # Dividir la cadena de fecha por espacio
        partes = fecha.split()

        # El mes es la segunda parte (índice 1) y el año es la tercera parte (índice 2)
        mes = partes[1]
        año = partes[2]

        # Convertir el mes a su abreviatura
        return f"{año}-{UST.meses_numeros.get(mes, "Mes no valido")}-01"

    def convert_to_pd():
        pass

    def export_to_json(self):
        import json
        import random

        with open(
            f"ust_data{self.source_path.stem}{random.random()}.json", "w"
        ) as json_file:
            json.dump(self.data, json_file)
