# 🔍 SEMRush Explorer - Obramax

Interface visual para explorar a API SEMRush, focada em análise de concorrentes e geração de FAQ.

## 🚀 Funcionalidades

- **Pesquisa de Keywords**: Perguntas, relacionadas e broad match
- **Análise Batch**: Analisar múltiplas keywords de uma vez
- **Análise de Concorrentes**: Keywords orgânicas e descoberta de concorrentes
- **Gap Analysis**: Keywords missing, shared e unique
- **Top Pages**: Páginas com mais tráfego

## 📦 Instalação Local

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows)
.\.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env com sua API Key

# Executar
streamlit run app_semrush.py
```

## ☁️ Deploy no Streamlit Cloud

1. Faça fork/clone deste repositório
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte seu GitHub
4. Selecione o repositório e `app_semrush.py`
5. Em **Advanced Settings > Secrets**, adicione:
   ```toml
   SEMRUSH_API_KEY = "sua_api_key"
   DISABLE_SSL_VERIFY = "false"
   ```
6. Deploy!

## 🔧 Configuração

| Variável | Descrição |
|----------|-----------|
| `SEMRUSH_API_KEY` | Sua chave da API SEMRush |
| `DISABLE_SSL_VERIFY` | `true` para desabilitar SSL (home office) |

## 📊 Endpoints Utilizados

| Endpoint | Custo | Descrição |
|----------|-------|-----------|
| `phrase_questions` | 40 un/ln | Perguntas sobre keywords |
| `phrase_related` | 40 un/ln | Keywords relacionadas |
| `phrase_fullsearch` | 20 un/ln | Broad match |
| `phrase_these` | 10 un/ln | Análise batch |
| `domain_organic` | 10 un/ln | Keywords orgânicas |
| `domain_organic_organic` | 40 un/ln | Concorrentes |
| `domain_domains` | 80 un/ln | Gap analysis |
| `domain_organic_unique` | 10 un/ln | Top pages |

## 📝 Licença

Uso interno - Obramax
