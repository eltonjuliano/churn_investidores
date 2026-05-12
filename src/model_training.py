import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
import joblib
import os
import json

def prepare_split(df: pd.DataFrame, target_col: str = 'churn', test_size: float = 0.2, random_state: int = 42):
    """Separa os dados em treino e teste."""
    X = df.drop(columns=[target_col, 'client_id'], errors='ignore')
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    return X_train, X_test, y_train, y_test

def train_and_evaluate(X_train, X_test, y_train, y_test):
    """Treina os 3 modelos solicitados e avalia os resultados."""
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'XGBoost': XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    }
    
    results = {}
    trained_models = {}
    
    for name, model in models.items():
        print(f"Treinando {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_prob)
        
        results[name] = {
            'Accuracy': acc,
            'Precision': prec,
            'Recall': rec,
            'F1-Score': f1,
            'ROC-AUC': roc_auc
        }
        trained_models[name] = model
        
    return trained_models, results

def save_model(model, filepath: str):
    """Salva o modelo serializado no disco."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(model, filepath)
    print(f"Modelo salvo em {filepath}")

def get_feature_importance(model, feature_names):
    """Extrai as importâncias das features de um modelo treinado."""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importances = np.abs(model.coef_[0])
    else:
        return None
        
    feat_imp = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False)
    
    return feat_imp

def predict_churn(df: pd.DataFrame, model_path: str = "outputs/models/xgb_churn_model.pkl") -> np.ndarray:
    """Carrega o modelo salvo e realiza a predição para novos dados."""
    model = joblib.load(model_path)
    X = df.drop(columns=['churn', 'client_id'], errors='ignore')
    probs = model.predict_proba(X)[:, 1]
    return probs
