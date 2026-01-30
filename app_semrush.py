"""
SEMRush Explorer - Interface Streamlit
======================================
Interface visual para testar a API SEMRush
Foco: Obramax + Análise de Concorrentes
"""

import streamlit as st
import pandas as pd
import requests
import time
import urllib3
import os
from dotenv import load_dotenv

# Carrega .env
load_dotenv()

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="SEMRush Explorer - Obramax",
    page_icon="🔍",
    layout="wide"
)

# ============================================================================
# SESSION STATE - Configurações persistentes no front
# ============================================================================
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("SEMRUSH_API_KEY", "")
if "main_domain" not in st.session_state:
    st.session_state.main_domain = "obramax.com.br"
if "competitors" not in st.session_state:
    st.session_state.competitors = ["leroymerlin.com.br", "sodimac.com.br", "telhanorte.com.br"]
if "database" not in st.session_state:
    st.session_state.database = "br"
if "disable_ssl" not in st.session_state:
    st.session_state.disable_ssl = os.getenv("DISABLE_SSL_VERIFY", "false").lower() == "true"

# Desabilita warnings SSL se necessário
if st.session_state.disable_ssl:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SEMRUSH_BASE_URL = "https://api.semrush.com/"
RATE_LIMIT_DELAY = 0.15

# ============================================================================
# FUNÇÕES DE API
# ============================================================================

def call_semrush_api(params: dict) -> dict:
    """Chamada genérica à API SEMRush."""
    params["key"] = st.session_state.api_key
    time.sleep(RATE_LIMIT_DELAY)
    response = requests.get(
        SEMRUSH_BASE_URL, 
        params=params, 
        timeout=30, 
        verify=not st.session_state.disable_ssl
    )
    return {
        "success": response.status_code == 200,
        "status_code": response.status_code,
        "text": response.text
    }

def parse_csv_response(raw_text: str) -> pd.DataFrame:
    """Converte resposta CSV da SEMRush para DataFrame."""
    lines = raw_text.strip().split('\n')
    if len(lines) < 2:
        return pd.DataFrame()
    
    headers = lines[0].split(';')
    data = []
    for line in lines[1:]:
        if line.strip():
            data.append(line.split(';'))
    
    df = pd.DataFrame(data, columns=headers)
    return df

# ============================================================================
# FUNÇÕES ESPECÍFICAS DE CADA ENDPOINT
# ============================================================================

def get_phrase_questions(keyword: str, limit: int = 5) -> pd.DataFrame:
    """Busca perguntas sobre uma keyword."""
    params = {
        "type": "phrase_questions",
        "phrase": keyword,
        "database": st.session_state.database,
        "export_columns": "Ph,Nq,Kd",
        "display_limit": limit
    }
    result = call_semrush_api(params)
    if result["success"]:
        return parse_csv_response(result["text"])
    return pd.DataFrame()

def get_phrase_related(keyword: str, limit: int = 5) -> pd.DataFrame:
    """Busca keywords relacionadas."""
    params = {
        "type": "phrase_related",
        "phrase": keyword,
        "database": st.session_state.database,
        "export_columns": "Ph,Nq,Kd",
        "display_limit": limit
    }
    result = call_semrush_api(params)
    if result["success"]:
        return parse_csv_response(result["text"])
    return pd.DataFrame()

def get_phrase_fullsearch(keyword: str, limit: int = 5) -> pd.DataFrame:
    """Busca broad match (variações) de uma keyword."""
    params = {
        "type": "phrase_fullsearch",
        "phrase": keyword,
        "database": st.session_state.database,
        "export_columns": "Ph,Nq,Kd",
        "display_limit": limit
    }
    result = call_semrush_api(params)
    if result["success"]:
        return parse_csv_response(result["text"])
    return pd.DataFrame()

def get_phrase_these(keywords: list, limit: int = 5) -> pd.DataFrame:
    """Análise batch de múltiplas keywords."""
    phrase = ";".join(keywords[:100])  # Máximo 100
    params = {
        "type": "phrase_these",
        "phrase": phrase,
        "database": st.session_state.database,
        "export_columns": "Ph,Nq,Kd",
        "display_limit": limit
    }
    result = call_semrush_api(params)
    if result["success"]:
        return parse_csv_response(result["text"])
    return pd.DataFrame()

def get_phrase_kdi(keywords: list) -> pd.DataFrame:
    """Obtém dificuldade de keywords."""
    phrase = ";".join(keywords[:100])
    params = {
        "type": "phrase_kdi",
        "phrase": phrase,
        "database": st.session_state.database,
        "export_columns": "Ph,Kd"
    }
    result = call_semrush_api(params)
    if result["success"]:
        return parse_csv_response(result["text"])
    return pd.DataFrame()

def get_domain_organic(domain: str, limit: int = 5) -> pd.DataFrame:
    """Obtém keywords orgânicas de um domínio."""
    params = {
        "type": "domain_organic",
        "domain": domain,
        "database": st.session_state.database,
        "export_columns": "Ph,Po,Nq,Kd,Ur,Tr",
        "display_limit": limit,
        "display_sort": "nq_desc"
    }
    result = call_semrush_api(params)
    if result["success"]:
        return parse_csv_response(result["text"])
    return pd.DataFrame()

def get_domain_competitors(domain: str, limit: int = 5) -> pd.DataFrame:
    """Descobre concorrentes de um domínio."""
    params = {
        "type": "domain_organic_organic",
        "domain": domain,
        "database": st.session_state.database,
        "export_columns": "Dn,Cr,Np,Or,Ot,Oc",
        "display_limit": limit
    }
    result = call_semrush_api(params)
    if result["success"]:
        return parse_csv_response(result["text"])
    return pd.DataFrame()

def get_gap_analysis(main_domain: str, competitors: list, gap_type: str, limit: int = 5) -> pd.DataFrame:
    """Gap analysis entre domínios."""
    if gap_type == "missing":
        domains_str = "|".join([f"*|or|{competitors[0]}"] + 
                               [f"+|or|{c}" for c in competitors[1:]] + 
                               [f"-|or|{main_domain}"])
    elif gap_type == "shared":
        all_domains = [main_domain] + competitors
        domains_str = "|".join([f"*|or|{d}" for d in all_domains])
    else:  # unique
        domains_str = "|".join([f"*|or|{main_domain}"] + 
                               [f"-|or|{c}" for c in competitors])
    
    params = {
        "type": "domain_domains",
        "domains": domains_str,
        "database": st.session_state.database,
        "export_columns": "Ph,Nq,Kd",
        "display_limit": limit,
        "display_sort": "nq_desc"
    }
    result = call_semrush_api(params)
    if result["success"]:
        return parse_csv_response(result["text"])
    return pd.DataFrame()

def get_domain_organic_unique(domain: str, limit: int = 5) -> pd.DataFrame:
    """Obtém top pages de um domínio."""
    params = {
        "type": "domain_organic_unique",
        "domain": domain,
        "database": st.session_state.database,
        "export_columns": "Ur,Pc,Tg,Tr",
        "display_limit": limit,
        "display_sort": "tr_desc"
    }
    result = call_semrush_api(params)
    if result["success"]:
        return parse_csv_response(result["text"])
    return pd.DataFrame()

# ============================================================================
# SIDEBAR - MENU DE NAVEGAÇÃO
# ============================================================================

st.sidebar.title("🔍 SEMRush Explorer")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação",
    [
        "🔍 Pesquisa de Keywords",
        "📊 Batch + Dificuldade",
        "🏢 Análise de Concorrentes",
        "⚖️ Gap Analysis",
        "📄 Top Pages",
        "⚙️ Configurações"
    ]
)

st.sidebar.markdown("---")


# ============================================================================
# PÁGINAS
# ============================================================================

# 🔍 PESQUISA DE KEYWORDS
if menu == "🔍 Pesquisa de Keywords":
    st.title("🔍 Pesquisa de Keywords")
    
    keyword = st.text_input("Digite a keyword:", value="furadeira")
    limit = st.slider("Limite de resultados:", 1, 20, 5)
    
    tab1, tab2, tab3 = st.tabs(["❓ Perguntas", "🔗 Relacionadas", "📝 Broad Match"])
    
    with tab1:
        if st.button("Buscar Perguntas", key="btn_questions"):
            with st.spinner("Buscando..."):
                df = get_phrase_questions(keyword, limit)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("Nenhum resultado encontrado.")
    
    with tab2:
        if st.button("Buscar Relacionadas", key="btn_related"):
            with st.spinner("Buscando..."):
                df = get_phrase_related(keyword, limit)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("Nenhum resultado encontrado.")
    
    with tab3:
        if st.button("Buscar Broad Match", key="btn_broad"):
            with st.spinner("Buscando..."):
                df = get_phrase_fullsearch(keyword, limit)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("Nenhum resultado encontrado.")

# 📊 BATCH + DIFICULDADE
elif menu == "📊 Batch + Dificuldade":
    st.title("📊 Análise Batch de Keywords")
    
    keywords_text = st.text_area(
        "Digite as keywords (uma por linha):",
        value="furadeira\ncimento\nargamassa\npiso laminado\ntorneira"
    )
    keywords = [k.strip() for k in keywords_text.split("\n") if k.strip()]
    
    st.write(f"**{len(keywords)} keywords** para analisar")
    
    if st.button("🔍 Analisar Keywords", key="btn_batch"):
        with st.spinner("Analisando volume e dificuldade..."):
            df = get_phrase_these(keywords)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Nenhum resultado.")

# 🏢 ANÁLISE DE CONCORRENTES
elif menu == "🏢 Análise de Concorrentes":
    st.title("🏢 Análise de Concorrentes")
    
    all_domains = [st.session_state.main_domain] + st.session_state.competitors
    domain = st.selectbox("Selecione o domínio:", all_domains)
    limit = st.slider("Limite de resultados:", 1, 20, 5, key="slider_conc")
    
    tab1, tab2 = st.tabs(["🔑 Keywords Orgânicas", "🎯 Descobrir Concorrentes"])
    
    with tab1:
        if st.button("Buscar Keywords Orgânicas", key="btn_organic"):
            with st.spinner(f"Analisando {domain}..."):
                df = get_domain_organic(domain, limit)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("Nenhum resultado.")
    
    with tab2:
        if st.button("Descobrir Concorrentes", key="btn_competitors"):
            with st.spinner(f"Buscando concorrentes de {domain}..."):
                df = get_domain_competitors(domain, limit)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("Nenhum resultado.")

# ⚖️ GAP ANALYSIS
elif menu == "⚖️ Gap Analysis":
    st.title("⚖️ Gap Analysis")
    
    st.markdown(f"**Domínio Principal:** {st.session_state.main_domain}")
    st.markdown(f"**Concorrentes:** {', '.join(st.session_state.competitors)}")
    
    gap_type = st.selectbox(
        "Tipo de análise:",
        ["missing", "shared", "unique"],
        format_func=lambda x: {
            "missing": "❌ Missing - Keywords que concorrentes têm e você NÃO",
            "shared": "🤝 Shared - Keywords que TODOS têm",
            "unique": "⭐ Unique - Keywords que SÓ você tem"
        }[x]
    )
    
    limit = st.slider("Limite de resultados:", 1, 20, 5, key="slider_gap")
    
    if st.button("Analisar Gap", key="btn_gap"):
        with st.spinner("Analisando..."):
            df = get_gap_analysis(
                st.session_state.main_domain,
                st.session_state.competitors,
                gap_type,
                limit
            )
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Nenhum resultado.")

# 📄 TOP PAGES
elif menu == "📄 Top Pages":
    st.title("📄 Top Pages")
    
    all_domains = [st.session_state.main_domain] + st.session_state.competitors
    domain = st.selectbox("Selecione o domínio:", all_domains, key="select_pages")
    limit = st.slider("Limite de resultados:", 1, 20, 5, key="slider_pages")
    
    if st.button("Buscar Top Pages", key="btn_pages"):
        with st.spinner(f"Buscando páginas de {domain}..."):
            df = get_domain_organic_unique(domain, limit)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("Nenhum resultado.")

# ⚙️ CONFIGURAÇÕES
elif menu == "⚙️ Configurações":
    st.title("⚙️ Configurações")
    
    st.markdown("### 🔑 API")
    new_api_key = st.text_input("API Key:", value=st.session_state.api_key, type="password")
    
    st.markdown("### 🌐 Domínios")
    new_main_domain = st.text_input("Domínio Principal:", value=st.session_state.main_domain)
    
    st.markdown("### 🏢 Concorrentes")
    competitors_text = st.text_area(
        "Concorrentes (um por linha):",
        value="\n".join(st.session_state.competitors)
    )
    
    st.markdown("### 🗄️ Database")
    new_database = st.selectbox(
        "Database Regional:",
        ["br", "us", "uk", "de", "fr", "es", "it", "pt", "mx", "ar"],
        index=0
    )
    
    st.markdown("### 🔒 SSL")
    new_disable_ssl = st.checkbox("Desabilitar verificação SSL (home office)", value=st.session_state.disable_ssl)
    
    if st.button("💾 Salvar Configurações", key="btn_save"):
        st.session_state.api_key = new_api_key
        st.session_state.main_domain = new_main_domain
        st.session_state.competitors = [c.strip() for c in competitors_text.split("\n") if c.strip()]
        st.session_state.database = new_database
        st.session_state.disable_ssl = new_disable_ssl
        st.success("✅ Configurações salvas!")
        st.rerun()
