from pathlib import Path
from typing import List
import hashlib

# Diccionario para convertir el mes en español a su abreviatura
meses_abrev = {
    "Enero": "ene.",
    "Febrero": "feb.",
    "Marzo": "mar.",
    "Abril": "abr.",
    "Mayo": "may.",
    "Junio": "jun.",
    "Julio": "jul.",
    "Agosto": "ago.",
    "Septiembre": "sept.",
    "Octubre": "oct.",
    "Noviembre": "nov.",
    "Diciembre": "dic.",
}


def generar_hash_archivo(ruta_archivo):
    # Crear un objeto hash SHA-256
    sha256_hash = hashlib.sha256()

    # Abrir el archivo en modo binario
    with open(ruta_archivo, "rb") as archivo:
        # Leer y actualizar el hash por bloques de 4096 bytes
        for byte_block in iter(lambda: archivo.read(4096), b""):
            sha256_hash.update(byte_block)

    # Devolver el hash en formato hexadecimal
    return sha256_hash.hexdigest()


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
        return f"{año}-{obtener_mes_como_numero(mes)}-01"
    else:
        return "Mes no válido"


def obtener_mes_como_numero(mes):
    # Diccionario para convertir el mes en español a su número correspondiente
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

    # Obtener el número del mes
    return meses_numeros.get(mes, "Mes no válido")


def transform_date(date_str):
    # Split the date string by '/'
    day, month, year = date_str.split("/")

    # Return in the format accepted by PostgreSQL: 'YYYY-MM-DD'
    return f"{year}-{month}-{day}"


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
