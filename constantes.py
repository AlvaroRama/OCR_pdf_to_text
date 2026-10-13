# Patrones de expresiones regulares.

clase_patrones_DIs = {
    "di": r"documento\s+identif\.?.{0,40}?(?P<valor>D[I]?\s*\d+)",
    "numero_albaran_DI":r"\bnumero\s+albaran\s*[:\-]?\s*(?P<val>\d+)\b",
    "fecha_inicio_traslado": r"\bfecha\s+de\s+inicio\s+traslado\s*[:\-]?\s*(?P<val>\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\b",
    "ler": r"\bLER\b\s*[:\-]?\s*(?P<val>\d{6})\b",
    "nima": r"\bNIMA\s*[:\-]?\s*(?P<val>\d{10})\b",
    "cantidad_aceptada": r"\bcantidad\s+aceptada\b\s*[:\-]?\s*(?P<raw>[\d.,]+)",
}

clase_patrones_Albaranes = {
    "numero_albaran_alba": r"\bnumero\s+de\s+albaran\s*[:\-]?\s*(?P<val>\d+)\b",
    "fecha_albaran": r"\bfecha\s*[:\-]?\s*(?P<val>\d{1,2}/\d{1,2}/\d{4})\b",
}
    
# Cosntantes para tablas y clasificación:

diccionario_LER_RESIDUO = {
    "200101": "CARTÓN - 200101 - 150101 - 191201",
    "150102":"R - PLÁSTICOS BLANDOS - 200139 150102 150106 191204",
    "200139": "R - EPS - 150102 - 200139 - 150106",
    "150106": "R - ENVASES PLÁSTICOS, MIXTOS Y METÁLICOS - 150102 150106 150104"
}

diccionario_LER_Carpteta_destino = {
    "200101": "CARTÓN",
    "150102":"PLÁSTICOS BLANDOS",
    "200139": "EPS",
    "150106": "ENVASES",
    }

diccionario_meses = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

Renombrado_columnas_df_lectura = {
    "pdf": "PDF",
    "di": "Documento de Identificación",
    "nima": "NIMA",
    "ler": "LER",
    "fecha_inicio_traslado": "Fecha Envío Almacén",
    "Centro Origen": "Centro Origen",
    "Residuo": "Residuo",
    "residuoDestino": "Residuo Destino",
    "erroneo": "Erróneo",
    "tipo_error": "Tipo Error",
    "di_duplicado": "DI Duplicado",
    "cantidad_aceptada": "Cantidad",
    "numero_albaran_alba": "Número de Albarán",
    "numero_albaran_DI": "Número de Albarán DI"
}

patrones_antiguos  = {"di": r"documento\s+identif\.?\s*(?P<valor>DI\s*\d+)"}