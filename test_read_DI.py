from ocr.ocr import get_ocr_model2, get_ocr_model3, limpiar_texto_pdf

from doctr.io import DocumentFile 

import re

from clase_validacion import Extraccion_DI

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

# DI`s

dicts_lectura_DIs = []

ruta_dis_fallidos = []

Di_files = list(url.PATH_DI_TEST.glob("*.pdf"))

total_Dis = len(Di_files)

print(f"Detectados {total_Dis} Dis de 1 página. Procesando en bloques de {TAMANO_LOTE}...")

inicio_DIs = time.time()

# Procesado de la carpeta en lotes de 4:

for i in range(0,total_Dis,TAMANO_LOTE):
    
    bloque_archivos = Di_files[i : i + TAMANO_LOTE]
    
    # Empaquetamos los 4 ficheros
    
    paginas_del_lote = []
    
    for file in bloque_archivos:
        
        doc = DocumentFile.from_pdf(str(file))
        
        paginas_del_lote.extend(doc)
        
    # Ejecución en CPU:
    
    result = model(paginas_del_lote)
    
     # Despiezamos el resultado asociando cada página a su archivo.
     
    for file, page_layout in zip(bloque_archivos,result.pages):
        
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
        
        raw = {}
        
        raw_error = {}
        
        for patron,expresion in conts.clase_patrones_DIs.items():
            
            if patron == "nima":
                
                coincidencias = re.findall(expresion, texto_limpio, flags=re.IGNORECASE)
                
                raw[patron] = None
                
                for nima in coincidencias:
                    
                    if nima in diccionario_centros:
                        
                        raw[patron] = nima
                        
                        break
                    
                continue
                
            extraccion = re.search(expresion,texto_limpio, flags=re.IGNORECASE)
           
            raw[patron] = extraccion.group(1) if extraccion else None

        # Validación con Pydantic:
    
        try:

            doc = Extraccion_DI(**raw)

            dicts_lectura_DIs.append({"pdf": file.name,"erroneo": False, "tipo_error": None, **doc.model_dump()})

        except ValidationError as e:
            
            try:
                
                doc_error = DocumentFile.from_pdf(str(file))
                
                result_error = model_error(doc_error)
        
                page_layout_error = result_error.pages[0]
        
                palabras_error = [
                    word.value
                    for block in page_layout_error.blocks
                    for line in block.lines
                    for word in line.words
                ]
        
                texto_crudo_error = " ".join(palabras_error)
                
                texto_limpio_error = limpiar_texto_pdf(texto_crudo_error)
        
                for patron, expresion in conts.clase_patrones_DIs.items():
                    
                    if patron == "nima":
                
                        coincidencias = re.findall(expresion, texto_limpio_error, flags=re.IGNORECASE)

                        raw_error[patron] = None

                        for nima in coincidencias:

                            if nima in diccionario_centros:

                                raw_error[patron] = nima

                                break
                            
                        continue
                    
                    extraccion_error = re.search(expresion, texto_limpio_error, flags=re.IGNORECASE)
                    
                    raw_error[patron] = extraccion_error.group(1) if extraccion_error else None
        
                doc_error_validacion = Extraccion_DI(**raw_error)
        
                dicts_lectura_DIs.append({"pdf": file.name,"erroneo": False,"tipo_error": "recuperado_segundo_pase", **doc_error_validacion.model_dump()})
            
            except ValidationError as e2:
            
                dicts_lectura_DIs.append({"pdf": file.name,"erroneo": True,"tipo_error": e2.errors(),**raw_error})
        
                ruta_dis_fallidos.append(file)

            
fin = time.time()
    
print(f"Bloque de DIs procesado en {fin - inicio_DIs:.2f} segundos.")

for _doc in dicts_lectura_DIs:
    
    print(_doc)
    
for _file in ruta_dis_fallidos:
    
    print(f"Fichero fallido: {_file.name}")



