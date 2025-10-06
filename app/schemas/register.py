# pylint: disable=E0213
import re
from pydantic import BaseModel, constr, AnyHttpUrl, validator
from typing import List, Optional
from datetime import datetime


class Item(BaseModel):
    sistema_operacional: Optional[str] = ""
    disponibilidade: Optional[str] = ""
    dimensoes: Optional[str] = ""
    peso: Optional[str] = ""
    processador: Optional[str] = ""
    memoria_ram: Optional[str] = ""
    chipset: Optional[str] = ""
    # 64_bit: Optional[str]
    gpu: Optional[str] = ""
    memoria_max: Optional[str] = ""
    memoria_expansivel: Optional[str] = ""
    tela_tamanho: Optional[str] = ""
    tela_resolucao: Optional[str] = ""
    tela_densidade_pixels: Optional[str] = ""
    tela_tipo: Optional[str] = ""
    tela_fps: Optional[str] = ""
    bateria_carga: Optional[str] = ""
    bateria_tipo: Optional[str] = ""
    camera_megapixel: Optional[str] = ""
    camera_resolucao: Optional[str] = ""
    resistencia_agua: Optional[str] = ""

class Register(BaseModel):
    name: constr(min_length=1, max_length=100, strip_whitespace=True, to_lower=True) # type: ignore
    category: constr(min_length=1, max_length=100, strip_whitespace=True, to_lower=True) # type: ignore
    status: int
    data: Item
    url: str
    source: constr(min_length=1, max_length=100, strip_whitespace=True, to_lower=True) # type: ignore
    release_date: Optional[datetime]

    @validator("release_date", pre=True)
    def transform_release_date_to_datetime(cls, v):
        if v and isinstance(v, str):
            # Verificando se entrada é um isoformat
            if re.match(r"\d{4}-\d{2}-\d{2}", v):
                return v

            year, q = v.split("/")
            # Calculando mês inicial do quadrimestre
            month = (int(q) - 1) * 4 + 1
            return datetime(year=int(year), month=month, day=1).isoformat()
        else:
            return None