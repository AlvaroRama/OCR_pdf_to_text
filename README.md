# Lectura de documentos digitalizados para posterior tratamiento

Extracción de todo el texto de documentos de identificación de traslado de residuos para posterior clasificación y obtener la información estructurada en fichero Excel.

## Características
* **Trasformacion de fichero pdf multipágina en documentos unitarios:** 
* **Extracción de texto del PDF digitalizado:** Empleo de doctr para extracción de texto del documento.
* **Tratamiento y transformación del texto extraido:** Uso de expresiones regulares junto con validación de Pydantic para validar lo extraido.
* **Estructuración con Pandas:** Modifica y transforma rápidamente toda la información extraida.
* **Clasificación de documentos y salida:** Permite clasificación en carpetas según la estructura elegida con reporte en fichero excel.

## Requisitos Previos

* **Python 3.9+**

## Configuración e Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/AlvaroRama/OCR_pdf_to_text](https://github.com/AlvaroRama/OCR_pdf_to_text)
   cd OCR_pdf_to_text
   ```

2. **Crear y activar un entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar y/o modificar los ficheros de configuración de path y direcciones.**

5. **Configurar y/o modificar los ficheros de configuración de tus gestores de residuo.**

## Uso

Asegurate de mantener actualizado el fichero de direcciones, split y read_and_classify.

## Estructura del Repositorio

```text
├── ocr/                           # OCR con DocTR
│   ├── ocr.py
│   └── ocr_doctr_CLI.py
│
├── outputs/                       # Resultados generados
│
├── tablas/                        # Tablas y datos de negocio
│
├── split_pdf.py                   # División de PDFs multipágina
├── read_and_classify.py           # Lectura y clasificación documental
├── clase_validacion.py            # Validación de datos extraídos
├── direcciones.py                 # Procesamiento de direcciones
├── constantes.py                  # Constantes y patrones
├── paths.py                       # Gestión de rutas
├── models_charts.py               # Modelos y gráficos auxiliares
├── test_read_DI.py                # Pruebas
├── README.md
└── requirements.txt
```

## Comentarios:

* Puedes modificar tu extractor de texto de los documentos pdf al gusto.
* Combina diferentes modelos para obtener mejores resultados u optimizar rendimiento.
