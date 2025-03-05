import os
import re
from PyPDF2 import PdfReader

def extract_names_from_pdf(file_path):
    """
    Extracts names from a PDF file based on the presence of the text "Alumne/a" or "Alumno/a".

    :param file_path: Path to the PDF file
    :return: A list of extracted names
    """
    names = []
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                # Regex to match the format: Alumne/a / Alumno/a: <Name>
                matches = re.findall(r'(?:Alumne/a|Alumno/a):\s*(.+)', text)
                names.extend(matches)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return names

def sanitize_filename(name):
    """
    Sanitizes a string to be used as a valid file name.

    :param name: The original name string
    :return: A sanitized file name
    """
    return re.sub(r'[\\/*?"<>|]', '_', name)

def rename_pdf_files(folder_path):
    """
    Recursively extracts names from all PDF files in a folder and renames the files accordingly.

    :param folder_path: Path to the folder
    """
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                names = extract_names_from_pdf(file_path)
                if names:
                    # Use the first extracted name for renaming
                    new_name = sanitize_filename(names[0]) + ".pdf"
                    new_path = os.path.join(root, new_name)
                    try:
                        os.rename(file_path, new_path)
                        print(f"Renamed: {file_path} -> {new_path}")
                    except Exception as e:
                        print(f"Error renaming {file_path}: {e}")

# Example usage
folder_path = "/home/josevicente/Escritorio/Boletines/boletines"
rename_pdf_files(folder_path)
