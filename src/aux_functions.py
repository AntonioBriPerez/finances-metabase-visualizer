from pathlib import Path
from typing import List
import hashlib


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
