import csv
from PyPDF2 import PdfReader
import re
keys = {"salario_base": "SALARIO BASE",
        "plus_convenio": "PLUS CONVENIO",
        "mejora_absorbible": "MEJORA VOLUNTARIA ABSORBIBLE",
        "base de cotizacion": "base_cotizacion",
        "comp_teletrabajo": "COMPENSACION TELETRABAJO",
        "p.extra.dic": "P.EXTRA DICIEM",
        "p.extra.jul": "P.EXTRA JULIO",
        "seguro_accidente":"SEGURO ACCIDENTE LABORAL",
        "plus_seguro_medico_tributa": "PLUS SEGURO MEDICO - TRIBUTA",
        "plus_seguro_medico_no_tributa": "PLUS SEGURO MEDICO SANITAS",
        "intervenciones": "INTERVENCIONES",
        "seguro_vida": "SEGURO VIDA"
        }

def extract_numbers(text):
    # Regular expression to match both integer and floating-point numbers in European format
    pattern = r'[-+]?\d{1,3}(?:\.\d{3})*(?:,\d+)?(?:\.\d+)?'
    ocurrences = re.findall(pattern, text)
    return ocurrences
def remove_non_letters_and_whitespace(text):
    return re.sub(r'[^a-zA-Z]', '', text).lower()

def remove_dots(s):
    # Eliminar puntos
    s_no_dots = s.replace('.', '')
    # Reemplazar coma por punto
    s_comma_to_dot = s_no_dots.replace(',', '.')
    # Convertir a float
    return float(s_comma_to_dot)

def get_income(text) -> dict:
    income_dict = {}
    lines = iter(text.split("\n"))
    for line in lines:
        idx = line.find("*")
        if idx != -1 and line[0] != "*":  # Check for a single *
            if any(k in line for k in keys.values()):  # Check if line contains any key
                # Update dictionary with concept and value
                number = float(remove_dots(extract_numbers(line[idx+1:])[0]))
                key = remove_non_letters_and_whitespace(line[idx+1:])
                income_dict.update({key:number})
        elif "líquido" in line.lower() and "madrid" not in line.lower():
            number = float(remove_dots(extract_numbers(line)[0]))
            income_dict.update({"liquido_a_percibir": number})
        elif "t. a deducir" in line.lower():
            try:
                next_line = next(lines)  # Advance to the next line
                income_dict.update({"t_a_deducir": float(remove_dots(extract_numbers(next_line)[-1]))})
                # You can process next_line here as needed
            except StopIteration:
                break  # End loop if there are no more lines
    return income_dict
def ingreso_bruto(income):
    total = 0
    for key, value in income.items():
        if key != "liquido_a_percibir" and key != "t_a_deducir":
            total += value
    return round(total,2 )

def json_to_csv(income, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = income.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow(income)

def get_data(pdf_path):
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    text = page.extract_text()
    income = get_income(text)
    print(income)
    ingreso_brt = ingreso_bruto(income)
    ingreso_net = income["liquido_a_percibir"]
    print(f"Ingreso bruto: {ingreso_brt}")
    print(f"Ingreso neto: {ingreso_net}")

    json_to_csv(income, "datos.csv")

def main():
    get_data("./nominas/abr-2023.pdf")

if __name__ == '__main__':
    main()