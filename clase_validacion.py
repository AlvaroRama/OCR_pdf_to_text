from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re

class Extraccion_DI(BaseModel):
    
    di: str = Field(..., description="Documento de Identificación (DI + dígitos)")
    
    numero_albaran_DI: str = Field(..., description="Número de albarán (solo dígitos)")
    
    fecha_inicio_traslado: date = Field(..., description="Fecha de inicio de traslado")
    
    ler: str = Field(..., description="Código LER (6 dígitos)")
    
    nima: str = Field(..., description="NIMA (10 dígitos)")
    
    cantidad_aceptada: Optional[float] = Field(
        default=None,
        ge=0,
        description="Cantidad aceptada (>= 0). Puede ser None si no se lee."
    )

    # --- Validadores / normalizadores ---

    @field_validator("di")
    @classmethod
    
    def validar_di(cls, v: str) -> str:
        
        LONGITUD_DI = 25
        
        v = v.replace(" ", "").upper()
        
        if v.startswith("D1"):
            
            v = "DI" + v[2:]
            
        if v.startswith("DI1"):
            
            v = "DI" + v[3:]
            
        if not (v.startswith("DI3")):
            
            raise ValueError("DI inválido (debe ser 'DI' + dígitos)")
        
        if len(v) != LONGITUD_DI:
                    
            raise ValueError(f"DI inválido (debe tener {LONGITUD_DI} caracteres)")
        
        return v


    @field_validator("numero_albaran_DI")
    @classmethod
    
    def validar_numero_albaran(cls, v: str) -> str:
        
        v = v.strip()
        
        if not v.isdigit():
            
            raise ValueError("Número de albarán debe contener solo dígitos")
        # Si es fijo (por ejemplo 8 dígitos), puedes reforzarlo:
        # if len(v) != 8: raise ValueError("Número de albarán debe tener 8 dígitos")
        return v


    @field_validator("fecha_inicio_traslado", mode="before")
    @classmethod
    
    def parsear_fecha(cls, v):
        
        if isinstance(v, date):
            
            return v
        
        if isinstance(v, str):
            
            v = v.strip()
            
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"):
                
                try:
                    
                    return datetime.strptime(v, fmt).date()
                
                except ValueError:
                    
                    pass
                
        raise ValueError("Fecha inválida (esperado dd/mm/aaaa)")


    @field_validator("ler")
    @classmethod
    
    def validar_ler(cls, v: str) -> str:
        
        v = v.replace(" ", "")
        
        if not (v.isdigit() and len(v) == 6):
            
            raise ValueError("LER inválido (debe tener 6 dígitos)")
        
        return v


    @field_validator("nima")
    @classmethod
    
    def validar_nima(cls, v: str) -> str:
        
        v = v.replace(" ", "")
        
        if not (v.isdigit() and len(v) == 10):
            
            raise ValueError("NIMA inválido (debe tener 10 dígitos)")
        
        return v


    @field_validator("cantidad_aceptada", mode="before")
    @classmethod  
    def parsear_float_es(cls, v):
        
        if v is None or v == "":
            
            return None

        if isinstance(v, (int, float)):
            
            return float(v)

        s = str(v).strip().replace(" ", "")
        
        if "," in s:
            
            s = s.replace(".", "").replace(",", ".")

        try:
            return float(s)
        
        except ValueError:
            
            return None

        
class Extraccion_Albaran(BaseModel):
    numero_albaran_alba: str = Field(..., description="Número de albarán (solo dígitos)")
    fecha_albaran: date = Field(..., description="Fecha del albarán")

    @field_validator('numero_albaran_alba')
    @classmethod
    def validar_numero_albaran(cls, v):
        v = v.strip()

        if not v.isdigit():
            raise ValueError("El número de albarán debe contener solo dígitos.")
        
        # Filtro mínimo razonable
        if len(v) < 6:
            raise ValueError("Número de albarán demasiado corto.")
        
        return v

    @field_validator('fecha_albaran', mode="before")
    @classmethod
    def parsear_fecha_albaran(cls, v):
        
        if isinstance(v, date):
            return v

        if isinstance(v, str):
            v = v.strip()

            # limpieza OCR
            v = re.sub(r"[^\d/\-]", "", v)

            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"):
                try:
                    fecha = datetime.strptime(v, fmt).date()

                    # Validar lógica
                    if fecha > date.today():
                        raise ValueError("La fecha no puede ser futura.")

                    return fecha
                
                except ValueError:
                    
                    pass

        raise ValueError("La fecha del albarán debe estar en formato dd/mm/yyyy o dd-mm-yyyy.")