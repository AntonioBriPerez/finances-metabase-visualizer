from pathlib import Path
from typing import List
def transform_date(date_str):
    # Dictionary mapping month numbers to three-letter abbreviations
    month_map = {
        '01': 'jan', '02': 'feb', '03': 'mar', '04': 'apr', '05': 'may', '06': 'jun',
        '07': 'jul', '08': 'aug', '09': 'sep', '10': 'oct', '11': 'nov', '12': 'dec'
    }
    
    # Split the date string by '/'
    day, month, year = date_str.split('/')
    
    # Get the abbreviated month
    month_abbrev = month_map.get(month, month)
    
    # Return in the desired format
    return f"{month_abbrev}-{year}"

def list_files_recursive(directory_path: str, extensions: List[str] = None):
    """
    List files recursively in a directory, optionally filtering by file extensions.
    
    :param directory_path: The directory to search.
    :param extensions: A list of file extensions to include (e.g., ['.txt', '.log']).
    :return: Yields the full path of each matching file.
    """
    # Convert the directory path to a Path object
    path = Path(directory_path)

    # Check if the directory exists
    if not path.exists() or not path.is_dir():
        raise ValueError(f"The path {directory_path} is not a valid directory.")

    # Iterate over files recursively
    for file in path.rglob("*"):
        if file.is_file():
            if extensions is None or file.suffix in extensions:
                yield file.resolve()  # Return the full path as a Path object
