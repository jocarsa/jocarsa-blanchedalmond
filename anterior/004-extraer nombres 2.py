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

def extract_names_from_folder(folder_path):
    """
    Recursively extracts names from all PDF files in a folder.

    :param folder_path: Path to the folder
    :return: A dictionary with file paths as keys and lists of extracted names as values
    """
    extracted_data = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                names = extract_names_from_pdf(file_path)
                if names:
                    extracted_data[file_path] = names
    return extracted_data

# Example usage
folder_path = "/home/josevicente/Escritorio/Boletines/boletines"
extracted_data = extract_names_from_folder(folder_path)

# Print extracted names
for file, names in extracted_data.items():
    print(f"File: {file}")
    for name in names:
        print(f"  - {name}")
