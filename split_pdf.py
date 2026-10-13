from __future__ import annotations
from pathlib import Path
import shutil
import unicodedata
from enum import Enum
from pypdf import PdfReader, PdfWriter
from typing import Optional
import paths as url

class DocType(str, Enum):
    ALB = "ALB" # Albaranes
    ID = "ID" # Documento identificación
    UNK = "UNK" # Desconocido
    
ALBARAN_KEYWORDS = {
    "albaranes", # Caso conocido
    "as", # Caso conocido
    "albaran",
    "alb",
}

DI_KEYWORDS = {
    "doc_ident", # Caso conocido
    "di", # Caso conodico
    "documento_identificacion",
}

# CARPETAS PARA LOTES DE EXTRACCION!

def normalize_name (path: Path)-> str:
    """
    Devuelve un nombre 'comparable':
    - en minúsculas
    - sin acentos
    - con separadores simplificados
    """
    
    s  = path.stem.lower() # sin extension
    
    s = unicodedata.normalize("NFKD", s)
    
    s = "".join(ch for ch in s if not unicodedata.combining(ch)) # quita tildes
    
    s = s.replace(" ","_").replace("-","_")
    
    return s


def classify_multipage_pdf (pdf_path: Path) -> DocType:
    """
    Clasifica un PDF multipágina según su NOMBRE:
    - contiene 'albaranes'  -> ALB
    - contiene 'doc_ident'  -> ID
    - ambos o ninguno       -> UNK
    """
    
    name = normalize_name(pdf_path)
    
    has_alb = any(k in name for k in ALBARAN_KEYWORDS)
    
    has_id = any(k in name for k in DI_KEYWORDS)
    
    if has_alb and not has_id:
        
        return DocType.ALB
    
    if has_id and not has_alb:
        
        return DocType.ID
    
    return DocType.UNK


def split_pdf_to_pages(pdf_path: Path, out_dir: Path) -> list[Path]:
    """
    Divide un PDF multipágina en PDFs de 1 página.
    Devuelve la lista de rutas generadas.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(pdf_path))
    
    created: list[Path] = []
    
    prefix = pdf_path.stem

    for i, page in enumerate(reader.pages, start=1):
        
        writer = PdfWriter()
        
        writer.add_page(page)

        out_path = out_dir / f"{prefix}_{i:03d}.pdf"
        
        with open(out_path, "wb") as f:
            
            writer.write(f)

        created.append(out_path)

    return created


def move_to_processed(pdf_path: Path, processed_dir: Path, pdf_name: Optional[str] = None) -> None:
    
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    destino = processed_dir / (pdf_name if pdf_name else pdf_path.name)
    
    base = destino.stem
    
    ext = destino.suffix
    
    contador = 1
    
    destino_final = destino
    
    while destino_final.exists():
        
        destino_final = processed_dir / f"{base}_dup{contador}{ext}"
        
        contador += 1
    
    shutil.move(str(pdf_path), str(destino_final))


# Tratamiento de documentos recibidos:

if __name__ == "__main__":
    
    ficheros_correctos = 0
    
    ficheros_erroneos = 0
    
    ficheros_correctos_movidos = 0
    
    ficheros_erroneos_movidos = 0 
    
    total_ficheros = len(list(url.BASE_PATH.glob("*.pdf")))
    
    print(f"Procesando {total_ficheros} ficheros...")

    for file in url.BASE_PATH.glob("*.pdf"): 

        if not file.is_file():

            continue

        # Clasificación fichero original: DI, Albarán o erroneo.
        
        tipo_documento = classify_multipage_pdf(file)

        try:
            
            match tipo_documento:

                case DocType.ALB:
                    
                    output_path = url.PATH_ALBARANES

                case DocType.ID:
                    
                    output_path = url.PATH_DIS

                case DocType.UNK:
                    
                    ficheros_erroneos += 1
                    
                    move_to_processed(file, url.PATH_ERRONEOS)
                    
                    ficheros_erroneos_movidos +=1
                    
                    continue
        
        # Descomposición fichero original y traslado de subficheros a carpetas.
        
            split_pdf_to_pages(file, output_path)
            
            ficheros_correctos += 1
            
            if file.exists():
                
        # Traslado de fichero original a carpeta originales.
                
                move_to_processed(file, url.PATH_ORIGINALES)
                
                ficheros_correctos_movidos += 1

        except Exception as e:

            print(f"[ERROR] {file.name}: {e}")
            
            ficheros_erroneos += 1

            if file.exists():
                
                move_to_processed(file, url.PATH_ERRONEOS)
                
                ficheros_erroneos_movidos +=1
                       
    print(
    f"Proceso finalizado\n"
    f"ficheros_correctos -> {ficheros_correctos}\n"
    f"ficheros_correctos_movidos a PATH_DIS / PATH_ALBARANES -> {ficheros_correctos_movidos}\n"
    f"ficheros_erroneos -> {ficheros_erroneos}\n"
    f"ficheros_erroneos_movidos a PATH_ERRONEOS -> {ficheros_erroneos_movidos}\n"
    )
    