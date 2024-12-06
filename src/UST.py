from .INomina import INomina
import pandas as pd
from .aux_functions import transform_date
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

class UST(INomina):
    def __init__(self, file: str):
        self.source_path = Path(file)
        pipeline_options = PdfPipelineOptions(do_table_structure=True)
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE  # use more accurate TableFormer model


        converter = DocumentConverter(
            format_options= {
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
        pass
        
    def extraerSalarioBruto(self):
        pass
    def extraerMes(self):
        pass

    def convert_to_pd():
        pass
    def export_to_json(self):
        import json
        import random
        with open(f'ust_data{self.source_path.stem}{random.random()}.json', 'w') as json_file:
            json.dump(self.data, json_file)