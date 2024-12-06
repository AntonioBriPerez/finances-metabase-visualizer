from pathlib import Path
from typing import List

# Diccionario para convertir el mes en español a su abreviatura
meses_abrev = {
    "Enero": "ene",
    "Febrero": "feb",
    "Marzo": "mar",
    "Abril": "abr",
    "Mayo": "may",
    "Junio": "jun",
    "Julio": "jul",
    "Agosto": "ago",
    "Septiembre": "sep",
    "Octubre": "oct",
    "Noviembre": "nov",
    "Diciembre": "dic",
}


def convertir_fecha(fecha):
    # Dividir la cadena de fecha por espacio
    partes = fecha.split()

    # El mes es la segunda parte (índice 1) y el año es la tercera parte (índice 2)
    mes = partes[1]
    año = partes[2]

    # Convertir el mes a su abreviatura
    mes_abrev = meses_abrev.get(mes)

    if mes_abrev:
        # Retornar el formato deseado: "mes-año"
        return f"{mes_abrev}-{año}"
    else:
        return "Mes no válido"


def transform_date(date_str):
    # Dictionary mapping month numbers to three-letter abbreviations
    month_map = {
        "01": "jan",
        "02": "feb",
        "03": "mar",
        "04": "apr",
        "05": "may",
        "06": "jun",
        "07": "jul",
        "08": "aug",
        "09": "sep",
        "10": "oct",
        "11": "nov",
        "12": "dec",
    }

    # Split the date string by '/'
    day, month, year = date_str.split("/")

    # Get the abbreviated month
    month_abbrev = month_map.get(month, month)

    # Return in the desired format
    return f"{month_abbrev}-{year}"


def list_files_recursive(
    directory_path: str, extensions: List[str] = None
) -> List[Path]:
    """
    List files recursively in a directory, optionally filtering by file extensions.

    :param directory_path: The directory to search.
    :param extensions: A list of file extensions to include (e.g., ['.txt', '.log']).
    :return: A list of full paths of each matching file.
    """
    # Convert the directory path to a Path object
    path = Path(directory_path)

    # Check if the directory exists
    if not path.exists() or not path.is_dir():
        raise ValueError(f"The path {directory_path} is not a valid directory.")

    # List to store the file paths
    files_list = []

    # Iterate over files recursively
    for file in path.rglob("*"):
        if file.is_file():
            if extensions is None or file.suffix in extensions:
                files_list.append(
                    file.resolve()
                )  # Add the full path as a Path object to the list

    return files_list
