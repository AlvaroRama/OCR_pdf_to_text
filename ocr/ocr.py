from doctr.models import ocr_predictor
from doctr.io import DocumentFile
from pathlib import Path
import json
import unicodedata


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
    )


def get_ocr_model3(assume_straight_pages: bool = True):
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
)


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