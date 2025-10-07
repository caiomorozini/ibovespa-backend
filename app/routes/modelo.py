import logging
import json
import sqlalchemy
import pandas as pd
from fastapi import (APIRouter, HTTPException, Response,
                     status, File, UploadFile, Depends)
from pydantic import BaseModel
from starlette import status
from app.models import Registration, Category
from app.database.db import get_session, AsyncSession
from typing import List, Annotated
from app.dependencies.authentication import get_current_active_user
from app.schemas.user import User
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor

router = APIRouter()


class Celular(BaseModel):
    memoria_ram: float | None = None
    memoria_max: float | None = None
    tela_largura: int | None = None
    tela_altura: int | None = None
    tela_densidade_pixels: float | None = None
    bateria_carga: float | None = None
    camera_megapixel: float | None = None
    bateria_tipo: str | None = None
    camera_resolucao: str | None = None
    disponibilidade: float | None = None
    chipset: str | None = None
    sistema_operacional: str | None = None
    processador: str | None = None
    dimensoes: str | None = None
    peso: float | None = None
    tela_resolucao: str | None = None
    tela_tamanho: float | None = None
    tela_tipo: str | None = None
    gpu: str | None = None
    tela_fps: float | None = None

    class Config:
        orm_mode = True
        json_schema_extra = {
            "examples": [
                {
                "memoria_ram": 4.0,
                "memoria_max": 128.0,
                "tela_tamanho": 6.6,
                "tela_densidade_pixels": 400.0,
                "bateria_carga": 5000.0,
                "camera_megapixel": 50.0,
                "bateria_tipo": "Litio",
                "tela_largura": 1080,
                "tela_altura": 2408,
                "camera_resolucao": "8160 x 6120 pixel",
                "disponibilidade": 11,
                "chipset": "SAMSUNG Exynos 850",
                "sistema_operacional": "Android 12 Samsung One UI 4.1",
                "processador": "4x 2.0 GHz Cortex-A55 + 4x 2.0 GHz Cortex-A55",
                "dimensoes": "165.1 x 76.4 x 8.8 mm",
                "peso": 195.0,
                "tela_tipo": "TFT LCD",
                "gpu": "Mali-G52",
                "tela_fps": 60.0
        },{
                    "memoria_ram": 4.0,
                    "memoria_max": 256.0,
                    "tela_tamanho": 6.1,
                    "tela_densidade_pixels": 460.0,
                    "bateria_carga": 2815.0,
                    "camera_megapixel": 12.0,
                    "bateria_tipo": "Litio",
                    "tela_largura": 1170,
                    "tela_altura": 2532,
                    "camera_resolucao": "4000 x 3000 pixel",
                    "disponibilidade": 67,
                    "chipset": "T8101 Apple A14 Bionic",
                    "sistema_operacional": "iOS 14",
                    "processador": "2x 3.1 GHz Firestorm + 4x 1.8 GHz Icestorm",
                    "dimensoes": "146.7 x 71.5 x 7.4 mm",
                    "peso": 164.0,
                    "tela_tipo": "Super Retina XDR OLED",
                    "gpu": "Apple GPU (4-core graphics)",
                    "tela_fps": 60.0
            },
                ]}
# Faixas de preço
bins = [0, 1000, 2000, 3000, 4000, 5000, 10000]
labels = ["Muito Barato", "Barato", "Médio", "Caro", "Muito Caro", "Luxo"]

@router.post("/predict_hybrid", status_code=status.HTTP_200_OK)
async def prever_hibrido(
    _: Annotated[User, Depends(get_current_active_user)],
    celular: Celular,
    session: AsyncSession = Depends(get_session)
):
    try:
        model = joblib.load("modelo_precos_regressor.pkl")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar o modelo: {e}")

    try:
        df = pd.DataFrame([celular.model_dump()])

        # remover colunas de preço do payload
        for col in ["preco", "preco_medio", "precos"]:
            if col in df.columns:
                df = df.drop(columns=[col])

        # Previsão do preço exato
        preco_previsto = model.predict(df)[0]

        # Converter para faixa
        faixa_preco = pd.cut([preco_previsto], bins=bins, labels=labels)[0]

        return {
            "preco_previsto": round(preco_previsto, 2),
            "faixa_preco": faixa_preco
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer a predição: {e}")

@router.post("/train", status_code=status.HTTP_200_OK)
async def treinar_modelo(
    _: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session)
):
    from pydantic import BaseModel, ConfigDict

    class RegistrationData(BaseModel):
        data: dict | None = None
        model_config = ConfigDict(from_attributes=True)

    # Buscar registros
    query = sqlalchemy.select(Registration)
    result = await session.execute(query)
    records = result.scalars().all()
    records_data = [RegistrationData.from_orm(r).data for r in records if r.data]

    if not records_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não há dados suficientes para treinar o modelo"
        )

    df = pd.DataFrame(records_data)

    # Extrair preço
    def extrair_preco(row):
        if pd.notna(row.get("preco_medio")):
            return float(row["preco_medio"])
        if isinstance(row.get("precos"), list) and row["precos"]:
            preco_str = row["precos"][0].replace("R$", "").replace(".", "").replace(",", ".").strip()
            try:
                return float(preco_str)
            except:
                return None
        return None

    df["preco"] = df.apply(extrair_preco, axis=1)
    df = df.dropna(subset=["preco"])
    df["preco"] = df["preco"].astype(float)

    # Remover colunas irrelevantes
    df = df.drop([
        "id", "name", "category", "release_date", "status",
        "url", "source", "created_at", "updated_at",
        "preco_medio", "precos", "memoria_expansivel", "resistencia_agua"
    ], axis=1, errors="ignore")
    
    # Tratando colunas numéricas com regex
    def extrair_numero(text):
        import re
        if pd.isna(text):
            return None
        match = re.search(r"[\d,.]+", text)
        if match:
            num_str = match.group(0).replace(",", ".")
            try:
                return float(num_str)
            except:
                return None
        return None

    numeric_cols = ["peso", "bateria_carga", "tela_fps", "memoria_max", "camera_megapixel", "tela_densidade_pixels"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(extrair_numero)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].astype(float)
            
    import re
    # Separando tela_resolucao em largura e altura
    if "tela_resolucao" in df.columns:
        def split_resolution(res):
            if pd.isna(res):
                return None, None
            # formato: '3200 x 2400 pixel'
            # pegar apenas a parte antes de 'pixel'
            res = res.split("pixel")[0].strip()
            # dividir por 'x' ou 'X'
            parts = re.split(r'[xX]', res)
            if len(parts) == 2:
                try:
                    width = int(parts[0].strip())
                    height = int(parts[1].strip())
                    return width, height
                except:
                    return None, None
            return None, None
        
        df[["tela_largura", "tela_altura"]] = df["tela_resolucao"].apply(
            lambda x: pd.Series(split_resolution(x))
        )
        df = df.drop("tela_resolucao", axis=1)

    # 
    # Preencher valores ausentes
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    for col in df.select_dtypes(include=["category"]).columns:
        df[col] = df[col].cat.add_categories("Desconhecido")
    if categorical_cols:
        df[categorical_cols] = df[categorical_cols].fillna("Desconhecido")

    # Calculando disponibilidade (idade do modelo em meses)
    df["disponibilidade"] = (pd.to_datetime("now") - pd.to_datetime(df["disponibilidade"])).dt.days // 30

    # Separar features e target
    X = df.drop("preco", axis=1)
    y = df["preco"]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Identificar colunas
    numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_features = X.select_dtypes(include=["object", "category"]).columns.tolist()

    # Transformadores
    numeric_transformer = SimpleImputer(strategy="median")
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ]
    )

    # Pipeline do regressor
    regressor = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", RandomForestRegressor(n_estimators=200, random_state=42))
    ])

    # Treinar
    regressor.fit(X_train, y_train)

    # Salvar modelo
    joblib.dump(regressor, "modelo_precos_regressor.pkl")
    logging.info("Modelo de regressão salvo como modelo_precos_regressor.pkl")

    return {"message": "Modelo treinado com sucesso"}