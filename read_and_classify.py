from datetime import datetime
import shutil

from ocr.ocr import get_ocr_model2, get_ocr_model3, limpiar_texto_pdf

from doctr.io import DocumentFile 

from split_pdf import move_to_processed

import re

from clase_validacion import Extraccion_Albaran, Extraccion_DI

from pydantic import ValidationError

import constantes as conts

import paths as url

import pandas as pd

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

Di_files = list(url.PATH_DIS.glob("*.pdf"))

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

# Albaranes

dicts_lectura_albaranes = []

rutas_albaranes_erroneos = []

Albaran_files = list(url.PATH_ALBARANES.glob("*.pdf"))

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
        
        for patron,expresion in conts.clase_patrones_Albaranes.items():
            
            extraccion = re.search(expresion,texto_limpio, flags=re.IGNORECASE)
           
            raw[patron] = extraccion.group(1) if extraccion else None
            
        # Validación con Pydantic:
    
        try:
        
            if None in raw.values(): # Si falta algún dato, lo consideramos erróneo directamente (aunque no entre en la validación de Pydantic, que es más estricta y puede fallar por otros motivos)
            
                print(f"[DEBUG] {file.name} → {raw}")

            doc = Extraccion_Albaran(**raw)
        
            dicts_lectura_albaranes.append({"pdf": file.name,"erroneo": False, "tipo_error": None, **doc.model_dump()})
        
        except ValidationError as e:
        
            dicts_lectura_albaranes.append({"pdf": file.name,"erroneo": True, "tipo_error": e.errors(), **raw})
        
            rutas_albaranes_erroneos.append(file)

fin = time.time()

print(f"Bloque de Albaranes procesado en {fin - inicio_albaranes:.2f} segundos.")

print("Resumen de lectura")

print(f"DIs correctos en lectura: {len(dicts_lectura_DIs)-len(ruta_dis_fallidos)}")

print(f"DIs erróneos en lectura: {len(ruta_dis_fallidos)}")

print(f"Albaranes correctos en lectura: {len(dicts_lectura_albaranes)-len(rutas_albaranes_erroneos)}")

print(f"Albaranes erróneos en lectura: {len(rutas_albaranes_erroneos)}")

#----------------------- Tratamiento de dataframes -----------------------#

url.OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

# Tratamiento df de DIs:

if len(dicts_lectura_DIs) > 0:

    df_lectura_DIs = pd.DataFrame(dicts_lectura_DIs)

    df_lectura_DIs["Centro Origen"] = df_lectura_DIs["nima"].map(diccionario_centros).fillna("error")

    df_lectura_DIs["Residuo"] = df_lectura_DIs["ler"].map(conts.diccionario_LER_RESIDUO ).fillna("error")

    df_lectura_DIs["residuoDestino"] = df_lectura_DIs["ler"].map(conts.diccionario_LER_Carpteta_destino).fillna("error")
    
    mask_DIs_validos = ~df_lectura_DIs["erroneo"]
    
    mask_DIS_duplicados = df_lectura_DIs["di"].duplicated(keep=False)

    df_lectura_DIs["di_duplicado"] = mask_DIs_validos & mask_DIS_duplicados
    

    if not df_lectura_DIs["di"].is_unique:

        print("Hay DIs duplicados")
        
    # Df_DIs_Ordenado y renombrado columnas para salida a excel:
    
    df_lectura_DIs_ordenado = df_lectura_DIs[~df_lectura_DIs["erroneo"]].copy() # Solo ordenamos los correctos (los erróneos ya los movimos a revisión)
    
    columnas_ordenadas_dis=["Centro Origen", "fecha_inicio_traslado","Residuo", "cantidad_aceptada","di","numero_albaran_DI"]
    
    df_lectura_DIs_ordenado = df_lectura_DIs_ordenado[columnas_ordenadas_dis].rename(columns=conts.Renombrado_columnas_df_lectura)
    
    # Salida a excel
    
    output_excel_DIs = url.OUTPUTS_PATH / f"lectura_DIs_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.xlsx"

    with pd.ExcelWriter(output_excel_DIs, engine="openpyxl") as writer:
        
        df_lectura_DIs_ordenado.to_excel(writer, index=False, sheet_name="Envíos")
        
        df_lectura_DIs.to_excel(writer, index=False, sheet_name="Raw") # Guardamos también la versión sin ordenar ni renombrar para tener toda la información de errores

else:

    print("No se han leído DIs correctamente, no se genera dataframe.")
    
    df_lectura_DIs = pd.DataFrame()
    
    
# Tratamiento df de albaranes:

if len(dicts_lectura_albaranes) > 0:

    df_lectura_albaranes = pd.DataFrame(dicts_lectura_albaranes)
    
    # Obtención del centro en el dataframe de albaranes:
    
    if not df_lectura_albaranes["numero_albaran_alba"].is_unique:
    
        print("Hay números de albarán duplicados")
    
    if not df_lectura_DIs.empty:

        df_lookup = df_lectura_DIs.groupby("numero_albaran_DI")["Centro Origen"].first().reset_index()

        df_lectura_albaranes = df_lectura_albaranes.merge(df_lookup, left_on="numero_albaran_alba", right_on="numero_albaran_DI", how="left")
        
        mask_albaranes_validos = ~df_lectura_albaranes["erroneo"]
    
        mask_albaranes_duplicados = df_lectura_albaranes["numero_albaran_alba"].duplicated(keep=False)

        df_lectura_albaranes["Albarán_duplicado"] = mask_albaranes_validos & mask_albaranes_duplicados
        
        # Deteccion de albaranes sin DIs asociados (número de albarán no encontrado en DIs):
        
        df_lectura_albaranes.loc[df_lectura_albaranes["numero_albaran_DI"].isna(), "numero_albaran_DI"] = "DIs_no_encontrados"

    # df_lectura_albaranes Ordenado y renombrado columnas para salida a excel:
    
        df_lectura_albaranes_ordenado = df_lectura_albaranes[~df_lectura_albaranes["erroneo"]].copy() # Solo ordenamos los correctos (los erróneos ya los movimos a revisión)
    
        columnas_ordenadas_albaranes=["numero_albaran_alba", "Centro Origen", "fecha_albaran"]

        df_lectura_albaranes_ordenado.dropna(subset=["numero_albaran_DI"], inplace=True) # Eliminamos filas sin número de albarán en df_DIs

        df_lectura_albaranes_ordenado = df_lectura_albaranes_ordenado[columnas_ordenadas_albaranes].rename(columns=conts.Renombrado_columnas_df_lectura)

    # Salida a excel
    
    output_excel_albaranes = url.OUTPUTS_PATH / f"lectura_albaranes_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.xlsx"
    
    
    with pd.ExcelWriter(output_excel_albaranes, engine="openpyxl") as writer:
        
        if not df_lectura_albaranes_ordenado.empty: # Hay que cambiarlo al DF de DIs
    
            df_lectura_albaranes_ordenado.to_excel(writer, index=False, sheet_name="Albaranes")

        else:
            
            print("Fichero de albaranes sin datos cruzados")
        
        df_lectura_albaranes.to_excel(writer, index=False, sheet_name="Raw")
        
else:
    
    print("No se han leído albaranes correctamente, no se genera dataframe.")
    
    df_lectura_albaranes = pd.DataFrame()
    
        
#----------------------- Movimiento DIs y albaranes erróneos a revisión -----------------------#
        
# Movimiento DIs erróneos a revisión:

if ruta_dis_fallidos:
    
    for di_fallido in ruta_dis_fallidos:
        
        if di_fallido.exists():
        
            move_to_processed(di_fallido, url.PATH_REVISION_DIS)
            
if rutas_albaranes_erroneos:
    
    for albaran_erroneo in rutas_albaranes_erroneos:
        
        if albaran_erroneo.exists():
        
            move_to_processed(albaran_erroneo, url.PATH_REVISION_ALBARANES)

#----------------------- Clasificacion de documentos -----------------------#

gestor = "FCC AMBITO, S.A"

# Clasificacion DIs por carpeta:

dis_clasificados_correctos = 0

dis_clasificados_erroneos = 0

destino_clasificacion = url.CLASIFICACION_PATH

if not df_lectura_DIs.empty:

    df_lectura_DIs = df_lectura_DIs[~df_lectura_DIs["erroneo"]] # Solo clasificamos los correctos (los erróneos ya los movimos a revisión)
    
    for row in df_lectura_DIs.to_dict(orient="records"):
        
        nombre_archivo = row["pdf"]
        
        ruta_origen = url.PATH_DIS / nombre_archivo
        
        di = row["di"] if pd.notna(row["di"]) else "error"
        
        centro = row["Centro Origen"] if pd.notna(row["Centro Origen"]) else "error"
        
        residuo = row["residuoDestino"] if pd.notna(row["residuoDestino"]) else "error"
        
        fecha = row["fecha_inicio_traslado"]
        
        if pd.notna(fecha):
            
            año = fecha.year
            
            mes_num= fecha.month
            
            mes = conts.diccionario_meses.get(mes_num, "error")
        
        else:
            
            año = "error"
            
            mes = "error"
            
        if ruta_origen.exists():
        
            if any(v == "error" for v in [di, centro, residuo, año, mes]):
            
                ruta_destino = url.PATH_REVISION_DIS
                
                move_to_processed(ruta_origen, ruta_destino)
                
                dis_clasificados_erroneos += 1
    
            else:
                
                ruta_destino = destino_clasificacion / centro / gestor / residuo / str(año) / mes
                
                nombre_archivo_destino = f"{di}.pdf"
    
                move_to_processed(ruta_origen, ruta_destino, nombre_archivo_destino)
                
                dis_clasificados_correctos += 1

# Clasificacion albaranes por carpeta:

albaranes_clasificados_correctos = 0

albaranes_clasificados_erroneos = 0

albaranes_sin_DIs = 0

if not df_lectura_albaranes.empty:
    
    df_lectura_albaranes = df_lectura_albaranes[~df_lectura_albaranes["erroneo"]] # Solo clasificamos los correctos (los erróneos ya los movimos a revisión)

    for row in df_lectura_albaranes.to_dict(orient="records"):

        nombre_archivo = row["pdf"]

        ruta_origen = url.PATH_ALBARANES / nombre_archivo

        numero_albaran = row["numero_albaran_alba"] if pd.notna(row["numero_albaran_alba"]) else "error"
        
        numero_albaran_DI = row["numero_albaran_DI"]
            
        centro = row["Centro Origen"] if pd.notna(row["Centro Origen"]) else "error"
        
        fecha = row["fecha_albaran"]
        
        if pd.notna(fecha):
            
            año = fecha.year
            
            mes_num = fecha.month
            
            mes = conts.diccionario_meses.get(mes_num, "error")
        
        else:
            
            año = "error"
            
            mes = "error"

        if ruta_origen.exists():

            if any(v == "error" for v in [numero_albaran, centro, año, mes]): # SI FALLA EL MERGE CON LOS DIs, EL CENTRO SALE ERROR, ASÍ QUE LOS MOVEMOS A REVISIÓN DIRECTAMENTE

                ruta_destino = url.PATH_REVISION_ALBARANES

                move_to_processed(ruta_origen, ruta_destino)

                albaranes_clasificados_erroneos += 1
                
            elif numero_albaran_DI == "DIs_no_encontrados":
                
                nombre_archivo_destino = f"{numero_albaran}.pdf"
                
                ruta_destino = destino_clasificacion / centro / gestor / "Albaranes" / str(año) / mes
                
                ruta_destino.mkdir(parents=True, exist_ok=True) 
                
                shutil.copy(ruta_origen, ruta_destino / nombre_archivo_destino)

                ruta_destino_copia = url.PATH_REVISION_ALBARANES_SIN_DIs
                
                move_to_processed(ruta_origen, ruta_destino_copia, nombre_archivo_destino)

                albaranes_sin_DIs += 1
                
            else:
                
                ruta_destino = destino_clasificacion / centro / gestor / "Albaranes" / str(año) / mes
                
                nombre_archivo_destino = f"{numero_albaran}.pdf"
                
                move_to_processed(ruta_origen, ruta_destino, nombre_archivo_destino)
                    
                albaranes_clasificados_correctos += 1
                
print("Resumen de clasificación")

print(f"DIs clasificados correctamente: {dis_clasificados_correctos}")

print(f"DIs clasificados con error (movidos a revisión): {dis_clasificados_erroneos}")

print(f"Albaranes clasificados correctamente: {albaranes_clasificados_correctos}")

print(f"Albaranes clasificados con error (movidos a revisión): {albaranes_clasificados_erroneos}")

print(f"Albaranes sin DIs asociados: {albaranes_sin_DIs}")