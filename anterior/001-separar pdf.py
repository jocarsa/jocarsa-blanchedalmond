from PyPDF2 import PdfReader, PdfWriter
import os

def split_pdf(input_pdf_path, output_dir):
    """
    Splits a multi-page PDF into single-page PDFs.

    Args:
        input_pdf_path (str): Path to the input PDF file.
        output_dir (str): Directory to save the single-page PDFs.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)

    for i in range(total_pages):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])

        output_file_path = os.path.join(output_dir, f"page_{i+1}.pdf")
        with open(output_file_path, 'wb') as output_file:
            writer.write(output_file)

        print(f"Saved: {output_file_path}")

# Example usage
input_pdf = "/home/josevicente/Escritorio/Boletines/Inf. Evaluación_2 GS Distancia.pdf"  # Path to your multi-page PDF
output_directory = "/home/josevicente/Escritorio/Boletines/DAM2"  # Directory to save single-page PDFs
split_pdf(input_pdf, output_directory)
