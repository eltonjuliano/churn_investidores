import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

def load_data(filepath: str) -> pd.DataFrame:
    """Carrega o dataset e retorna um DataFrame do pandas."""
    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    elif filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        raise ValueError("Formato não suportado. Use .xlsx ou .csv")
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica limpeza e padronização básica nos dados."""
    df = df.copy()
    
    # Remover duplicados
    df = df.drop_duplicates(subset=['client_id'], keep='last')
    
    # Tratamento de nulos (se houver, preenchendo numéricos com mediana e cats com moda)
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    cat_cols = df.select_dtypes(include=['object']).columns
    
    for col in num_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())
            
    for col in cat_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].mode()[0])
            
    return df

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering para criar variáveis inteligentes de negócio."""
    df = df.copy()
    
    # 1. Variação percentual de saldo (12 meses)
    # Evitar divisão por zero
    saldo_inicial_safe = np.where(df['saldo_inicial'] == 0, 1, df['saldo_inicial'])
    df['variacao_saldo_12m_perc'] = ((df['saldo_12_meses'] - df['saldo_inicial']) / saldo_inicial_safe) * 100
    
    # 2. Score de Engajamento
    # Multiplica logins e tempo no app, divide por dias_sem_login (+1 pra evitar div por 0)
    df['score_engajamento'] = (df['logins_mes'] * df['tempo_app_min_mes']) / (df['dias_sem_login'] + 1)
    
    # 3. Nível de Interação com Assessor
    tempo_resposta_safe = np.where(df['tempo_resposta_horas'] == 0, 1, df['tempo_resposta_horas'])
    df['interacao_assessor'] = df['contato_assessor'] / tempo_resposta_safe
    
    # 4. Cliente VIP
    # Se o saldo atual (12 meses) está no quartil superior ou é maior que um limiar
    limiar_vip = df['saldo_12_meses'].quantile(0.85)
    df['cliente_vip'] = np.where(df['saldo_12_meses'] >= limiar_vip, 1, 0)
    
    # 5. Indicador de Baixa Atividade (Inativo / Risco Alto)
    df['risco_inativo'] = np.where(df['dias_sem_login'] > 30, 1, 0)
    
    # 6. Indicador de rentabilidade
    df['teve_lucro'] = np.where(df['lucro_12_meses'] > 0, 1, 0)
    
    return df

def encode_features(df: pd.DataFrame, is_train: bool = True, models_path: str = "outputs/models") -> pd.DataFrame:
    """Codifica variáveis categóricas e escala os numéricos."""
    df_encoded = df.copy()
    
    # Separar colunas
    cat_cols = ['sexo', 'cidade', 'estado', 'perfil_investidor', 'ativos_carteira', 'assessor_principal', 'perfil_assessor']
    num_cols = [c for c in df_encoded.columns if c not in cat_cols and c not in ['client_id', 'churn']]
    
    if not os.path.exists(models_path):
        os.makedirs(models_path)
    
    if is_train:
        # Treinar Label Encoders
        encoders = {}
        for col in cat_cols:
            if col in df_encoded.columns:
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                encoders[col] = le
        joblib.dump(encoders, os.path.join(models_path, 'label_encoders.pkl'))
        
        # Treinar Scaler
        scaler = StandardScaler()
        df_encoded[num_cols] = scaler.fit_transform(df_encoded[num_cols])
        joblib.dump(scaler, os.path.join(models_path, 'scaler.pkl'))
    else:
        # Carregar Encoders
        encoders = joblib.load(os.path.join(models_path, 'label_encoders.pkl'))
        for col in cat_cols:
            if col in df_encoded.columns and col in encoders:
                le = encoders[col]
                # Tratar classes novas em inferência
                df_encoded[col] = df_encoded[col].astype(str)
                # O que não for conhecido vira uma categoria "Unknown" ou mapeia pro mais comum. Aqui pegamos os conhecidos.
                known_classes = le.classes_
                df_encoded[col] = df_encoded[col].apply(lambda x: x if x in known_classes else known_classes[0])
                df_encoded[col] = le.transform(df_encoded[col])
        
        # Carregar Scaler
        scaler = joblib.load(os.path.join(models_path, 'scaler.pkl'))
        df_encoded[num_cols] = scaler.transform(df_encoded[num_cols])
        
    return df_encoded

def process_pipeline(filepath: str, is_train: bool = True) -> pd.DataFrame:
    """Executa o pipeline completo (raw -> clean -> features -> encode)."""
    print(f"Carregando dados de: {filepath}")
    df = load_data(filepath)
    print("Limpando dados...")
    df_clean = clean_data(df)
    print("Criando features inteligentes...")
    df_feat = create_features(df_clean)
    print("Codificando variáveis...")
    df_final = encode_features(df_feat, is_train=is_train)
    return df_final, df_feat
