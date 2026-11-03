from ocr.ocr import get_ocr_model2, get_ocr_model3, limpiar_texto_pdf

from doctr.io import DocumentFile 

import re

from clase_validacion import Extraccion_Albaran

from pydantic import ValidationError

import constantes as conts

import paths as url

from direcciones import dict_direcciones

import time

# Generacion diccionario de centros

diccionario_centros = dict_direcciones(url.PATH_DIRECCIONES)

# Carga del modelo OCR:

print("Cargando configuracion de los modelos")

model = get_ocr_model2()

model_error = get_ocr_model3()

TAMANO_LOTE = 4

#----------------------- Lectura de ficheros OCR y extracción de datos -----------------------#

dicts_lectura_albaranes = []

rutas_albaranes_erroneos = []

Albaran_files = list(url.PATH_ALBARANES_TEST.glob("*.pdf"))

total_albaranes = len(Albaran_files)

print(f"Detectados {total_albaranes} Albaranes de 1 página. Procesando en bloques de {TAMANO_LOTE}...")

inicio_albaranes = time.time()

# Procesado de la carpeta en lotes de 4:

for i in range(0,total_albaranes,TAMANO_LOTE):
    
    bloque_archivos = Albaran_files[i : i + TAMANO_LOTE]
    
    # Empaquetamos los 4 ficheros
    
    paginas_del_lote = []
    
    for file in bloque_archivos:
        
        doc = DocumentFile.from_pdf(str(file))
        
        paginas_del_lote.extend(doc)
        
    # Ejecución en GPU:
    
    result = model(paginas_del_lote)
    
     # Despiezamos el resultado asociando cada página a su archivo.
     
    for file, page_layout in zip(bloque_archivos,result.pages):

        print(f'Fichero {file}')
        
        # Extraemos las palabras directamente en una lista plana en una sola línea de código.
        palabras = [
            word.value
            for block in page_layout.blocks
            for line in block.lines
            for word in line.words
        ]
        
        # Convierto la lista en un String.
        texto_crudo = " ".join(palabras)
        
        # Limpieza texto.
        texto_limpio = limpiar_texto_pdf(texto_crudo)

        print('------TEXTO------')

        print(texto_limpio)
        
        raw = {}
        
        for patron,expresion in conts.clase_patrones_Albaranes.items():

            if patron == "fecha_albaran":

                extraccion = re.findall(expresion,texto_limpio)
           
                raw[patron] = extraccion[0] if extraccion else None

            else:    
            
                extraccion = re.search(expresion,texto_limpio, flags=re.IGNORECASE)
           
                raw[patron] = extraccion.group(1) if extraccion else None
            
        # Validación con Pydantic:
    
        try:
        
            if None in raw.values(): # Si falta algún dato, lo consideramos erróneo directamente (aunque no entre en la validación de Pydantic, que es más estricta y puede fallar por otros motivos)
            
                print(f"[DEBUG] {file.name} → {raw}")

            doc = Extraccion_Albaran(**raw)
        
            dicts_lectura_albaranes.append({"pdf": file.name,"erroneo": False, "tipo_error": None, **doc.model_dump()})

            print(raw)
        
        except ValidationError as e:
        
            dicts_lectura_albaranes.append({"pdf": file.name,"erroneo": True, "tipo_error": e.errors(), **raw})
        
            rutas_albaranes_erroneos.append(file)

fin = time.time()

print(f"Bloque de Albaranes procesado en {fin - inicio_albaranes:.2f} segundos.")

