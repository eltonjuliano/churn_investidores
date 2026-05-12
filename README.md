# 🚀 Analytics & Predição de Churn de Investidores

Bem-vindo ao projeto de inteligência de dados focado em retenção de clientes no mercado financeiro. Este repositório contém uma solução completa (de ponta a ponta) para analisar, prever e agir sobre o risco de abandono (churn) de investidores em corretoras ou fintechs.

## 🎯 Objetivo do Projeto
Identificar padrões comportamentais de investidores que levam ao cancelamento ou inatividade, utilizando Machine Learning para prever quem está em risco de sair. Além disso, fornecer um dashboard executivo moderno para monitoramento contínuo e acompanhamento do impacto financeiro.

## 💼 Problema de Negócio
No mercado financeiro competitivo, o custo de aquisição de um cliente (CAC) é alto. Perder um cliente (Churn) significa perder o patrimônio sob custódia, reduzindo receitas de corretagem, gestão e taxas. Antecipar a saída de um cliente permite à equipe comercial agir proativamente com ofertas de retenção.

## 🏗 Estrutura do Projeto
O repositório está organizado utilizando as melhores práticas de Engenharia de Dados e Data Science:

```text
/
├── data/
│   ├── raw/                 # Novos dados chegam aqui (pipeline os consome)
│   ├── processed/           # Dados limpos e preparados (dataset_master.csv)
│   └── archive/             # Arquivos brutos já processados
├── notebooks/               # Notebooks didáticos do processo
│   ├── 01_data_loading_cleaning.ipynb
│   ├── 02_eda.ipynb
│   └── 03_feature_engineering_modeling.ipynb
├── src/                     # Código fonte para produção
│   ├── data_processing.py   # Transformações e limpeza
│   ├── model_training.py    # Funções de treino do modelo
│   └── ingestion_pipeline.py# Pipeline automático de ingestão
├── dashboard/               # Aplicação web
│   └── app.py               # Streamlit Executive Dashboard
└── outputs/                 # Artefatos gerados (modelos .pkl, métricas)
```

## ⚙️ Processo de Análise e Modelagem

1. **Limpeza e Engenharia de Features**:
   - Tratamento de nulos e duplicidades.
   - Criação de novas variáveis inteligentes: `score_engajamento`, `risco_inativo`, `cliente_vip` e interações com o assessor.
   
2. **Modelagem de Machine Learning**:
   Foram testados Logistic Regression, Random Forest e XGBoost.
   - **Melhor Modelo**: XGBoost com F1-Score ~ 0.87 e ROC-AUC ~ 0.97.
   - **Feature Importance**: O engajamento com o app, lucros recentes e o contato com o assessor mostraram-se chaves para a decisão de churn.

3. **Pipeline Automático de Ingestão**:
   Sempre que um novo lote de clientes chega na pasta `data/raw`, o script `src/ingestion_pipeline.py` automaticamente calcula as features, gera a probabilidade de churn e atualiza a base processada `data/processed/dataset_master.csv`.

## 📈 Dashboard Executivo
Construímos um Dashboard com visualizações modernas (estilo *Glassmorphism/Dark Mode* financeiro) para acompanhamento:
- **KPIs**: Patrimônio em risco, total de clientes, taxa de churn estimada.
- **Gráficos Preditivos**: Churn por assessor, impacto financeiro, mapa de risco por perfil de investimento.
- **Tabela de Ação**: Lista dos clientes mais críticos.

## 💻 Como Executar

**1. Instalar as dependências**
```bash
pip install -r requirements.txt
```

**2. Rodar o Pipeline de Ingestão (para criar a base master)**
*Coloque novos arquivos Excel ou CSV na pasta `data/raw/`*
```bash
python src/ingestion_pipeline.py
```

**3. Iniciar o Dashboard**
```bash
streamlit run dashboard/app.py
```

## 💡 Insights e Recomendações
- **Engajamento**: Clientes com mais de 30 dias sem login possuem probabilidade drasticamente maior de churn. *Recomendação: Automação de push/email focado em reengajamento após 15 dias de inatividade.*
- **Assessoria**: O tempo de resposta do assessor afeta diretamente a retenção dos clientes VIPs. *Recomendação: Implementar SLA de resposta menor que 12h para clientes de alto patrimônio.*
- **Rentabilidade**: Apesar de importante, o cliente que tem lucro mas não interage corre risco de sair por falta de relacionamento. *Ação: Consultorias periódicas (reviews de carteira).*

## 🌟 Próximos Passos (Possíveis Melhorias)
- Integração da pipeline com serviços Cloud (AWS S3, Google Cloud Storage).
- Explicabilidade do modelo a nível de indivíduo usando SHAP (para explicar exatamente por que um cliente X vai sair).
- Conexão em tempo real do Streamlit com um banco PostgreSQL.
