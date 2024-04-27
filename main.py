from PyPDF2 import PdfReader
import re
keys = {"salario_base": "SALARIO BASE",
        "plus_convenio": "PLUS CONVENIO",
        "mejora_absorvible": "MEJORA VOLUNTARIA ABSORBIBLE",
        "base de cotizacion": "base_cotizacion",
        "comp_teletrabajo": "COMPENSACION TELETRABAJO",
        "p.extra.dic": "P.EXTRA DICIEM",
        "p.extra.jul": "P.EXTRA JULIO",
        "seguro_accidente":"SEGURO ACCIDENTE LABORAL"}

def extract_numbers(text):
    # Regular expression to match both integer and floating-point numbers in European format
    pattern = r'[-+]?\d{1,3}(?:\.\d{3})*(?:,\d+)?(?:\.\d+)?'
    return re.findall(pattern, text)
def remove_non_letters_and_whitespace(text):
    return re.sub(r'[^a-zA-Z\s]', '', text).strip()
def get_income(text):
    income_dict = {}
    for t in text.split("\n"):
        # todos los ingresos comienzan por uno, y solo un * en la nomina
        idx = t.find("*")
        if idx != -1 and t[0] != "*": #comprobamos que solo es un *
            if any(k in t for k in keys.values()): # para todas las lineas que contengan las keys de conceptos de ingresos
                #actualizamos diccionario con el concepto y el valor
                income_dict.update({remove_non_letters_and_whitespace(t[idx+1:]):extract_numbers(t[idx+1:])})
    return income_dict

def get_deduciones(text):
    print(text)
def get_data(pdf_path):
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    text = page.extract_text()
    income = get_income(text)
    deducciones = get_deduciones(text)


def main():
    get_data("./nominas/ene-2023.pdf")

if __name__ == '__main__':
    main()