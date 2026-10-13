from doctr.models import ocr_predictor
from doctr.io import DocumentFile
import paths as url
import time
from ocr.ocr import limpiar_texto_pdf
import constantes as conts
from clase_validacion import Extraccion_DI
from pydantic import ValidationError
import re

path_pdf = url.PATH_DI_TEST
    
print("Cargando modelo")


model = ocr_predictor(
    det_arch="fast_base",
    reco_arch="parseq",
    pretrained=True,
    pretrained_backbone=True,
    assume_straight_pages=True,
    preserve_aspect_ratio=True,
    symmetric_pad=True,
    export_as_straight_boxes=False,
    detect_orientation=False,
    straighten_pages=False,
    detect_language=False,
    det_bs=4,
    reco_bs=4,
)

files = list(path_pdf.glob("*.pdf"))

total_archivos = len(files)

print(f"Detectados {total_archivos} archivos de 1 página. Procesando en bloques de 4...")

inicio = time.time()

TAMANO_LOTE = 4

dicts_lectura_DIs = []

textos_extraidos = []

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
        
        textos_extraidos.append(text_limpio)
        
        raw = {}
        
        for patron, expresion in conts.clase_patrones_DIs.items():
            
            extraccion = re.search(expresion,text_limpio, flags=re.IGNORECASE)
            
            raw[patron] = extraccion.group(1) if extraccion else None
            
        try:

            doc = Extraccion_DI(**raw)

            dicts_lectura_DIs.append({"pdf": file.name,"erroneo": False, "tipo_error": None, **doc.model_dump()})

        except ValidationError as e:

            dicts_lectura_DIs.append({"pdf": file.name,"erroneo": True, "tipo_error": e.errors(), **raw})

        
        
    print(f"=== Bloque de {len(bloque_archivos)} archivos procesado en {time.time() - t_bloque:.2f} segundos ===\n")
     
fin = time.time()
print("=======================================")
print(f"Tiempo TOTAL para los {total_archivos} archivos: {fin - inicio:.2f} segundos")
print("=======================================")
for expresion,texto in zip(textos_extraidos,dicts_lectura_DIs):
    print("-" * 20)
    print(f"Expresión: {expresion}")
    print(f"Texto extraído: {texto}")
    print("-" * 20)