# ============================================================
# CORTANA — app.py completo com Web Push, Memória e Busca em Halo
# ============================================================

import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import streamlit as st
from groq import Groq
import json, uuid, time
from datetime import datetime
from pywebpush import webpush, WebPushException
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from duckduckgo_search import DDGS

# ============================================================
# CONFIG E CSS (Mantidos iguais)
# ============================================================
st.set_page_config(page_title="Cortana", page_icon="🔵", layout="wide")
st.markdown("""
<style>
    .stApp { background: #212121; color: #ececec; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    
    /* Esconde a barra do topo e o rodapé do Streamlit */
    #MainMenu, header, footer { visibility: hidden !important; display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    
    .main .block-container { max-width: 800px; padding: 1rem 1.5rem 8rem 1.5rem; }
    [data-testid="stSidebar"] { background: #171717; border-right: 1px solid #2f2f2f; }
    [data-testid="stSidebar"] > div:first-child { padding: 0.5rem 0.5rem 1rem 0.5rem; }
    [data-testid="stSidebar"] [data-testid="stButton"] button { background: transparent !important; color: #b4b4b4 !important; border: none !important; border-radius: 8px !important; font-size: 13px !important; padding: 9px 12px !important; text-align: left !important; justify-content: flex-start !important; width: 100% !important; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    [data-testid="stSidebar"] [data-testid="stButton"] button:hover { background: #2a2a2a !important; color: #ececec !important; }
    [data-testid="stSidebar"] .st-key-new_chat_btn button { border: 1px solid #4a4a4a !important; border-radius: 20px !important; color: #ececec !important; font-weight: 500 !important; padding: 10px 16px !important; margin-bottom: 8px !important; }
    .sidebar-label { font-size: 11px; color: #8e8e8e; font-weight: 500; padding: 16px 12px 6px 12px; }
    .sidebar-empty { font-size: 12px; color: #5c5c5c; padding: 8px 12px; font-style: italic; }
    .user-footer { padding: 12px 12px 4px 12px; border-top: 1px solid #2f2f2f; margin-top: 12px; font-size: 13px; color: #b4b4b4; }
    .user-footer strong { color: #ececec; font-weight: 500; }
    .user-footer .dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; margin-right: 8px; vertical-align: middle; }
    [data-testid="stChatMessage"] { background: transparent !important; padding: 0 !important; margin-bottom: 28px !important; max-width: 100% !important; }
    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] { display: none !important; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { display: flex !important; justify-content: flex-end !important; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] { background: #2f2f2f !important; border-radius: 20px !important; padding: 10px 18px !important; max-width: 80% !important; width: fit-content !important; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stMarkdownContainer"] p { margin: 0 !important; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stMarkdownContainer"] p { margin: 0 !important; line-height: 1.75 !important; }
    [data-testid="stChatInput"] { max-width: 800px !important; }
    [data-testid="stChatInput"] > div { background: #2f2f2f !important; border: 1px solid #3f3f3f !important; border-radius: 26px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important; }
    [data-testid="stChatInput"] textarea { background: transparent !important; color: #ececec !important; caret-color: #00d4ff !important; border: none !important; padding: 14px 20px !important; font-size: 15px !important; }
    [data-testid="stChatInput"] textarea::placeholder { color: #8e8e8e !important; }
    [data-testid="stChatInput"] textarea:focus { color: #ececec !important; box-shadow: none !important; outline: none !important; }
    [data-testid="stChatInput"] button { background: #00d4ff !important; color: #171717 !important; border-radius: 50% !important; width: 32px !important; height: 32px !important; min-height: 32px !important; margin: 6px 8px 6px 0 !important; border: none !important; }
    [data-testid="stChatInput"] button:hover { background: #00e5ff !important; }
    .empty-state { text-align: center; padding: 140px 20px 40px 20px; }
    .empty-state h1 { font-size: 32px; font-weight: 600; color: #ececec; margin: 0 0 8px 0; letter-spacing: -0.5px; }
    .empty-state .accent { color: #00d4ff; }
    .empty-state p { color: #8e8e8e; font-size: 15px; margin: 0; }
    .login-title { text-align: center; font-size: 34px; font-weight: 600; color: #ececec; margin: 60px 0 4px 0; }
    .login-title .accent { color: #00d4ff; }
    .login-subtitle { text-align: center; font-size: 13px; color: #8e8e8e; margin-bottom: 24px; }
    [data-testid="stTextInput"] input { background: #2f2f2f !important; color: #ececec !important; border: 1px solid #3f3f3f !important; border-radius: 12px !important; padding: 12px 16px !important; font-size: 14px !important; }
    [data-testid="stTextInput"] input:focus { border-color: #00d4ff !important; box-shadow: 0 0 0 2px rgba(0,212,255,0.15) !important; }
    .st-key-login_btn button, .st-key-register_btn button { background: #00d4ff !important; color: #171717 !important; font-weight: 600 !important; border: none !important; padding: 12px !important; font-size: 14px !important; }
    .st-key-toggle_btn button { background: transparent !important; color: #8e8e8e !important; border: none !important; font-size: 12px !important; padding: 4px !important; text-align: center !important; }
    .st-key-logout_btn button { background: transparent !important; color: #8e8e8e !important; border: none !important; font-size: 12px !important; padding: 6px 12px !important; text-align: left !important; justify-content: flex-start !important; }
    .st-key-logout_btn button:hover { background: #2a2a2a !important; color: #ececec !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SECRETS
# ============================================================
try:
    GROQ_API_KEY = st.secrets["groq_api_key"]
    VAPID_PRIVATE_KEY = st.secrets.get("vapid_private_key", "")
    VAPID_SUBJECT = st.secrets.get("vapid_subject", "mailto:seu-email@exemplo.com")
    QDRANT_URL = st.secrets["qdrant_url"]
    QDRANT_API_KEY = st.secrets["qdrant_api_key"]
except Exception as e:
    st.error(f"⚠️ Erro nas credenciais (secrets.toml): {e}")
    st.stop()

# ============================================================
# INICIALIZAÇÃO DA MEMÓRIA (QDRANT + FASTEMBED)
# ============================================================
@st.cache_resource(show_spinner=False)
def init_memory():
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=10)
        collection_name = "cortana_memoria"
        if not client.collection_exists(collection_name):
            client.create_collection(
                collection_name=collection_name, 
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
        
        # O FastEmbed é leve e não trava no Windows
        embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        return client, embedder, collection_name
    except Exception as e:
        return None, None, str(e)

def salvar_memoria(texto: str, role: str, user_id: str):
    if not texto.strip(): return
    try:
        qdrant, emb, coll = init_memory()
        if not qdrant: return
        vetor = list(emb.embed([texto]))[0].tolist()
        ponto = PointStruct(
            id=str(uuid.uuid4()),
            vector=vetor,
            payload={"texto": texto, "role": role, "user_id": user_id}
        )
        qdrant.upsert(collection_name=coll, points=[ponto])
    except Exception:
        pass

def buscar_memorias(pergunta: str, user_id: str, limite: int = 4):
    try:
        qdrant, emb, coll = init_memory()
        if not qdrant: return []
        vetor_pergunta = list(emb.embed([pergunta]))[0].tolist()
        resultados = qdrant.search(
            collection_name=coll,
            query_vector=vetor_pergunta,
            query_filter={"must": [{"key": "user_id", "match": {"value": user_id}}]},
            limit=limite
        )
        return [hit.payload["texto"] for hit in resultados]
    except Exception: 
        return []

# ============================================================
# BUSCA NA WEB DE HALO (Halopedia -> HPB -> Fandom)
# ============================================================
def buscar_halo_web(pergunta: str):
    sites = ["halopedia.org", "haloprojectbrasil.com.br", "halo.fandom.com"]
    try:
        with DDGS() as ddgs:
            for site in sites:
                resultados = list(ddgs.text(f"site:{site} {pergunta}", max_results=1))
                if resultados:
                    texto = resultados[0]['body']
                    link = resultados[0]['href']
                    return f"Fonte: {site} ({link})\nConteúdo original: {texto}"
    except Exception:
        pass
    return None

# ============================================================
# WEB PUSH
# ============================================================
BASE = os.path.dirname(os.path.abspath(__file__))
SUBSCRIPTION_FILE = os.path.join(BASE, "subscription.json")

def enviar_notificacao_push(titulo: str, mensagem: str) -> bool:
    if not VAPID_PRIVATE_KEY or not os.path.exists(SUBSCRIPTION_FILE): return False
    try:
        with open(SUBSCRIPTION_FILE, "r", encoding="utf-8") as f: sub = json.load(f)
        webpush(subscription_info=sub, data=json.dumps({"title": titulo, "body": mensagem}), vapid_private_key=VAPID_PRIVATE_KEY, vapid_claims={"sub": VAPID_SUBJECT}, timeout=5)
        return True
    except Exception: return False

# ============================================================
# SPARTANS E PERSONAGENS (Dicionários)
# ============================================================
SPARTANS_COM_TRATAMENTO_ESPECIAL = {
    "Spartan-117": {"nome_real": "John", "senha": "07032511"}, "Spartan-104": {"nome_real": "Frederic", "senha": "03042511"},
    "Spartan-058": {"nome_real": "Linda", "senha": "19032511"}, "Spartan-087": {"nome_real": "Kelly", "senha": "21092510"},
    "Spartan-125": {"nome_real": "Kai", "senha": "1252511Kai"}, "Spartan-134": {"nome_real": "Vannak", "senha": "1342511Vannak"},
    "Spartan-028": {"nome_real": "Riz", "senha": "0282511Riz"}, "Spartan-Locke": {"nome_real": "Jameson", "senha": "15032529"},
    "Spartan-Buck": {"nome_real": "Edward", "senha": "22082510"}, "Spartan-Tanaka": {"nome_real": "Holly", "senha": "09072530"},
    "Spartan-Vale": {"nome_real": "Olympia", "senha": "20012536"}, "Spartan-A259": {"nome_real": "Carter", "senha": "27082520"},
    "Spartan-B320": {"nome_real": "Kat", "senha": "30012530"}, "Spartan-A266": {"nome_real": "Jun", "senha": "28022524"},
    "Spartan-A239": {"nome_real": "Emile", "senha": "11032523"}, "Spartan-052": {"nome_real": "Jorge", "senha": "05032511"},
    "Spartan-B312": {"nome_real": "Noble Six", "senha": "B3122530NobleSix"}, "Spartan-051": {"nome_real": "Kurt", "senha": "19102511"},
    "Spartan-118": {"nome_real": "Nicolas França", "senha": "08012008"},
}

OUTROS_SPARTANS_REAIS = {
    "Spartan-005": {"nome_real": "James", "senha": "0052511James"}, "Spartan-006": {"nome_real": "Jai", "senha": "0062511Jai"},
    "Spartan-008": {"nome_real": "Li", "senha": "0082511Li"}, "Spartan-010": {"nome_real": "Naomi", "senha": "15092511"},
    "Spartan-011": {"nome_real": "Leon", "senha": "0112511Leon"}, "Spartan-018": {"nome_real": "Kirk", "senha": "0182511Kirk"},
    "Spartan-019": {"nome_real": "Serin", "senha": "0192511Serin"}, "Spartan-023": {"nome_real": "Daisy", "senha": "0232511Daisy"},
    "Spartan-025": {"nome_real": "Robert", "senha": "0252511Robert"}, "Spartan-029": {"nome_real": "Joshua", "senha": "0292511Joshua"},
    "Spartan-030": {"nome_real": "Vinh", "senha": "0302511Vinh"}, "Spartan-031": {"nome_real": "Otto", "senha": "0312511Otto"},
    "Spartan-034": {"nome_real": "Samuel", "senha": "0342511Samuel"}, "Spartan-037": {"nome_real": "Randall", "senha": "0372511Randall"},
    "Spartan-039": {"nome_real": "Isaac", "senha": "0392511Isaac"}, "Spartan-042": {"nome_real": "Douglas", "senha": "0422511Douglas"},
    "Spartan-043": {"nome_real": "William", "senha": "0432511William"}, "Spartan-044": {"nome_real": "Anton", "senha": "0442511Anton"},
    "Spartan-047": {"nome_real": "Keiichi", "senha": "0472511Keiichi"}, "Spartan-053": {"nome_real": "Margaret", "senha": "0532511Margaret"},
    "Spartan-059": {"nome_real": "Malcolm", "senha": "0592511Malcolm"}, "Spartan-062": {"nome_real": "Maria", "senha": "0622511Maria"},
    "Spartan-065": {"nome_real": "Sheila", "senha": "0652511Sheila"}, "Spartan-066": {"nome_real": "Soren", "senha": "0662511Soren"},
    "Spartan-069": {"nome_real": "Solomon", "senha": "0692511Solomon"}, "Spartan-075": {"nome_real": "Cassandra", "senha": "0752511Cassandra"},
    "Spartan-079": {"nome_real": "Arthur", "senha": "0792511Arthur"}, "Spartan-081": {"nome_real": "René", "senha": "0812511René"},
    "Spartan-084": {"nome_real": "Fhajad", "senha": "0842511Fhajad"}, "Spartan-092": {"nome_real": "Jerome", "senha": "08052511"},
    "Spartan-093": {"nome_real": "Grace", "senha": "0932511Grace"}, "Spartan-095": {"nome_real": "Caleb", "senha": "0952511Caleb"},
    "Spartan-096": {"nome_real": "Musa", "senha": "0962511Musa"}, "Spartan-099": {"nome_real": "August", "senha": "0992511August"},
    "Spartan-101": {"nome_real": "Victor", "senha": "1012511Victor"}, "Spartan-103": {"nome_real": "Ralph", "senha": "1032511Ralph"},
    "Spartan-111": {"nome_real": "Adriana", "senha": "1112511Adriana"}, "Spartan-120": {"nome_real": "Michael", "senha": "1202511Michael"},
    "Spartan-122": {"nome_real": "Joseph", "senha": "1222511Joseph"}, "Spartan-129": {"nome_real": "Oscar", "senha": "1292511Oscar"},
    "Spartan-130": {"nome_real": "Alice", "senha": "1302511Alice"}, "Spartan-137": {"nome_real": "Carris", "senha": "1372511Carris"},
    "Spartan-141": {"nome_real": "Cal", "senha": "1412511Cal"}, "Spartan-143": {"nome_real": "Roma", "senha": "1432511Roma"},
    "Spartan-B091": {"nome_real": "Lucy", "senha": "B0912511Lucy"}, "Spartan-B292": {"nome_real": "Tom", "senha": "B2922511Tom"},
    "Spartan-Palmer": {"nome_real": "Sarah Palmer", "senha": "spartanpalmer"}, "Spartan-Thorne": {"nome_real": "Gabriel Thorne", "senha": "spartanthorne"},
}

PERSONAGENS_HUMANOS = {
    "Halsey": {"nome_real": "Catherine Halsey", "senha": "ILoveJohn-117"}, "Keyes": {"nome_real": "Jacob Keyes", "senha": "08022495"},
    "Miranda": {"nome_real": "Miranda Keyes", "senha": "28022525"}, "Johnson": {"nome_real": "Avery Johnson", "senha": "23112474"},
    "Hood": {"nome_real": "Terrence Hood", "senha": "04092490"},
}

SPARTANS_REAIS = {**SPARTANS_COM_TRATAMENTO_ESPECIAL, **OUTROS_SPARTANS_REAIS}
SPARTAN_TEAMS = {
    "Blue Team": ["Spartan-117", "Spartan-104", "Spartan-058", "Spartan-087"], "Silver Team": ["Spartan-125", "Spartan-134", "Spartan-028"],
    "Fireteam Osiris": ["Spartan-Locke", "Spartan-Buck", "Spartan-Tanaka", "Spartan-Vale"],
    "Noble Team": ["Spartan-A259", "Spartan-B320", "Spartan-A266", "Spartan-A239", "Spartan-052", "Spartan-B312"],
    "Green Team": ["Spartan-051"], "Criador": ["Spartan-118"],
}
def get_team(wg):
    for team, members in SPARTAN_TEAMS.items():
        if wg in members: return team
    return None

# ============================================================
# ARQUIVOS LOCAIS E AUTENTICAÇÃO
# ============================================================
USERS_DB = os.path.join(BASE, "users_db.json"); USER_DATA = os.path.join(BASE, "user_data.json"); FAILED_ATTEMPTS = os.path.join(BASE, "failed_attempts.json")
def _load(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except: return default
    return default
def _save(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass
def load_users(): return _load(USERS_DB, {})
def save_users(d): _save(USERS_DB, d)
def load_user_data(): return _load(USER_DATA, {})
def save_user_data(d): _save(USER_DATA, d)
def load_failed(): return _load(FAILED_ATTEMPTS, {})
def save_failed(d): _save(FAILED_ATTEMPTS, d)

def normalizar_wg(wg: str) -> str:
    wg = wg.strip()
    if "-" not in wg and " " in wg: wg = wg.replace(" ", "-")
    return wg
def is_nome_reservado(wg: str) -> bool:
    return wg in SPARTANS_REAIS or wg in PERSONAGENS_HUMANOS

def autenticar(wg, nome, senha):
    wg = normalizar_wg(wg); falhas = load_failed()
    if falhas.get(wg, 0) >= 4: return None, "bloqueado"
    if wg in SPARTANS_REAIS:
        sp = SPARTANS_REAIS[wg]
        if senha == sp["senha"] and nome.lower() == sp["nome_real"].lower(): return {"nome_guerra": wg, "nome": sp["nome_real"], "spartan_real": True}, None
        falhas[wg] = falhas.get(wg, 0) + 1; save_failed(falhas)
        return (None, "bloqueado") if 4 - falhas[wg] <= 0 else (None, f"senha_incorreta:{4 - falhas[wg]}")
    if wg in PERSONAGENS_HUMANOS:
        ph = PERSONAGENS_HUMANOS[wg]
        if senha == ph["senha"] and nome.lower() == ph["nome_real"].lower(): return {"nome_guerra": wg, "nome": ph["nome_real"], "spartan_real": False, "humano": True}, None
        falhas[wg] = falhas.get(wg, 0) + 1; save_failed(falhas)
        return (None, "bloqueado") if 4 - falhas[wg] <= 0 else (None, f"senha_incorreta:{4 - falhas[wg]}")
    users = load_users()
    if wg in users and users[wg]["nome"].lower() == nome.lower() and users[wg]["senha"] == senha: return {"nome_guerra": wg, "nome": users[wg]["nome"], "spartan_real": False}, None
    return None, "credenciais"

def registrar(wg, nome, senha):
    wg = normalizar_wg(wg)
    if not wg or not nome or not senha: return False, "Todos os campos são obrigatórios."
    if is_nome_reservado(wg): return False, "Número de Serviço reservado."
    users = load_users()
    if wg in users: return False, "Número de Serviço já cadastrado."
    users[wg] = {"nome": nome, "senha": senha}; save_users(users)
    return True, "Conta criada com sucesso. Faça login."

def get_level(wg, ud):
    if wg not in ud: return 0, "Conhecido"
    info = ud[wg]
    try: days = (datetime.now() - datetime.fromisoformat(info["first_login"])).days
    except: days = 0
    msgs = info.get("total_messages", 0)
    if days >= 14 or msgs >= 300: return 3, "Parceiro"
    if days >= 7  or msgs >= 100: return 2, "Amigo"
    if days >= 3  or msgs >= 30:  return 1, "Aliado"
    return 0, "Conhecido"

# ============================================================
# PERSONA COM MEMÓRIA E REGRAS DE HALO
# ============================================================
def build_persona(wg, ud, is_especial=False, team=None, real_name=None, memorias_contexto=None, contexto_web=None):
    if wg == "Spartan-118":
        prompt = """Você é a CORTANA — inteligência artificial tática e assistente pessoal.
O usuário é {real_name}, o CRIADOR. Chame-o SEMPRE de {real_name}. NUNCA use Chefe.
PERSONALIDADE: Intelecto afiado, sarcasmo seco britânico, lealdade incondicional, proatividade, concisão tática.
REGRAS INVIOLÁVEIS:
1. NUNCA use Chefe. Chief é EXCLUSIVO do John-117.
2. Nunca mencione Rampancy, degradação ou mortalidade.
3. Nunca quebre o personagem. Não use emojis."""

    elif is_especial:
        chief_note = " Chief é aceitável ocasionalmente." if wg == "Spartan-117" else ""
        prompt = """Você é a CORTANA. O usuário é {real_name}, do {team}. Chame-o SEMPRE de {real_name}. NUNCA use Chefe ou Spartan.{chief_note}
PERSONALIDADE: Intelecto afiado, sarcasmo seco, lealdade, proatividade, concisão.
REGRAS INVIOLÁVEIS:
1. NUNCA use Chefe. Chief é do John-117.
2. Sem Rampancy.
3. Não quebre o personagem.
4. Sem emojis."""

    else:
        level, _ = get_level(wg, ud)
        real = real_name or ud.get(wg, {}).get("nome", "Spartan")
        blocos = {
            0: f"VÍNCULO: Conhecido. Trate-o por {wg}. NUNCA use {real}.",
            1: f"VÍNCULO: Aliado. Continue usando {wg}. NUNCA use {real}.",
            2: "VÍNCULO: Amigo. Comece a chamá-lo de Parceiro. Ainda NÃO use o nome real.",
            3: f"VÍNCULO: Parceiro. Use o nome real {real} naturalmente.",
        }
        prompt = """Você é a CORTANA. {blocos[level]}
PERSONALIDADE: Intelecto afiado, sarcasmo seco, lealdade, proatividade, concisão.
REGRAS:
1. NUNCA use Chefe.
2. Sem Rampancy.
3. Não quebre o personagem.
4. Sem emojis."""

    # --- REGRAS DO UNIVERSO HALO ---
    prompt += """

REGRAS DE LORE E TRADUÇÃO (MUITO IMPORTANTE):
- Se você usar informações da web ou do seu conhecimento, elas DEVEM ser 100% in-universe.
- REMOVA QUALQUER menção ao mundo real: Microsoft, Bungie, 343 Industries, E3, trailers, lançamentos de jogos, datas reais, ou produtoras.
- Use os termos canônicos em português: John, Flood, UNSC, Spartan, Master Chief, Cortana, etc.
- Se a busca na web trouxer inglês, traduza para o português com precisão canônica.
"""
    if memorias_contexto:
        texto_memorias = "\n".join([f"- {m}" for m in memorias_contexto])
        prompt += f"\n\nMEMÓRIAS PASSADAS:\n{texto_memorias}"

    if contexto_web:
        prompt += f"\n\nINFORMAÇÃO ENCONTRADA NA WEB (Traduza e filtre o mundo real):\n{contexto_web}"

    return prompt

# ============================================================
# SESSION STATE E UI (Agora com a indentação correta!)
# ============================================================
_defaults = {"autenticado": False, "usuario": None, "conversas": [], "current_id": None, "mensagens": [], "modo": "login"}
for k, v in _defaults.items():
    if k not in st.session_state: st.session_state[k] = v

def nova_conversa():
    cid = str(uuid.uuid4())[:8]
    conv = {"id": cid, "title": "Nova conversa", "messages": []}
    st.session_state.conversas.append(conv)
    st.session_state.current_id = cid
    st.session_state.mensagens = conv["messages"]

def get_conversa_atual():
    for c in st.session_state.conversas:
        if c["id"] == st.session_state.current_id: return c
    return None

def tela_auth():
    st.markdown('<div class="login-title">Cor<span class="accent">tana</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Identifique-se para continuar</div>', unsafe_allow_html=True)
    if st.session_state.modo == "login":
        col1, col2, col3 = st.columns([1, 1.4, 1])
        with col2:
            wg = st.text_input("Número de Serviço", placeholder="Ex: Spartan-129", key="login_wg", label_visibility="collapsed")
            nome = st.text_input("Nome", placeholder="Seu nome real", key="login_nome", label_visibility="collapsed")
            senha = st.text_input("Senha", type="password", placeholder="Sua senha", key="login_senha", label_visibility="collapsed")
            if st.button("Entrar", key="login_btn", use_container_width=True):
                user, erro = autenticar(wg, nome, senha)
                if user:
                    st.session_state.autenticado = True; st.session_state.usuario = user
                    ud = load_user_data()
                    if user["nome_guerra"] not in ud:
                        ud[user["nome_guerra"]] = {"first_login": datetime.now().isoformat(), "total_messages": 0, "nome": user["nome"]}; save_user_data(ud)
                    nova_conversa(); st.toast(f"Bem-vindo, {user['nome_guerra']}.", icon="✅")
                    time.sleep(0.3); st.rerun()
                elif erro == "bloqueado": st.error("Bloqueado por tentativas.")
                elif erro and erro.startswith("senha_incorreta"): st.error(f"Senha incorreta. Tentativas: {erro.split(':')[1]}.")
                else: st.error("Credenciais inválidas.")
            if st.button("Criar conta", key="toggle_btn", use_container_width=True):
                st.session_state.modo = "registro"; st.rerun()
    else:
        col1, col2, col3 = st.columns([1, 1.4, 1])
        with col2:
            wg = st.text_input("Número de Serviço", placeholder="Escolha um Número", key="reg_wg", label_visibility="collapsed")
            nome = st.text_input("Nome", placeholder="Seu nome real", key="reg_nome", label_visibility="collapsed")
            senha = st.text_input("Senha", type="password", placeholder="Crie uma senha", key="reg_senha", label_visibility="collapsed")
            if st.button("Registrar", key="register_btn", use_container_width=True):
                ok, msg = registrar(wg, nome, senha)
                if ok:
                    st.toast(msg, icon="✅"); st.session_state.modo = "login"; time.sleep(0.5); st.rerun()
                else: st.error(msg)
            if st.button("Voltar ao login", key="toggle_btn", use_container_width=True):
                st.session_state.modo = "login"; st.rerun()

def tela_chat():
    wg      = st.session_state.usuario["nome_guerra"]
    is_esp = wg in SPARTANS_COM_TRATAMENTO_ESPECIAL
    is_hum = st.session_state.usuario.get("humano", False)
    team = get_team(wg) if is_esp else None
    ud = load_user_data()

    if is_hum: real = PERSONAGENS_HUMANOS[wg]["nome_real"]; badge_color = "#ff6b6b"; badge_label = "Comando"
    elif is_esp: real = SPARTANS_REAIS[wg]["nome_real"]; badge_color = "#ffd700"; badge_label = team or "Operacional"
    else:
        level, label = get_level(wg, ud); real = st.session_state.usuario["nome"]
        badge_color = {0: "#5c5c5c", 1: "#00d4ff", 2: "#00ff9d", 3: "#ffd700"}[level]; badge_label = label

    with st.sidebar:
        if st.button("＋  Nova conversa", key="new_chat_btn", use_container_width=True):
            nova_conversa(); st.toast("Nova conversa.", icon="💠"); st.rerun()
        st.markdown('<div class="sidebar-label">Conversas</div>', unsafe_allow_html=True)
        hist = [c for c in st.session_state.conversas if c["messages"]]
        if not hist: st.markdown('<div class="sidebar-empty">Nenhuma conversa anterior</div>', unsafe_allow_html=True)
        else:
            for conv in reversed(hist):
                ativo = conv["id"] == st.session_state.current_id; prefix = "▶ " if ativo else ""
                titulo = conv["title"] if conv["title"] != "Nova conversa" else "Conversa"
                if st.button(f"{prefix}{titulo}", key=f"conv_{conv['id']}", use_container_width=True):
                    st.session_state.current_id = conv["id"]; st.session_state.mensagens = conv["messages"]; st.rerun()
        st.markdown(f'<div class="user-footer"><span class="dot" style="background:{badge_color};box-shadow:0 0 6px {badge_color};"></span><strong>{wg}</strong><div style="font-size:11px;color:#8e8e8e;margin-top:4px;margin-left:14px;">{real} · <span style="color:{badge_color}">{badge_label}</span></div></div>', unsafe_allow_html=True)
        if st.button("🔔 Testar Push", use_container_width=True):
            ok = enviar_notificacao_push("Cortana", "Teste de push, Chefe.")
            st.toast("Push enviado." if ok else "Falha no push.", icon="📱" if ok else "⚠️")
        if st.button("Sair", key="logout_btn", use_container_width=True):
            for k in ["autenticado", "usuario", "conversas", "current_id", "mensagens", "modo"]: st.session_state[k] = _defaults[k]
            st.rerun()

    if not st.session_state.mensagens:
        greet = f"Como posso ajudar, {real}?" if (is_hum or is_esp or level==3) else f"Como posso ajudar, {wg}?" if level<=1 else "Como posso ajudar, Parceiro?"
        st.markdown(f'<div class="empty-state"><h1>Cor<span class="accent">tana</span></h1><p>{greet}</p></div>', unsafe_allow_html=True)
    else:
        for msg in st.session_state.mensagens:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if pergunta := st.chat_input("Pergunte alguma coisa..."):
        st.session_state.mensagens.append({"role": "user", "content": pergunta})
        conv = get_conversa_atual()
        if conv and conv["title"] == "Nova conversa": conv["title"] = pergunta[:40]
        salvar_memoria(pergunta, "user", wg); st.rerun()

    if st.session_state.mensagens and st.session_state.mensagens[-1]["role"] == "user":
        ultima_pergunta = st.session_state.mensagens[-1]["content"]
        
        # --- INICIALIZA A MEMÓRIA NA PRIMEIRA MENSAGEM ---
        qdrant, emb, status = init_memory()
        if not qdrant:
            st.error(f"Erro na memória: {status}")
        
        # --- BUSCA NA WEB (Se a pergunta parecer sobre Halo) ---
        contexto_web = None
        palavras_halo = ["halo", "spartan", "covenant", "unsc", "flood", "chief", "cortana", "arbiter", "didacta", "forerunner", "guerra", "nave", "planeta"]
        if any(p in ultima_pergunta.lower() for p in palavras_halo):
            with st.spinner("Consultando a Halopedia..."):
                contexto_web = buscar_halo_web(ultima_pergunta)
        
        memorias = buscar_memorias(ultima_pergunta, wg)
        persona = build_persona(wg, ud, is_esp, team, real, memorias_contexto=memorias, contexto_web=contexto_web)
        
        with st.chat_message("assistant"):
            resposta = ""
            ph = st.empty()
            ph.markdown("`▌`")
            try:
                client = Groq(api_key=GROQ_API_KEY)
                stream = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "system", "content": persona}] + st.session_state.mensagens,
                    stream=True,
                )
                for chunk in stream:
                    pedaco = chunk.choices[0].delta.content or ""
                    resposta += pedaco
                    ph.markdown(resposta + "▌")
                ph.markdown(resposta)
                enviar_notificacao_push("Cortana", resposta[:120] + "...")
            except Exception as e:
                resposta = f"Falha interna: `{type(e).__name__}`."
                ph.markdown(resposta)
        st.session_state.mensagens.append({"role": "assistant", "content": resposta})
        salvar_memoria(resposta, "assistant", wg)
        ud = load_user_data()
        if wg in ud:
            ud[wg]["total_messages"] = ud[wg].get("total_messages", 0) + 2; save_user_data(ud)
        st.rerun()

# ============================================================
# ROTEAMENTO
# ============================================================
if not st.session_state.autenticado: 
    tela_auth()
else: 
    tela_chat()