import os
import re
import json
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, simpledialog
import webbrowser
from PyPDF2 import PdfReader, PdfWriter

# Intentar importar módulos opcionales
try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

try:
    from PIL import Image
except ImportError:
    Image = None

# --- Configuración ---
CONFIG_FILE = "config.json"

def cargar_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config
        except Exception as e:
            print("Error al cargar la configuración:", e)
    return {"carpeta_origen": "", "carpeta_destino": ""}

def guardar_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Error al guardar la configuración:", e)

# --- Funciones comunes ---
def extraer_nombres_pdf(ruta_archivo):
    """Extrae nombres del PDF buscando líneas que contengan 'Alumne/a:' o 'Alumno/a:'."""
    nombres = []
    try:
        reader = PdfReader(ruta_archivo)
        for pagina in reader.pages:
            texto = pagina.extract_text()
            if texto:
                coincidencias = re.findall(r'(?:Alumne/a|Alumno/a):\s*(.+)', texto)
                nombres.extend(coincidencias)
    except Exception as e:
        print(f"Error al leer {ruta_archivo}: {e}")
    return nombres

def sanitizar_nombre(nombre):
    """Sanitiza un string para usarlo como nombre de archivo válido."""
    return re.sub(r'[\\/*?"<>|]', '_', nombre)

def dividir_pdf_archivo(archivo_entrada, carpeta_salida, prefijo="pagina"):
    """Divide un único PDF en páginas individuales usando un prefijo para el nombre."""
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    try:
        reader = PdfReader(archivo_entrada)
    except Exception as e:
        messagebox.showerror("Error", f"Error al abrir el archivo:\n{e}")
        return
    total_paginas = len(reader.pages)
    for i in range(total_paginas):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        nombre_archivo = f"{prefijo}_{i+1}.pdf"
        ruta_salida = os.path.join(carpeta_salida, nombre_archivo)
        try:
            with open(ruta_salida, 'wb') as f:
                writer.write(f)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar {ruta_salida}:\n{e}")

def dividir_pdfs_carpeta(carpeta_entrada, carpeta_salida):
    """
    Para cada PDF en carpeta_entrada:
      - Crea una subcarpeta (con el nombre del archivo sin extensión) en carpeta_salida.
      - Divide el PDF en páginas individuales.
    Luego renombra cada archivo usando el primer nombre extraído.
    """
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
    archivos_pdf = [f for f in os.listdir(carpeta_entrada) if f.lower().endswith('.pdf')]
    for archivo in archivos_pdf:
        ruta_pdf = os.path.join(carpeta_entrada, archivo)
        nombre_pdf = os.path.splitext(archivo)[0]
        carpeta_pdf = os.path.join(carpeta_salida, nombre_pdf)
        if not os.path.exists(carpeta_pdf):
            os.makedirs(carpeta_pdf)
        try:
            reader = PdfReader(ruta_pdf)
        except Exception as e:
            print(f"Error al abrir {archivo}: {e}")
            continue
        total_paginas = len(reader.pages)
        for i in range(total_paginas):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            ruta_salida = os.path.join(carpeta_pdf, f"pagina_{i+1}.pdf")
            try:
                with open(ruta_salida, 'wb') as salida:
                    writer.write(salida)
            except Exception as e:
                print(f"Error al guardar {ruta_salida}: {e}")
    renombrar_pdfs(carpeta_salida)

def renombrar_pdfs(carpeta):
    """Recorre recursivamente la carpeta y renombra cada PDF según el primer nombre extraído."""
    for root_dir, _, archivos in os.walk(carpeta):
        for archivo in archivos:
            if archivo.lower().endswith('.pdf'):
                ruta_archivo = os.path.join(root_dir, archivo)
                nombres = extraer_nombres_pdf(ruta_archivo)
                if nombres:
                    nuevo_nombre = sanitizar_nombre(nombres[0]) + ".pdf"
                    nueva_ruta = os.path.join(root_dir, nuevo_nombre)
                    try:
                        os.rename(ruta_archivo, nueva_ruta)
                    except Exception as e:
                        print(f"Error renombrando {ruta_archivo}: {e}")

# --- Funciones de interfaz en el área principal ---
def limpiar_contenido():
    """Elimina todos los widgets del área principal."""
    for widget in main_frame.winfo_children():
        widget.destroy()

def mostrar_inicio():
    """Muestra la pantalla de inicio con el logo, el texto de copyright y la descripción."""
    limpiar_contenido()
    # Mostrar logo (si existe)
    if imagen:
        label_img = ttk.Label(main_frame, image=imagen)
        label_img.pack(pady=10)
    # Texto de copyright bajo el logo
    label_app = ttk.Label(main_frame, 
                          text="jocarsa | blanchedalmond 1.2 (c) 2025 JOCARSA - Jose Vicente Carratala Sanchis", 
                          font=("Ubuntu", 16, "bold"), justify="center")
    label_app.pack(pady=5)
    desc = ("Esta aplicación le permite dividir, renombrar y unir archivos PDF, convertir PDF a JPG y\n"
            "unir imágenes en PDF.\nUtilice el menú 'Operaciones' para comenzar.")
    label_desc = ttk.Label(main_frame, text=desc, wraplength=400, justify="center", font=("Ubuntu", 10))
    label_desc.pack(pady=5)
    label_info = ttk.Label(main_frame, text="Selecciona una opción del menú", font=("Ubuntu", 14))
    label_info.pack(pady=10)

def boton_volver(parent):
    """Crea un botón para volver a la pantalla de inicio."""
    btn = ttk.Button(parent, text="Volver", bootstyle="secondary", command=mostrar_inicio)
    btn.pack(pady=10)
    return btn

def mostrar_dividir_boletines():
    limpiar_contenido()
    titulo = ttk.Label(main_frame, text="Dividir PDFs en Carpeta", font=("Ubuntu", 14, "bold"))
    titulo.pack(pady=10)
    instrucciones = ("Seleccione la carpeta de origen que contiene los archivos PDF y la carpeta de destino "
                     "donde se guardarán los archivos divididos.")
    label_inst = ttk.Label(main_frame, text=instrucciones, wraplength=400, font=("Ubuntu", 10))
    label_inst.pack(pady=5)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(padx=20, pady=20)
    
    # Carpeta de Origen
    ttk.Label(form_frame, text="Carpeta de Origen:", font=("Ubuntu", 10)).grid(row=0, column=0, sticky="w")
    entry_origen = ttk.Entry(form_frame, width=40)
    entry_origen.grid(row=0, column=1, padx=5)
    def buscar_origen():
        carpeta = filedialog.askdirectory(title="Seleccione Carpeta de Origen")
        if carpeta:
            entry_origen.delete(0, tk.END)
            entry_origen.insert(0, carpeta)
    ttk.Button(form_frame, text="Examinar", command=buscar_origen).grid(row=0, column=2, padx=5)
    
    # Carpeta de Destino
    ttk.Label(form_frame, text="Carpeta de Destino:", font=("Ubuntu", 10)).grid(row=1, column=0, sticky="w")
    entry_destino = ttk.Entry(form_frame, width=40)
    entry_destino.grid(row=1, column=1, padx=5)
    def buscar_destino():
        carpeta = filedialog.askdirectory(title="Seleccione Carpeta de Destino")
        if carpeta:
            entry_destino.delete(0, tk.END)
            entry_destino.insert(0, carpeta)
    ttk.Button(form_frame, text="Examinar", command=buscar_destino).grid(row=1, column=2, padx=5)
    
    def ejecutar():
        origen = entry_origen.get().strip()
        destino = entry_destino.get().strip()
        if not origen or not destino:
            messagebox.showerror("Error", "Debe seleccionar ambas carpetas.")
            return
        dividir_pdfs_carpeta(origen, destino)
        messagebox.showinfo("Completado", "El procesamiento de PDFs ha finalizado.")
        mostrar_inicio()
        
    ttk.Button(main_frame, text="Ejecutar", bootstyle="success", command=ejecutar).pack(pady=10)
    boton_volver(main_frame)

def mostrar_dividir_un_archivo():
    limpiar_contenido()
    titulo = ttk.Label(main_frame, text="Dividir un PDF (Boletines)", font=("Ubuntu", 14, "bold"))
    titulo.pack(pady=10)
    instrucciones = ("Seleccione un archivo PDF y la carpeta de destino para dividir el PDF en páginas individuales.")
    ttk.Label(main_frame, text=instrucciones, wraplength=400, font=("Ubuntu", 10)).pack(pady=5)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(padx=20, pady=20)
    
    # Archivo PDF de Origen
    ttk.Label(form_frame, text="Archivo PDF de Origen:", font=("Ubuntu", 10)).grid(row=0, column=0, sticky="w")
    entry_archivo = ttk.Entry(form_frame, width=40)
    entry_archivo.grid(row=0, column=1, padx=5)
    def buscar_archivo():
        archivo = filedialog.askopenfilename(title="Seleccione Archivo PDF", filetypes=[("PDF Files", "*.pdf")])
        if archivo:
            entry_archivo.delete(0, tk.END)
            entry_archivo.insert(0, archivo)
    ttk.Button(form_frame, text="Examinar", command=buscar_archivo).grid(row=0, column=2, padx=5)
    
    # Carpeta de Destino
    ttk.Label(form_frame, text="Carpeta de Destino:", font=("Ubuntu", 10)).grid(row=1, column=0, sticky="w")
    entry_destino = ttk.Entry(form_frame, width=40)
    entry_destino.grid(row=1, column=1, padx=5)
    def buscar_destino():
        carpeta = filedialog.askdirectory(title="Seleccione Carpeta de Destino")
        if carpeta:
            entry_destino.delete(0, tk.END)
            entry_destino.insert(0, carpeta)
    ttk.Button(form_frame, text="Examinar", command=buscar_destino).grid(row=1, column=2, padx=5)
    
    def ejecutar():
        archivo = entry_archivo.get().strip()
        destino = entry_destino.get().strip()
        if not archivo or not destino:
            messagebox.showerror("Error", "Debe seleccionar el archivo y la carpeta de destino.")
            return
        nombre_base = os.path.splitext(os.path.basename(archivo))[0]
        carpeta_resultado = os.path.join(destino, nombre_base)
        dividir_pdf_archivo(archivo, carpeta_resultado, prefijo="pagina")
        renombrar_pdfs(carpeta_resultado)
        messagebox.showinfo("Completado", "El procesamiento del PDF ha finalizado.")
        mostrar_inicio()
        
    ttk.Button(main_frame, text="Ejecutar", bootstyle="success", command=ejecutar).pack(pady=10)
    boton_volver(main_frame)

def mostrar_dividir_pdfs_prefijo():
    limpiar_contenido()
    titulo = ttk.Label(main_frame, text="Dividir PDFs en Carpeta (Prefijo Personalizado)", font=("Ubuntu", 14, "bold"))
    titulo.pack(pady=10)
    instrucciones = ("Seleccione la carpeta de origen que contiene los PDFs, la carpeta de destino y especifique un prefijo "
                     "para los archivos resultantes.")
    ttk.Label(main_frame, text=instrucciones, wraplength=400, font=("Ubuntu", 10)).pack(pady=5)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(padx=20, pady=20)
    
    # Carpeta de Origen
    ttk.Label(form_frame, text="Carpeta de Origen:", font=("Ubuntu", 10)).grid(row=0, column=0, sticky="w")
    entry_origen = ttk.Entry(form_frame, width=40)
    entry_origen.grid(row=0, column=1, padx=5)
    def buscar_origen():
        carpeta = filedialog.askdirectory(title="Seleccione Carpeta de Origen")
        if carpeta:
            entry_origen.delete(0, tk.END)
            entry_origen.insert(0, carpeta)
    ttk.Button(form_frame, text="Examinar", command=buscar_origen).grid(row=0, column=2, padx=5)
    
    # Carpeta de Destino
    ttk.Label(form_frame, text="Carpeta de Destino:", font=("Ubuntu", 10)).grid(row=1, column=0, sticky="w")
    entry_destino = ttk.Entry(form_frame, width=40)
    entry_destino.grid(row=1, column=1, padx=5)
    def buscar_destino():
        carpeta = filedialog.askdirectory(title="Seleccione Carpeta de Destino")
        if carpeta:
            entry_destino.delete(0, tk.END)
            entry_destino.insert(0, carpeta)
    ttk.Button(form_frame, text="Examinar", command=buscar_destino).grid(row=1, column=2, padx=5)
    
    # Prefijo
    ttk.Label(form_frame, text="Prefijo:", font=("Ubuntu", 10)).grid(row=2, column=0, sticky="w")
    entry_prefijo = ttk.Entry(form_frame, width=40)
    entry_prefijo.grid(row=2, column=1, padx=5)
    
    def ejecutar():
        origen = entry_origen.get().strip()
        destino = entry_destino.get().strip()
        prefijo = entry_prefijo.get().strip()
        if not origen or not destino or not prefijo:
            messagebox.showerror("Error", "Debe completar todos los campos.")
            return
        archivos_pdf = [f for f in os.listdir(origen) if f.lower().endswith('.pdf')]
        for archivo in archivos_pdf:
            ruta_pdf = os.path.join(origen, archivo)
            nombre_pdf = os.path.splitext(archivo)[0]
            carpeta_pdf = os.path.join(destino, nombre_pdf)
            if not os.path.exists(carpeta_pdf):
                os.makedirs(carpeta_pdf)
            try:
                reader = PdfReader(ruta_pdf)
            except Exception as e:
                print(f"Error al abrir {archivo}: {e}")
                continue
            total_paginas = len(reader.pages)
            for i in range(total_paginas):
                writer = PdfWriter()
                writer.add_page(reader.pages[i])
                ruta_salida = os.path.join(carpeta_pdf, f"{prefijo}_{i+1}.pdf")
                try:
                    with open(ruta_salida, 'wb') as f:
                        writer.write(f)
                except Exception as e:
                    print(f"Error al guardar {ruta_salida}: {e}")
        messagebox.showinfo("Completado", "La división de PDFs en carpeta ha finalizado.")
        mostrar_inicio()
    
    ttk.Button(main_frame, text="Ejecutar", bootstyle="success", command=ejecutar).pack(pady=10)
    boton_volver(main_frame)

def mostrar_dividir_pdf_unico_prefijo():
    limpiar_contenido()
    titulo = ttk.Label(main_frame, text="Dividir un PDF (Prefijo Personalizado)", font=("Ubuntu", 14, "bold"))
    titulo.pack(pady=10)
    instrucciones = ("Seleccione un archivo PDF, la carpeta de destino y especifique un prefijo para nombrar cada página.")
    ttk.Label(main_frame, text=instrucciones, wraplength=400, font=("Ubuntu", 10)).pack(pady=5)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(padx=20, pady=20)
    
    # Archivo PDF de Origen
    ttk.Label(form_frame, text="Archivo PDF de Origen:", font=("Ubuntu", 10)).grid(row=0, column=0, sticky="w")
    entry_archivo = ttk.Entry(form_frame, width=40)
    entry_archivo.grid(row=0, column=1, padx=5)
    def buscar_archivo():
        archivo = filedialog.askopenfilename(title="Seleccione Archivo PDF", filetypes=[("PDF Files", "*.pdf")])
        if archivo:
            entry_archivo.delete(0, tk.END)
            entry_archivo.insert(0, archivo)
    ttk.Button(form_frame, text="Examinar", command=buscar_archivo).grid(row=0, column=2, padx=5)
    
    # Carpeta de Destino
    ttk.Label(form_frame, text="Carpeta de Destino:", font=("Ubuntu", 10)).grid(row=1, column=0, sticky="w")
    entry_destino = ttk.Entry(form_frame, width=40)
    entry_destino.grid(row=1, column=1, padx=5)
    def buscar_destino():
        carpeta = filedialog.askdirectory(title="Seleccione Carpeta de Destino")
        if carpeta:
            entry_destino.delete(0, tk.END)
            entry_destino.insert(0, carpeta)
    ttk.Button(form_frame, text="Examinar", command=buscar_destino).grid(row=1, column=2, padx=5)
    
    # Prefijo
    ttk.Label(form_frame, text="Prefijo:", font=("Ubuntu", 10)).grid(row=2, column=0, sticky="w")
    entry_prefijo = ttk.Entry(form_frame, width=40)
    entry_prefijo.grid(row=2, column=1, padx=5)
    
    def ejecutar():
        archivo = entry_archivo.get().strip()
        destino = entry_destino.get().strip()
        prefijo = entry_prefijo.get().strip()
        if not archivo or not destino or not prefijo:
            messagebox.showerror("Error", "Debe completar todos los campos.")
            return
        nombre_base = os.path.splitext(os.path.basename(archivo))[0]
        carpeta_resultado = os.path.join(destino, nombre_base)
        dividir_pdf_archivo(archivo, carpeta_resultado, prefijo=prefijo)
        messagebox.showinfo("Completado", "La división del PDF ha finalizado.")
        mostrar_inicio()
        
    ttk.Button(main_frame, text="Ejecutar", bootstyle="success", command=ejecutar).pack(pady=10)
    boton_volver(main_frame)

def mostrar_pdf_a_jpg():
    limpiar_contenido()
    titulo = ttk.Label(main_frame, text="Convertir PDF a JPG", font=("Ubuntu", 14, "bold"))
    titulo.pack(pady=10)
    instrucciones = ("Seleccione un archivo PDF y la carpeta de destino para convertir cada página en una imagen JPG.")
    ttk.Label(main_frame, text=instrucciones, wraplength=400, font=("Ubuntu", 10)).pack(pady=5)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(padx=20, pady=20)
    
    # Archivo PDF de Origen
    ttk.Label(form_frame, text="Archivo PDF de Origen:", font=("Ubuntu", 10)).grid(row=0, column=0, sticky="w")
    entry_archivo = ttk.Entry(form_frame, width=40)
    entry_archivo.grid(row=0, column=1, padx=5)
    def buscar_archivo():
        archivo = filedialog.askopenfilename(title="Seleccione Archivo PDF", filetypes=[("PDF Files", "*.pdf")])
        if archivo:
            entry_archivo.delete(0, tk.END)
            entry_archivo.insert(0, archivo)
    ttk.Button(form_frame, text="Examinar", command=buscar_archivo).grid(row=0, column=2, padx=5)
    
    # Carpeta de Destino
    ttk.Label(form_frame, text="Carpeta de Destino:", font=("Ubuntu", 10)).grid(row=1, column=0, sticky="w")
    entry_destino = ttk.Entry(form_frame, width=40)
    entry_destino.grid(row=1, column=1, padx=5)
    def buscar_destino():
        carpeta = filedialog.askdirectory(title="Seleccione Carpeta de Destino")
        if carpeta:
            entry_destino.delete(0, tk.END)
            entry_destino.insert(0, carpeta)
    ttk.Button(form_frame, text="Examinar", command=buscar_destino).grid(row=1, column=2, padx=5)
    
    def ejecutar():
        if convert_from_path is None:
            messagebox.showerror("Error", "El módulo pdf2image no está instalado.")
            return
        archivo = entry_archivo.get().strip()
        destino = entry_destino.get().strip()
        if not archivo or not destino:
            messagebox.showerror("Error", "Debe seleccionar el archivo PDF y la carpeta de destino.")
            return
        try:
            paginas = convert_from_path(archivo)
            for i, pagina in enumerate(paginas):
                ruta_salida = os.path.join(destino, f"pagina_{i+1}.jpg")
                pagina.save(ruta_salida, "JPEG")
        except Exception as e:
            messagebox.showerror("Error", f"Error al convertir PDF a JPG:\n{e}")
            return
        messagebox.showinfo("Completado", "La conversión de PDF a JPG ha finalizado.")
        mostrar_inicio()
        
    ttk.Button(main_frame, text="Ejecutar", bootstyle="success", command=ejecutar).pack(pady=10)
    boton_volver(main_frame)

def mostrar_unir_pdfs():
    limpiar_contenido()
    titulo = ttk.Label(main_frame, text="Unir PDFs en un Solo PDF", font=("Ubuntu", 14, "bold"))
    titulo.pack(pady=10)
    instrucciones = ("Seleccione los archivos PDF a unir y especifique el archivo de destino para guardar el PDF combinado.")
    ttk.Label(main_frame, text=instrucciones, wraplength=400, font=("Ubuntu", 10)).pack(pady=5)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(padx=20, pady=20)
    
    # Archivos PDF de Origen (separados por punto y coma)
    ttk.Label(form_frame, text="Archivos PDF de Origen:", font=("Ubuntu", 10)).grid(row=0, column=0, sticky="w")
    entry_archivos = ttk.Entry(form_frame, width=40)
    entry_archivos.grid(row=0, column=1, padx=5)
    def buscar_archivos():
        archivos = filedialog.askopenfilenames(title="Seleccione archivos PDF", filetypes=[("PDF Files", "*.pdf")])
        if archivos:
            entry_archivos.delete(0, tk.END)
            entry_archivos.insert(0, ";".join(archivos))
    ttk.Button(form_frame, text="Examinar", command=buscar_archivos).grid(row=0, column=2, padx=5)
    
    # Archivo PDF de Destino
    ttk.Label(form_frame, text="Archivo PDF de Destino:", font=("Ubuntu", 10)).grid(row=1, column=0, sticky="w")
    entry_destino = ttk.Entry(form_frame, width=40)
    entry_destino.grid(row=1, column=1, padx=5)
    def buscar_destino():
        archivo = filedialog.asksaveasfilename(title="Guardar PDF combinado", defaultextension=".pdf",
                                                filetypes=[("PDF Files", "*.pdf")])
        if archivo:
            entry_destino.delete(0, tk.END)
            entry_destino.insert(0, archivo)
    ttk.Button(form_frame, text="Examinar", command=buscar_destino).grid(row=1, column=2, padx=5)
    
    def ejecutar():
        lista_archivos = entry_archivos.get().strip()
        destino = entry_destino.get().strip()
        if not lista_archivos or not destino:
            messagebox.showerror("Error", "Debe seleccionar los archivos de origen y el archivo de destino.")
            return
        archivos = lista_archivos.split(";")
        writer = PdfWriter()
        for archivo in archivos:
            try:
                reader = PdfReader(archivo)
                for pagina in reader.pages:
                    writer.add_page(pagina)
            except Exception as e:
                messagebox.showerror("Error", f"Error al procesar {archivo}:\n{e}")
                return
        try:
            with open(destino, 'wb') as f:
                writer.write(f)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el PDF combinado:\n{e}")
            return
        messagebox.showinfo("Completado", "La unión de PDFs ha finalizado.")
        mostrar_inicio()
        
    ttk.Button(main_frame, text="Ejecutar", bootstyle="success", command=ejecutar).pack(pady=10)
    boton_volver(main_frame)

def mostrar_unir_jpgs():
    limpiar_contenido()
    titulo = ttk.Label(main_frame, text="Unir JPGs en un PDF", font=("Ubuntu", 14, "bold"))
    titulo.pack(pady=10)
    instrucciones = ("Seleccione las imágenes JPG a unir y especifique el archivo de destino para guardar el PDF resultante.")
    ttk.Label(main_frame, text=instrucciones, wraplength=400, font=("Ubuntu", 10)).pack(pady=5)
    
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(padx=20, pady=20)
    
    # Archivos JPG de Origen
    ttk.Label(form_frame, text="Archivos JPG de Origen:", font=("Ubuntu", 10)).grid(row=0, column=0, sticky="w")
    entry_archivos = ttk.Entry(form_frame, width=40)
    entry_archivos.grid(row=0, column=1, padx=5)
    def buscar_archivos():
        archivos = filedialog.askopenfilenames(title="Seleccione archivos JPG", 
                                                filetypes=[("JPG Files", "*.jpg"), ("JPEG Files", "*.jpeg")])
        if archivos:
            entry_archivos.delete(0, tk.END)
            entry_archivos.insert(0, ";".join(archivos))
    ttk.Button(form_frame, text="Examinar", command=buscar_archivos).grid(row=0, column=2, padx=5)
    
    # Archivo PDF de Destino
    ttk.Label(form_frame, text="Archivo PDF de Destino:", font=("Ubuntu", 10)).grid(row=1, column=0, sticky="w")
    entry_destino = ttk.Entry(form_frame, width=40)
    entry_destino.grid(row=1, column=1, padx=5)
    def buscar_destino():
        archivo = filedialog.asksaveasfilename(title="Guardar PDF combinado", defaultextension=".pdf",
                                                filetypes=[("PDF Files", "*.pdf")])
        if archivo:
            entry_destino.delete(0, tk.END)
            entry_destino.insert(0, archivo)
    ttk.Button(form_frame, text="Examinar", command=buscar_destino).grid(row=1, column=2, padx=5)
    
    def ejecutar():
        lista_archivos = entry_archivos.get().strip()
        destino = entry_destino.get().strip()
        if not lista_archivos or not destino:
            messagebox.showerror("Error", "Debe seleccionar las imágenes de origen y el archivo de destino.")
            return
        archivos = lista_archivos.split(";")
        try:
            imagenes = [Image.open(a).convert('RGB') for a in archivos]
            if imagenes:
                imagenes[0].save(destino, save_all=True, append_images=imagenes[1:])
        except Exception as e:
            messagebox.showerror("Error", f"Error al unir imágenes en PDF:\n{e}")
            return
        messagebox.showinfo("Completado", "La unión de imágenes en PDF ha finalizado.")
        mostrar_inicio()
        
    ttk.Button(main_frame, text="Ejecutar", bootstyle="success", command=ejecutar).pack(pady=10)
    boton_volver(main_frame)

# --- Funciones del Menú ---
def salir():
    root.quit()

def ayuda_en_linea():
    webbrowser.open("https://github.com/jocarsa/jocarsa-blanchedalmond")

def acerca_de():
    webbrowser.open("https://josevicentecarratala.com/")

# --- Ventana principal ---
root = ttk.Window(themename="flatly")
root.title("jocarsa | blanchedalmond")
root.geometry("1024x768")

# Aplicar la fuente Ubuntu globalmente
style = ttk.Style("flatly")
style.configure('.', font=("Ubuntu", 10))

# Intentar cargar la imagen
try:
    imagen = tk.PhotoImage(file="blanchedalmond.png")
except Exception as e:
    print("Error al cargar la imagen:", e)
    imagen = None

# Crear la barra de menú
menubar = tk.Menu(root)
menu_archivo = tk.Menu(menubar, tearoff=0)
# --- Nuevo comando para volver a la pantalla de inicio ---
menu_archivo.add_command(label="Inicio", command=mostrar_inicio)
menu_archivo.add_command(label="Salir", command=salir)
menubar.add_cascade(label="Archivo", menu=menu_archivo)

menu_operaciones = tk.Menu(menubar, tearoff=0)
menu_operaciones.add_command(label="Dividir Boletines (Carpeta)", command=mostrar_dividir_boletines)
menu_operaciones.add_command(label="Dividir un PDF (Boletines)", command=mostrar_dividir_un_archivo)
menu_operaciones.add_command(label="Dividir PDFs en Carpeta (Prefijo Personalizado)", command=mostrar_dividir_pdfs_prefijo)
menu_operaciones.add_command(label="Dividir un PDF (Prefijo Personalizado)", command=mostrar_dividir_pdf_unico_prefijo)
menu_operaciones.add_command(label="Convertir PDF a JPG", command=mostrar_pdf_a_jpg)
menu_operaciones.add_command(label="Unir PDFs en un Solo PDF", command=mostrar_unir_pdfs)
menu_operaciones.add_command(label="Unir JPGs en un PDF", command=mostrar_unir_jpgs)
menubar.add_cascade(label="Operaciones", menu=menu_operaciones)

menu_ayuda = tk.Menu(menubar, tearoff=0)
menu_ayuda.add_command(label="Ayuda en Línea", command=ayuda_en_linea)
menu_ayuda.add_command(label="Acerca de la aplicación", command=acerca_de)
menubar.add_cascade(label="Ayuda", menu=menu_ayuda)

root.config(menu=menubar)

# Área principal para mostrar la interfaz (contenido dinámico)
main_frame = ttk.Frame(root)
main_frame.pack(expand=True, fill="both", padx=20, pady=20)

# Mostrar pantalla de inicio
mostrar_inicio()

root.mainloop()
