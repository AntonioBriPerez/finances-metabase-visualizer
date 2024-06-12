import csv
from PyPDF2 import PdfReader
import re
import openpyxl
import pandas as pd
import os
from dotenv import load_dotenv
from K_CONSTANTS import keys, date_pattern, number_pattern

load_dotenv()


iCloudFolderNominas = os.getenv("iCloudFolderNominas")
iCloudFolderCalculos = os.getenv("iCloudFolderCalculos")


def extract_numbers(text):
    pattern = number_pattern
    ocurrences = re.findall(pattern, text)
    return ocurrences


def remove_non_letters_and_whitespace(text):
    return re.sub(r"[^a-zA-Z]", "", text).lower()


def remove_dots(s):
    s_no_dots = s.replace(".", "")
    s_comma_to_dot = s_no_dots.replace(",", ".")
    return float(s_comma_to_dot)


def get_income(text) -> dict:
    income_dict = {}
    lines = iter(text.split("\n"))
    for line in lines:
        idx = line.find("*")
        if idx != -1 and line[0] != "*":  # Check for a single *
            if any(k in line for k in keys.values()):  # Check if line contains any key
                # Update dictionary with concept and value
                number = float(remove_dots(extract_numbers(line[idx + 1 :])[0]))
                key = remove_non_letters_and_whitespace(line[idx + 1 :])
                income_dict.update({key: number})
        elif "líquido" in line.lower() and "madrid" not in line.lower():
            number = float(remove_dots(extract_numbers(line)[0]))
            income_dict.update({"liquido_a_percibir": number})
        elif "t. a deducir" in line.lower():
            try:
                next_line = next(lines)  # Advance to the next line
                income_dict.update(
                    {"t_a_deducir": float(remove_dots(extract_numbers(next_line)[-1]))}
                )
                # You can process next_line here as needed
            except StopIteration:
                break  # End loop if there are no more lines
    return income_dict


def ingreso_bruto(income):
    total = 0
    for key, value in income.items():
        if key != "liquido_a_percibir" and key != "t_a_deducir":
            total += value
    return round(total, 2)


def csv_to_excel(csv_filename, excel_filename):
    df = pd.read_csv(csv_filename)
    df.to_excel(excel_filename, index=False, engine="openpyxl")


def json_to_csv(list_of_dicts, filename):
    if not list_of_dicts:  # Check if the list is not empty
        return

    # Step 1: Collect all unique fieldnames from all dictionaries
    all_fieldnames = set()
    for income in list_of_dicts:
        all_fieldnames.update(income.keys())
    all_fieldnames = list(all_fieldnames)

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_fieldnames)

        writer.writeheader()

        # Step 2: For each dictionary, add missing fieldnames with a value of 0
        for income in list_of_dicts:
            for field in all_fieldnames:
                if field not in income:
                    income[field] = 0  # Assign 0 to missing keys
            writer.writerow(income)


def buscar_mes_y_año(texto):
    # Expresión regular para buscar el mes (en formato texto) y el año (1900-2099)
    pattern = date_pattern
    match = re.search(pattern, texto, re.IGNORECASE)
    if match:
        return match.group()
    else:
        return "Mes y año no encontrados"


def get_data(pdf_path):
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    text = page.extract_text()
    income = get_income(text)
    income.update({"fecha": buscar_mes_y_año(text)})
    return income


def read_nominas_recursively(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".pdf"):
                yield os.path.join(root, file)


def main():
    data = []
    for nomina in read_nominas_recursively(iCloudFolderNominas):
        income = get_data(nomina)
        data.append(income)

    json_to_csv(data, f"{iCloudFolderCalculos}/nominas.csv")
    csv_to_excel(
        f"{iCloudFolderCalculos}/nominas.csv", f"{iCloudFolderCalculos}/nominas.xlsx"
    )


if __name__ == "__main__":
    main()
