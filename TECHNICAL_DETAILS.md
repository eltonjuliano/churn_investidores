# Detalhamento Técnico e Estudo de Caso (Para Entrevistas)

Este documento foi criado para detalhar as decisões técnicas, a lógica de negócio e o desenvolvimento do projeto **Churn de Investidores**. Ele serve como um guia profundo para estudos e para apresentação em entrevistas técnicas na área de Data Analytics, Data Science e Business Intelligence.

---

## 1. Arquitetura e Lógica do Pipeline de Dados

A arquitetura do projeto foi pensada para simular um ambiente real de produção (DataOps).

**Como funciona a lógica de chegada de dados?**
1. O banco, corretora ou fintech gera relatórios periódicos de clientes e os joga na pasta `data/raw/`.
2. O script `src/ingestion_pipeline.py` atua como um orquestrador. Ele varre a pasta `raw`, encontra os arquivos novos e aciona as transformações.
3. Após processado (limpeza + IA), o arquivo é anexado na base consolidada (`data/processed/dataset_master.csv`) e o original vai para a pasta `data/archive/` para não ser lido duas vezes.

**Por que fazer assim?** Em uma entrevista, isso demonstra que você entende de automação e não faz apenas análises manuais isoladas em Jupyter Notebooks. Você criou um produto de dados contínuo.

---

## 2. Detalhamento do Machine Learning (Modelagem Preditiva)

O coração da Inteligência Artificial do projeto está em `src/model_training.py` e `src/data_processing.py`.

### A. Feature Engineering (Engenharia de Variáveis)
Para o modelo funcionar bem, a IA precisa de variáveis ligadas a comportamento. Nós criamos:
- **Score de Engajamento**: Criamos um cálculo que multiplica o número de logins pelo tempo no App, e divide pelo tempo inativo. Clientes que logam muito mas ficam inativos recentemente caem no score.
- **Risco Inativo e Cliente VIP**: Criamos limites numéricos lógicos (ex: Saldo no top 85% é VIP. Mais de 30 dias sem logar = Inativo).

### B. Escolha do Algoritmo
Testamos Logistic Regression, Random Forest e **XGBoost**.
- Optamos pelo **XGBoost** (Extreme Gradient Boosting) porque ele lida extremamente bem com dados tabulares, valores não-lineares (como picos de inatividade) e desbalanceamento de classes leves.
- **Métricas:** Não olhamos apenas para *Accuracy* (Acurácia). Focamos no **F1-Score** e na **ROC-AUC (Área sob a curva)**. Em churn, prever quem vai sair (True Positive) e não dar alarmes falsos excessivos (False Positive) é crucial, e a ROC-AUC de ~0.97 nos disse que o modelo consegue separar incrivelmente bem quem sai de quem fica.

### C. Pipeline de Transformação (Encoders e Scalers)
No código, utilizamos `LabelEncoder` para transformar textos (como perfis e estados) em números que o XGBoost entende. E usamos o `StandardScaler` para normalizar escalas (para que um saldo de 100 mil não "esmague" um login mensal de 5 na matemática do modelo). Tudo isso é serializado (salvo em disco com `joblib`) para ser reutilizado na predição de novos clientes.

---

## 3. Detalhamento do CSS e Layout (Dashboard)

A maioria dos dashboards em Python (Streamlit) são feios ou padronizados. Nós fomos além para criar um visual **Premium Fintech** (Padrão XP, BTG, Nubank).

### A. O CSS e o "Glassmorphism"
O arquivo `dashboard/app.py` recebe uma injeção pesada de código CSS via `st.markdown("<style>...", unsafe_allow_html=True)`.
- **Glassmorphism:** Usamos as propriedades `background: rgba(21, 26, 34, 0.6);` combinadas com `backdrop-filter: blur(10px);`. Isso cria um efeito de "vidro fumê" atrás dos cartões, gerando uma sobreposição elegante no fundo.
- **Micro-interações:** Adicionamos `transition: transform 0.2s ease` para que o painel ganhe "vida". Quando o mouse passa por cima de um KPI, o card sobe ligeiramente e projeta uma sombra, chamando a atenção.

### B. O Arquivo `.streamlit/config.toml`
Essa é uma sacada de sênior. O Streamlit do usuário obedece o tema claro/escuro do Sistema Operacional dele (Windows/Mac). Como o nosso CSS foi desenhado para fundo escuro, criamos a pasta oculta `.streamlit` com o comando `base="dark"` no config. Assim, forçamos o aplicativo a abrir no nosso tema padrão, evitando que o texto branco desapareça em um fundo branco de um usuário mal configurado.

---

## 4. Escolha Visual: Por que esses Gráficos?

Na hora de apresentar dados para a diretoria, menos é mais.

1. **Barras Horizontais (Percentual de Risco por Perfil):**
   - *Por quê?* Evitamos gráficos de pizza poluídos ou barras empilhadas complexas. Ao usar barras horizontais mostrando apenas a porcentagem (Ex: 45% do perfil Conservador), o cérebro humano consegue comparar imediatamente o topo do ranking com o final dele sem pensar.

2. **O Funil de Inatividade (Barras de Faixa Etária/Tempo):**
   - *Por quê?* Inicialmente tínhamos um gráfico de dispersão com "bolinhas" que cruzava saldo e logins. Isso exigia conhecimento estatístico para leitura. Nós agrupamos (Clusterizamos visualmente) os clientes em "Até 10 dias", "11 a 30 dias" e "Mais de 30 dias". Agora, qualquer leigo olha e diz: "Nossa, quase todo mundo que sai está sem logar há mais de 30 dias". O gráfico responde à dor direto na fonte.

3. **Ranking de Impacto Financeiro (Assessores):**
   - *Por quê?* Em negócios, Churn se traduz em dinheiro. Mostrar quantos clientes o Assessor perdeu é bom, mas mostrar a **Soma do Patrimônio em Risco** é o que acende o alerta. Um gráfico de barras direto com os Top 5 assessores que mais concentram risco de perda milionária gera ação instantânea da gestão.

---

### Resumo para o Entrevistador
Este não é apenas um projeto que roda um "`.fit()` e `.predict()`". 
Ele possui:
- **Engenharia de Software:** Pipelines automatizados e orientados a arquivos.
- **Ciência de Dados Avançada:** XGBoost com feature engineering voltado à dor de negócio.
- **Produto e UX:** Um painel focado no tomador de decisão, com design premium forçado via configs de alto nível, cartões envidraçados e legibilidade absoluta.
