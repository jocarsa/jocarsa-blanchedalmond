import os
import re
import json
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter

# Nombre del archivo de configuración
CONFIG_FILE = "config.json"

def load_config():
    """Carga la configuración desde el archivo JSON."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config
        except Exception as e:
            print("Error al cargar la configuración:", e)
    # Valores por defecto si no existe la configuración
    return {"carpeta_origen": "", "carpeta_destino": ""}

def save_config(config):
    """Guarda la configuración en un archivo JSON."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Error al guardar la configuración:", e)

def split_pdfs_in_folder(input_folder, output_folder):
    """
    Divide cada PDF en el folder de origen en páginas individuales.
    Cada PDF se guarda en una subcarpeta (con el mismo nombre que el PDF sin extensión)
    dentro de la carpeta de destino.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_folder, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]
        pdf_output_dir = os.path.join(output_folder, pdf_name)
        if not os.path.exists(pdf_output_dir):
            os.makedirs(pdf_output_dir)

        print(f"Procesando: {pdf_file}")
        try:
            reader = PdfReader(pdf_path)
        except Exception as e:
            print(f"Error al abrir {pdf_file}: {e}")
            continue

        total_pages = len(reader.pages)
        for i in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            output_file_path = os.path.join(pdf_output_dir, f"pagina_{i+1}.pdf")
            try:
                with open(output_file_path, 'wb') as output_file:
                    writer.write(output_file)
                print(f"Guardado: {output_file_path}")
            except Exception as e:
                print(f"Error al guardar {output_file_path}: {e}")

def extract_names_from_pdf(file_path):
    """
    Extrae nombres del PDF buscando líneas que contengan "Alumne/a:" o "Alumno/a:".
    """
    names = []
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                matches = re.findall(r'(?:Alumne/a|Alumno/a):\s*(.+)', text)
                names.extend(matches)
    except Exception as e:
        print(f"Error al leer {file_path}: {e}")
    return names

def sanitize_filename(name):
    """
    Sanitiza un string para que se pueda usar como nombre de archivo válido.
    """
    return re.sub(r'[\\/*?"<>|]', '_', name)

def rename_pdf_files(folder_path):
    """
    Recorre recursivamente todos los archivos PDF en folder_path y los renombra
    basándose en el primer nombre encontrado.
    """
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                names = extract_names_from_pdf(file_path)
                if names:
                    new_name = sanitize_filename(names[0]) + ".pdf"
                    new_path = os.path.join(root, new_name)
                    try:
                        os.rename(file_path, new_path)
                        print(f"Renombrado: {file_path} -> {new_path}")
                    except Exception as e:
                        print(f"Error renombrando {file_path}: {e}")

def process_pdfs():
    """
    Ejecuta el proceso completo: divide los PDFs y luego renombra los archivos divididos.
    """
    src = source_folder_var.get()
    tgt = target_folder_var.get()
    if not src or not tgt:
        messagebox.showerror("Error", "Por favor, seleccione ambas carpetas.")
        return

    split_pdfs_in_folder(src, tgt)
    rename_pdf_files(tgt)
    messagebox.showinfo("Completado", "El procesamiento de PDFs ha finalizado.")

def seleccionar_carpeta_origen():
    folder = filedialog.askdirectory(title="Seleccione Carpeta de Origen")
    if folder:
        source_folder_var.set(folder)
        source_entry.delete(0, tk.END)
        source_entry.insert(0, folder)
        config_data["carpeta_origen"] = folder
        save_config(config_data)

def seleccionar_carpeta_destino():
    folder = filedialog.askdirectory(title="Seleccione Carpeta de Destino")
    if folder:
        target_folder_var.set(folder)
        target_entry.delete(0, tk.END)
        target_entry.insert(0, folder)
        config_data["carpeta_destino"] = folder
        save_config(config_data)

# Cargar la configuración previamente guardada
config_data = load_config()

# Crear la ventana principal usando ttkbootstrap
root = ttk.Window(themename="flatly")
root.title("jocarsa | blanchedalmond - Divisor y Renombrador de PDFs con Boletines")

# Cargar la imagen (asegúrese de que 'blanchedalmond.png' esté en la misma carpeta que el script)
try:
    imagen = tk.PhotoImage(file="blanchedalmond.png")
except Exception as e:
    print("Error al cargar la imagen:", e)
    imagen = None

# Mostrar la imagen en la parte superior, si se cargó correctamente
if imagen:
    imagen_label = ttk.Label(root, image=imagen)
    imagen_label.pack(pady=10)

# Variables para almacenar las rutas (usando tk.StringVar)
source_folder_var = tk.StringVar(value=config_data.get("carpeta_origen", ""))
target_folder_var = tk.StringVar(value=config_data.get("carpeta_destino", ""))

# Crear un frame para los controles del formulario
form_frame = ttk.Frame(root)
form_frame.pack(padx=20, pady=20)

# Fila para la carpeta de origen
ttk.Label(form_frame, text="Carpeta de Origen:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
source_entry = ttk.Entry(form_frame, textvariable=source_folder_var, width=50)
source_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(form_frame, text="Examinar", command=seleccionar_carpeta_origen).grid(row=0, column=2, padx=5, pady=5)

# Fila para la carpeta de destino
ttk.Label(form_frame, text="Carpeta de Destino:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
target_entry = ttk.Entry(form_frame, textvariable=target_folder_var, width=50)
target_entry.grid(row=1, column=1, padx=5, pady=5)
ttk.Button(form_frame, text="Examinar", command=seleccionar_carpeta_destino).grid(row=1, column=2, padx=5, pady=5)

# Botón para iniciar el procesamiento
ttk.Button(root, text="Iniciar Procesamiento", bootstyle="success", command=process_pdfs).pack(pady=10)

root.mainloop()
