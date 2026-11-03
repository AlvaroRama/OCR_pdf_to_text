from doctr.models import ocr_predictor
from doctr.io import DocumentFile
from pathlib import Path
import json
import unicodedata
import time
import torch

#--------------------------- Model ---------------------------#



def get_ocr_model(assume_straight_pages: bool = True):
    return ocr_predictor(
        det_arch="fast_base",
        reco_arch="crnn_vgg16_bn",
        pretrained=True,         
        pretrained_backbone=True,
        assume_straight_pages=assume_straight_pages,
        preserve_aspect_ratio=True,
        symmetric_pad=True,
        export_as_straight_boxes=False,
        detect_orientation=False,
        straighten_pages=False,
        detect_language=False,
    )


def get_ocr_model2(assume_straight_pages: bool = True):
    device = torch.device("mps")
    return ocr_predictor(
        det_arch="db_mobilenet_v3_large",
        reco_arch="crnn_mobilenet_v3_large",
        pretrained=True,
        pretrained_backbone=True,
        assume_straight_pages=assume_straight_pages,
        preserve_aspect_ratio=True,
        symmetric_pad=True,
        export_as_straight_boxes=False,
        detect_orientation=False,
        straighten_pages=False,
        detect_language=False,
        det_bs=4,   # batch size detección
        reco_bs=4,  # batch size reconocimiento
).to(device)


def get_ocr_model3(assume_straight_pages: bool = True):
    device = torch.device("mps")
    return ocr_predictor(
        det_arch="fast_base",
        reco_arch="parseq",
        pretrained=True,
        pretrained_backbone=True,
        assume_straight_pages=assume_straight_pages,
        preserve_aspect_ratio=True,
        symmetric_pad=True,
        export_as_straight_boxes=False,
        detect_orientation=False,
        straighten_pages=False,
        detect_language=False,
).to(device)


def ocr_pdf_1page_to_text(pdf_path: Path, model) -> str:
    doc = DocumentFile.from_pdf(str(pdf_path))
    result = model(doc)
    return result.render()


#--------------------------- Debug ---------------------------#


def ocr_pdf_1page_export(pdf_path: Path, model) -> dict:
    doc = DocumentFile.from_pdf(str(pdf_path))
    result = model(doc)
    return result.export()

def save_debug_json(exported: dict, out_json: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(exported, ensure_ascii=False, indent=2), encoding="utf-8")
    
    
#--------------------------- Utils ---------------------------#

def limpiar_texto_pdf(texto_plano_pdf: str, minusculas: bool = False) -> str:
    """
    Limpia el texto de un PDF: elimina espacios extra y quita tildes.
    """
    # Normaliza espacios (elimina saltos de línea y tabulaciones dobles)
    t = " ".join(texto_plano_pdf.split())

    # Quita tildes usando normalización NFKD
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))

    return t.lower() if minusculas else t

if __name__ == "__main__":

    path_pdf = Path(r"C:\Users\66439464\OneDrive - El Corte Inglés, S.A\DIs_descargados\negocios_practicos\Revision_DIs")
    
    print("Cargando modelo")
    
    model = ocr_predictor(
        det_arch="db_mobilenet_v3_large",   
        reco_arch="crnn_mobilenet_v3_large", 
        pretrained=True,
        assume_straight_pages=True,
        det_bs=4,  # Procesamiento nativo en lotes de 4
        reco_bs=4
    )
    
    files = list(path_pdf.glob("*.pdf"))
    total_archivos = len(files)
    print(f"Detectados {total_archivos} archivos de 1 página. Procesando en bloques de 4...")

    inicio = time.time()
    TAMANO_LOTE = 4

    # Procesamos la carpeta saltando de 4 en 4
    for i in range(0, total_archivos, TAMANO_LOTE):
        t_bloque = time.time()
        bloque_archivos = files[i : i + TAMANO_LOTE]
        
        # Empaquetamos las páginas de los 4 archivos
        paginas_del_lote = []
        for file in bloque_archivos:
            doc = DocumentFile.from_pdf(str(file))
            paginas_del_lote.extend(doc)  
            
        # Ejecución paralela en CPU
        result = model(paginas_del_lote)
        
        # Despiezamos el resultado asociando cada página a su archivo
        for file, page_layout in zip(bloque_archivos, result.pages):
            
            palabras = [
                word.value 
                for block in page_layout.blocks 
                for line in block.lines 
                for word in line.words
            ]
            
            texto_crudo = " ".join(palabras)
            text_limpio = limpiar_texto_pdf(texto_crudo)
            
            print(f"-> Procesado: {file.name}")
            print("-" * 50)
            print(text_limpio)
            print("-" * 50)
            
        print(f"=== Bloque de {len(bloque_archivos)} archivos procesado en {time.time() - t_bloque:.2f} segundos ===\n")
         
    fin = time.time()
    print("=======================================")
    print(f"Tiempo TOTAL para los {total_archivos} archivos: {fin - inicio:.2f} segundos")
    print("=======================================")


