import os
import PyPDF2
import spacy

# Load SpaCy's Spanish model
nlp = spacy.load("es_core_news_sm")

# Predefined lists of common Spanish names and surnames
COMMON_SPANISH_NAMES = {"Juan", "Carlos", "María", "José", "Luis", "Ana", "Carmen", "Francisco"}
COMMON_SPANISH_SURNAMES = {"García", "López", "Martínez", "Rodríguez", "Hernández", "Pérez", "González", "Sánchez"}

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file.
    """
    text = ""
    try:
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return text

def extract_common_names(text):
    """
    Extract common Spanish names and surnames from text.
    """
    doc = nlp(text)
    extracted_names = set()

    for ent in doc.ents:
        if ent.label_ == "PER":  # Check if the entity is a person
            words = ent.text.split()
            for word in words:
                # Match against common names and surnames
                if word in COMMON_SPANISH_NAMES or word in COMMON_SPANISH_SURNAMES:
                    extracted_names.add(word)
    
    return list(extracted_names)

def find_pdf_files(folder_path):
    """
    Recursively find all PDF files in a given folder.
    """
    pdf_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def main(folder_path):
    """
    Main function to process PDFs and extract common Spanish names.
    """
    pdf_files = find_pdf_files(folder_path)
    all_names = {}

    for pdf_file in pdf_files:
        print(f"Processing {pdf_file}...")
        text = extract_text_from_pdf(pdf_file)
        names = extract_common_names(text)
        all_names[pdf_file] = names

    # Display results
    for pdf, names in all_names.items():
        print(f"\nCommon Spanish names found in {pdf}:")
        for name in names:
            print(f" - {name}")

if __name__ == "__main__":
    folder_path = input("Enter the path to the folder: ").strip()
    main(folder_path)
