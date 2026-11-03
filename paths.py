from pathlib import Path
import config as cfg

# Raíz documentos brutos:

BASE_PATH = Path(cfg.config_path)

# Procesado documentos brutos Split_pdf.py:
PATH_ORIGINALES = BASE_PATH / "Originales" # Carpeta donde se depositan los documentos recién descargados, sin procesar.

# Erroneos Split_pdf.py:
PATH_ERRONEOS = BASE_PATH / "Erroneos" # Carpeta donde se depositan los documentos que no se han podido procesar correctamente (ya sea DIs o albaranes).

# Correctos Split_pdf.py y lectura de read_and_classify.py:
PATH_DIS = BASE_PATH / "DIs"
PATH_ALBARANES = BASE_PATH / "Albaranes"
PATH_REVISION_DIS = BASE_PATH / "Revision_DIs"
PATH_REVISION_ALBARANES = BASE_PATH / "Revision_Albaranes"
PATH_REVISION_ALBARANES_SIN_DIs = PATH_REVISION_ALBARANES / "Albaranes_sin_DIs" 

# Base destino clasify_pdf.py:
CLASIFICACION_PATH = Path(r"/Users/alvaro/Library/CloudStorage/OneDrive-ElCorteInglés,S.A/Residuo Cero Region Madrid - Documentos/Documentos Identificación Residuo 0")

# Salidas a excel read_and_classify.py:
OUTPUTS_PATH = Path("outputs")

# Fichero direcciones:
PATH_DIRECCIONES = Path(r"tablas/direcciones.xlsx")

# Test
PATH_DI_TEST = BASE_PATH / "Test" / "Test DIs"
PATH_ALBARANES_TEST = BASE_PATH / "Test" / "Test Albaranes"