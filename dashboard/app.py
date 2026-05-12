import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np

# Configuração da página
st.set_page_config(page_title="Analytics | Churn de Investidores", page_icon="📈", layout="wide")

# CSS para estilo Premium Fintech: Modernizado com Glassmorphism e Google Fonts
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Global Font */
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Main Background adjustments (Streamlit handles base dark mode now, but we enhance it) */
    .stApp {
        background: radial-gradient(circle at top left, #121A28, #0B0E14);
    }

    /* Metric Cards - Modern Glassmorphism */
    .metric-card {
        background: rgba(21, 26, 34, 0.6);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
    }
    .metric-title {
        font-size: 15px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #8B9BB4;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.5px;
    }
    
    /* Color Highlights for Cards */
    .risk-high { border-bottom: 4px solid #FF4B4B; }
    .risk-med { border-bottom: 4px solid #FFA500; }
    .risk-low { border-bottom: 4px solid #00F0FF; }
    .neutral { border-bottom: 4px solid #8B9BB4; }

    /* Insights Box - Elegant and readable */
    .insight-box {
        background: linear-gradient(145deg, rgba(30, 35, 45, 0.8), rgba(21, 26, 34, 0.4));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        height: 100%;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .insight-title {
        color: #00F0FF;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .insight-text {
        font-size: 15px;
        color: #CBD5E1;
        line-height: 1.6;
        margin-bottom: 15px;
    }
    .insight-action {
        color: #FFD700;
        font-weight: 600;
        font-size: 14px;
        background: rgba(255, 215, 0, 0.1);
        padding: 8px 12px;
        border-radius: 6px;
        border-left: 3px solid #FFD700;
    }
    
    /* Headers and Titles */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Fix Top padding */
    div.block-container {
        padding-top: 2rem;
    }
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    file_path = os.path.join(project_root, "data", "processed", "dataset_master.csv")
    
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error(f"Base de dados não encontrada em: {file_path}. Por favor, rode o pipeline de ingestão.")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# Garantir colunas preditivas
if 'churn_probability' not in df.columns:
    df['churn_probability'] = 0.0
    df['risk_segment'] = 'Baixo'

st.title("📊 Painel Executivo: Retenção de Investidores")
st.markdown("Visualização simplificada e direta sobre o risco de abandono (churn) da nossa base.")

# ==========================================
# SEÇÃO 1: INSIGHTS E DIRETRIZES
# ==========================================
st.markdown("### 🧠 Insights & Diretrizes de Ação")
col_ins1, col_ins2, col_ins3 = st.columns(3)

with col_ins1:
    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">⏱️ Alerta de Engajamento</div>
        <div class="insight-text">Clientes inativos (sem abrir o App) por mais de 30 dias apresentam taxa altíssima de risco de resgate. A inatividade é o principal sintoma.</div>
        <div class="insight-action">Ação: Automação imediata de WhatsApp/Email de reengajamento após 15 dias sem login.</div>
    </div>
    """, unsafe_allow_html=True)

with col_ins2:
    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">📞 Tempo de Resposta</div>
        <div class="insight-text">O atraso nas respostas do assessor atua como "gatilho" de saída para clientes VIPs (com saldo alto), mesmo quando a carteira vai bem.</div>
        <div class="insight-action">Ação: Estabelecer SLA de resposta menor que 12h para contas de alto patrimônio.</div>
    </div>
    """, unsafe_allow_html=True)

with col_ins3:
    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">💰 Lucro não basta</div>
        <div class="insight-text">Há clientes com lucro recente, mas que correm risco de evasão por falta de relacionamento próximo com a assessoria.</div>
        <div class="insight-action">Ação: Agendar "Review de Carteira" a cada 6 meses com o cliente, preventivamente.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# SEÇÃO 2: FILTROS E KPIs
# ==========================================
st.sidebar.title("Filtros")
estados = st.sidebar.multiselect("Estado", options=df['estado'].unique(), default=[])
assessor = st.sidebar.multiselect("Assessor Principal", options=df['assessor_principal'].unique(), default=[])

df_filtered = df.copy()
if estados:
    df_filtered = df_filtered[df_filtered['estado'].isin(estados)]
if assessor:
    df_filtered = df_filtered[df_filtered['assessor_principal'].isin(assessor)]

# Cálculos KPI
total_clientes = len(df_filtered)
clientes_risco_alto = len(df_filtered[df_filtered['risk_segment'] == 'Alto'])
perc_risco = (clientes_risco_alto / total_clientes * 100) if total_clientes > 0 else 0
patrimonio_risco = df_filtered[df_filtered['risk_segment'] == 'Alto']['saldo_12_meses'].sum()

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(f'<div class="metric-card neutral"><div class="metric-title">Total de Clientes</div><div class="metric-value">{total_clientes:,}</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="metric-card risk-high"><div class="metric-title">Clientes em Risco Alto</div><div class="metric-value">{clientes_risco_alto:,} ({perc_risco:.1f}%)</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="metric-card risk-high"><div class="metric-title">Patrimônio em Risco de Fuga</div><div class="metric-value">R$ {patrimonio_risco/1e6:.1f} Milhões</div></div>', unsafe_allow_html=True)

# ==========================================
# SEÇÃO 3: GRÁFICOS SIMPLIFICADOS
# ==========================================
st.markdown("### 📈 Análises Diretas")

c1, c2 = st.columns(2)

with c1:
    # Gráfico 1: Risco por Perfil (Em %)
    # Qual a porcentagem de clientes de cada perfil que está em risco alto?
    perfil_totals = df_filtered.groupby('perfil_investidor').size()
    perfil_risco = df_filtered[df_filtered['risk_segment'] == 'Alto'].groupby('perfil_investidor').size()
    
    # Preenche com zero onde não há risco
    perfil_risco = perfil_risco.reindex(perfil_totals.index, fill_value=0)
    
    df_perfil = pd.DataFrame({
        'Perfil': perfil_totals.index,
        '% em Risco Alto': (perfil_risco / perfil_totals) * 100
    }).sort_values(by='% em Risco Alto', ascending=True)

    fig1 = px.bar(df_perfil, x='% em Risco Alto', y='Perfil', orientation='h',
                  title="1. Qual perfil tem mais % de clientes em Risco Alto?",
                  text_auto='.1f', color_discrete_sequence=['#FF4B4B'])
    fig1.update_layout(xaxis_title="%", yaxis_title="", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    # Gráfico 2: Faixa de Inatividade vs Risco Alto
    # Cria faixas de dias sem login
    df_filtered['faixa_inatividade'] = pd.cut(df_filtered['dias_sem_login'], 
                                              bins=[-1, 10, 30, 999], 
                                              labels=['Até 10 dias', '11 a 30 dias', 'Mais de 30 dias'])
    
    inatividade_risco = df_filtered[df_filtered['risk_segment'] == 'Alto'].groupby('faixa_inatividade').size().reset_index(name='Qtd Clientes')
    
    fig2 = px.bar(inatividade_risco, x='faixa_inatividade', y='Qtd Clientes',
                  title="2. Inatividade: Quantos clientes de Risco Alto temos por tempo sem login?",
                  text_auto=True, color_discrete_sequence=['#FF4B4B'])
    fig2.update_layout(xaxis_title="Dias Sem Acessar", yaxis_title="Qtd Clientes (Risco Alto)", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Impacto Financeiro por Assessor (Ranking Top 5)
st.markdown("### 🚨 Onde estamos perdendo dinheiro? (Top 5 Assessores Críticos)")
loss_by_advisor = df_filtered[df_filtered['risk_segment'] == 'Alto'].groupby('assessor_principal')['saldo_12_meses'].sum().reset_index()
loss_by_advisor = loss_by_advisor.sort_values(by='saldo_12_meses', ascending=False).head(5)

fig3 = px.bar(loss_by_advisor, x='assessor_principal', y='saldo_12_meses',
              text_auto='.2s', color_discrete_sequence=['#FFA500'])
fig3.update_layout(title="Ranking de Patrimônio em Risco por Assessor",
                   xaxis_title="Assessor", yaxis_title="Patrimônio (R$)",
                   plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
st.plotly_chart(fig3, use_container_width=True)

# Tabela Limpa de Ação
st.markdown("### 📋 Fila de Ação (Apenas Clientes Críticos)")
df_critical = df_filtered[df_filtered['risk_segment'] == 'Alto'].sort_values(by='churn_probability', ascending=False)
display_cols = ['client_id', 'assessor_principal', 'estado', 'dias_sem_login', 'saldo_12_meses', 'churn_probability']
st.dataframe(df_critical[display_cols].head(30).style.format({
    'saldo_12_meses': 'R$ {:.2f}',
    'churn_probability': '{:.1%}'
}), use_container_width=True)
