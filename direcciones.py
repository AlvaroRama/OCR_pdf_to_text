import pandas as pd
import pathlib

fichero_direcciones = r"tablas\direcciones.xlsx"

def dict_direcciones(ruta_absoluta_excel: pathlib.Path)->dict:
    """Lee un fichero Excel con direcciones y devuelve un diccionario
    con NIMA como clave y Nombre como valor.
    """
    direcciones = pd.read_excel(ruta_absoluta_excel, engine="openpyxl")
    
    direcciones = direcciones[["Nima", "Nombre"]].dropna()
    
    direcciones = direcciones.set_index("Nima")["Nombre"].to_dict()
    
    return direcciones


#-----------------------TEST-----------------------

if __name__ == "__main__":
    
    fichero_direcciones = r"tablas\direcciones.xlsx"
    
    ruta_excel = pathlib.Path(fichero_direcciones).expanduser().resolve()
    
    direcciones_dict = dict_direcciones(ruta_excel)
    
    for nima, nombre in direcciones_dict.items():
        
        print(f"{nima}-------{nombre}")