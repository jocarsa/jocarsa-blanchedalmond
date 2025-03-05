import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdfs_in_folder(input_folder, output_folder):
    """
    Splits all PDFs in a folder into single-page PDFs and organizes them into separate folders.

    Args:
        input_folder (str): Path to the folder containing PDF files.
        output_folder (str): Path to the folder where output folders will be created.
    """
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get a list of all PDF files in the input folder
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]

    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_folder, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]
        pdf_output_dir = os.path.join(output_folder, pdf_name)

        # Create a folder for the current PDF file
        if not os.path.exists(pdf_output_dir):
            os.makedirs(pdf_output_dir)

        print(f"Processing: {pdf_file}")

        # Split the PDF into single-page PDFs
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)

        for i in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])

            output_file_path = os.path.join(pdf_output_dir, f"page_{i+1}.pdf")
            with open(output_file_path, 'wb') as output_file:
                writer.write(output_file)

            print(f"Saved: {output_file_path}")

# Example usage
input_folder_path = "/home/josevicente/Escritorio/Boletines"  # Folder containing PDF files
output_folder_path = "/home/josevicente/Escritorio/Boletines/boletines"  # Folder to save the processed PDFs
split_pdfs_in_folder(input_folder_path, output_folder_path)
