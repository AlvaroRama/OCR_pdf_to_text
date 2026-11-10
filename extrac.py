import os
import zipfile
import tarfile
from pathlib import Path
import re

def get_unique_path(path):
    path = Path(path)
    parent = path.parent
    suffix = path.suffix
    stem = path.stem

    # Si NO existe el archivo original → usarlo tal cual
    if not path.exists():
        return path

    # Buscar archivos con mismo patrón: nombre, nombre_1, nombre_2...
    pattern = re.compile(rf"^{re.escape(stem)}_(\d+){re.escape(suffix)}$")

    max_num = 0
    for f in parent.iterdir():
        match = pattern.match(f.name)
        if match:
            max_num = max(max_num, int(match.group(1)))

    # Siguiente número disponible
    new_name = f"{stem}_{max_num + 1}{suffix}"
    return parent / new_name




def extract_zip(file_path, dest_folder):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            original_path = Path(member)

            if original_path.name == "":
                continue

            target_path = Path(dest_folder) / original_path.name
            target_path = get_unique_path(target_path)

            with zip_ref.open(member) as source, open(target_path, "wb") as target:
                target.write(source.read())


def extract_tar(file_path, dest_folder):
    with tarfile.open(file_path, 'r:*') as tar_ref:
        for member in tar_ref.getmembers():
            if member.isfile():
                original_name = Path(member.name).name
                target_path = Path(dest_folder) / original_name
                target_path = get_unique_path(target_path)

                with tar_ref.extractfile(member) as source, open(target_path, "wb") as target:
                    target.write(source.read())


def extract_all(folder_path, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                if file.endswith(".zip"):
                    print(f"Extrayendo ZIP: {file}")
                    extract_zip(file_path, dest_folder)

                elif file.endswith((".tar", ".tar.gz", ".tgz")):
                    print(f"Extrayendo TAR: {file}")
                    extract_tar(file_path, dest_folder)

            except Exception as e:
                print(f"Error con {file}: {e}")