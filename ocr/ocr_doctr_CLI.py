import argparse
from pathlib import Path

from doctr.io import DocumentFile
from doctr.models import ocr_predictor


def ocr_pdf_to_text(pdf_path: Path, assume_straight_pages: bool = True) -> tuple[str, dict]:
    """
    Ejecuta OCR con docTR sobre un PDF y devuelve:
      - texto plano (result.render())
      - estructura exportable (result.export()) para debug / futuros parseos
    """
    doc = DocumentFile.from_pdf(str(pdf_path))
    model = ocr_predictor(pretrained=True, assume_straight_pages=assume_straight_pages)
    result = model(doc)

    text = result.render()
    exported = result.export()
    return text, exported


def main():
    parser = argparse.ArgumentParser(description="OCR con docTR sobre PDF escaneado (texto plano).")
    parser.add_argument("pdf", type=str, help="Ruta al PDF escaneado")
    parser.add_argument("-o", "--out", type=str, default=None, help="Ruta al TXT de salida (por defecto ./outputs/<nombre>.txt)")
    parser.add_argument("--json", action="store_true", help="También guarda la salida estructurada en JSON")
    parser.add_argument("--no-straight", action="store_true", help="No asumir páginas rectas (mejor si el escaneo está torcido)")
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {pdf_path}")

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    out_txt = Path(args.out).expanduser().resolve() if args.out else out_dir / f"{pdf_path.stem}.txt"
    out_json = out_dir / f"{pdf_path.stem}.json"

    text, exported = ocr_pdf_to_text(
        pdf_path,
        assume_straight_pages=(not args.no_straight))

    out_txt.write_text(text, encoding="utf-8")
    print(f"Texto guardado en: {out_txt}")

    if args.json:
        import json
        out_json.write_text(json.dumps(exported, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON guardado en:  {out_json}")


if __name__ == "__main__":
    
    main()