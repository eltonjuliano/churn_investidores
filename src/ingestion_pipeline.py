import os
import glob
import pandas as pd
from datetime import datetime
from data_processing import load_data, clean_data, create_features, encode_features
from model_training import predict_churn
import shutil

# Calcula a raiz do projeto dinamicamente
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
ARCHIVE_DIR = os.path.join(BASE_DIR, "data", "archive")
MASTER_FILE = os.path.join(PROCESSED_DIR, "dataset_master.csv")
MODELS_DIR = os.path.join(BASE_DIR, "outputs", "models")
MODEL_PATH = os.path.join(MODELS_DIR, "xgb_churn_model.pkl")

def setup_dirs():
    for d in [RAW_DIR, PROCESSED_DIR, ARCHIVE_DIR, MODELS_DIR]:
        os.makedirs(d, exist_ok=True)

def run_pipeline():
    """Busca novos dados, processa, gera predições e anexa ao master."""
    setup_dirs()
    
    # Procura arquivos .xlsx ou .csv em raw
    new_files = glob.glob(os.path.join(RAW_DIR, "*.xlsx")) + glob.glob(os.path.join(RAW_DIR, "*.csv"))
    
    if not new_files:
        print("Nenhum arquivo novo para processar.")
        return
        
    master_df = None
    if os.path.exists(MASTER_FILE):
        master_df = pd.read_csv(MASTER_FILE)
        
    for file in new_files:
        print(f"Processando: {file}")
        
        # 1. Carregar
        df = load_data(file)
        
        # Guardar ids originais e os dados que não vão pro modelo (opcional, mas bom pra master)
        df_clean = clean_data(df)
        df_feat = create_features(df_clean)
        
        # Se o modelo já existe, aplica o encoding como is_train=False e prevê
        encoders_path = os.path.join(MODELS_DIR, "label_encoders.pkl")
        if os.path.exists(MODEL_PATH) and os.path.exists(encoders_path):
            df_encoded = encode_features(df_feat, is_train=False, models_path=MODELS_DIR)
            probs = predict_churn(df_encoded, MODEL_PATH)
            # Adiciona a probabilidade aos dados limpos/feat
            df_feat['churn_probability'] = probs
            df_feat['risk_segment'] = pd.cut(probs, bins=[0, 0.3, 0.7, 1.0], labels=['Baixo', 'Médio', 'Alto'])
            df_feat['processed_at'] = datetime.now().isoformat()
        else:
            print("Modelo ainda não treinado. Apenas processando dados (sem predição).")
            # Salvar como dados de treinamento master e não prever ainda
            df_feat['churn_probability'] = None
            df_feat['risk_segment'] = None
            df_feat['processed_at'] = datetime.now().isoformat()

        # Atualizar dataset master
        if master_df is None:
            master_df = df_feat
        else:
            # Concatena os novos e remove duplicatas de client_id (mantém o último/mais recente)
            master_df = pd.concat([master_df, df_feat], ignore_index=True)
            master_df = master_df.drop_duplicates(subset=['client_id'], keep='last')
            
        # Move o arquivo processado para um arquivo morto (archive) para não processar de novo
        filename = os.path.basename(file)
        archive_path = os.path.join(ARCHIVE_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}")
        shutil.move(file, archive_path)
        print(f"Arquivo movido para {archive_path}")

    # Salva o master atualizado
    if master_df is not None:
        master_df.to_csv(MASTER_FILE, index=False)
        print(f"Master dataset atualizado em {MASTER_FILE}")

if __name__ == "__main__":
    run_pipeline()
