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
    memoria_ram: str | None = None
    memoria_max: str | None = None
    tela_tamanho: str | None = None
    tela_densidade_pixels: str | None = None
    bateria_carga: str | None = None
    camera_megapixel: str | None = None
    bateria_tipo: str | None = None
    memoria_expansivel: str | None = None
    resistencia_agua: str | None = None
    camera_resolucao: str | None = None
    disponibilidade: str | None = None
    chipset: str | None = None
    sistema_operacional: str | None = None
    processador: str | None = None
    dimensoes: str | None = None
    peso: str | None = None
    tela_resolucao: str | None = None
    tela_tipo: str | None = None
    gpu: str | None = None
    tela_fps: str | None = None

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
            "memoria_ram": "4 GB",
            "memoria_max": "256 GB",
            "tela_tamanho": "6.1",
            "tela_densidade_pixels": "460 ppi",
            "bateria_carga": "2815 mAh",
            "camera_megapixel": "12 Mp + 12 Mp",
            "bateria_tipo": "Litio",
            "memoria_expansivel": "Não",
            "resistencia_agua": "Sim",
            "camera_resolucao": "4000 x 3000 pixel",
            "disponibilidade": "2020/4",
            "chipset": "T8101 Apple A14 Bionic",
            "sistema_operacional": "iOS 14",
            "processador": "2x 3.1 GHz Firestorm + 4x 1.8 GHz Icestorm",
            "dimensoes": "146.7 x 71.5 x 7.4 mm",
            "peso": "164 g",
            "tela_resolucao": "1170 x 2532 pixel",
            "tela_tipo": "Super Retina XDR OLED",
            "gpu": "Apple GPU (4-core graphics)",
            "tela_fps": "60 Hz"
            }
        }
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
        "preco_medio", "precos"
    ], axis=1, errors="ignore")

    # Preencher valores ausentes
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    for col in df.select_dtypes(include=["category"]).columns:
        df[col] = df[col].cat.add_categories("Desconhecido")
    if categorical_cols:
        df[categorical_cols] = df[categorical_cols].fillna("Desconhecido")

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