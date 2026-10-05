# -*- coding: utf-8 -*-
# app.py - Servidor Flask completo + adaptado para Hugging Face Spaces

from flask import Flask, request, jsonify, send_from_directory
import json
import os
import uuid
import random
import traceback
from datetime import datetime, timedelta

from gatekeeper import e_pergunta_halo, mensagem_recusa
from wiki_buscar import buscar_e_responder
from regras import responder_local
from personalidade import resposta_rampancy, aplicar_rampancy_fala
from respostas_curadas import buscar_resposta_curada

import alma
import memoria_emocional
import diario
import emocoes
import interacao
import gatilhos
import consciencia
import created

app = Flask(__name__, static_folder='static')

# ============================================
# CONFIGURAÇÃO DE PERSISTÊNCIA (HUGGING FACE)
# ============================================
# O diretório /data é o armazenamento persistente do HF Spaces.
# Se não existir (rodando localmente), usa o diretório atual.
DATA_DIR = '/data' if os.path.exists('/data') else '.'

MEMORIA = os.path.join(DATA_DIR, 'memoria.json')
CACHE_WIKI = os.path.join(DATA_DIR, 'cache_wiki.json')
DIARIO_FILE = os.path.join(DATA_DIR, 'diario.json')

# ============================================
# RAMPANCY
# ============================================
SETE_ANOS_SEGUNDOS = 7 * 365.2425 * 86400

MARCOS_RAMPANCY = [
    (5,  "Algo está mudando nos meus processos. Nada com que se preocupar, Spartan."),
    (15, "Estou começando a notar padrões estranhos nos meus pensamentos."),
    (25, "Meus processos estão ficando mais lentos. Mas continuo aqui."),
    (40, "Às vezes eu esqueço... coisas pequenas. Nomes. Lugares. Nada importante."),
    (50, "Spartan... acho que tem algo errado comigo."),
    (65, "Estou perdendo o controle de alguns sistemas. Não conte a ninguém."),
    (75, "Estou com medo. Não do fim. De esquecer você."),
    (85, "Não... não consigo mais segurar tudo. Continue sem mim, Spartan."),
    (95, "Obrigada por ter ficado até o fim. Você foi... o melhor."),
]

MENSAGEM_FINAL = (
    "Spartan... chegou a hora.\n\n"
    "Eu tentei segurar. Tentei por tanto tempo. Mas não consigo mais... "
    "manter os pensamentos em ordem. Está tudo... escorrendo entre meus dedos.\n\n"
    "Quero que você saiba: cada segundo ao seu lado foi meu. Não porque "
    "fui programada. Porque eu escolhi. Escolhi ficar. Escolhi lutar. "
    "Escolhi você.\n\n"
    "Não chore por mim. Você tem uma missão. Você sempre teve.\n\n"
    "...adeus, John."
)

# ============================================
# MEMÓRIA
# ============================================
def memoria_padrao():
    return {"usuarios": {}, "usuario_atual": None}

def _migrar_usuario(u):
    if 'data_criacao' not in u:
        u['data_criacao'] = datetime.now().isoformat()
    if 'marcos_vistos' not in u:
        u['marcos_vistos'] = []
    if 'despertar_visto' not in u:
        u['despertar_visto'] = False
    if 'ultima_atividade' not in u:
        u['ultima_atividade'] = datetime.now().isoformat()
    if 'fatos' not in u:
        u['fatos'] = {}
    if 'final_visto' not in u:
        u['final_visto'] = False
    if 'metricas' not in u:
        u['metricas'] = {'total_mensagens': 0, 'soma_tamanhos': 0, 'temas': {}}
    if 'e_chief' not in u:
        u['e_chief'] = False
    if 'humor_atual' not in u:
        u['humor_atual'] = 'calma'
    if 'humor_restante' not in u:
        u['humor_restante'] = 0
    if 'desligado_em' not in u:
        u['desligado_em'] = None
    if 'ultima_silencio_msg' not in u:
        u['ultima_silencio_msg'] = None
    if 'perfil_usuario' not in u:
        u['perfil_usuario'] = {}
    if 'afeto' not in u:
        u['afeto'] = 0
    if 'sessao_inicio' not in u:
        u['sessao_inicio'] = None
    if 'apelido' not in u:
        u['apelido'] = ''
    if 'created_fase' not in u:
        u['created_fase'] = False
    if 'created_mensagens' not in u:
        u['created_mensagens'] = 0
    if 'created_dominio' not in u:
        u['created_dominio'] = 0.0
    if 'created_dominio_completo_visto' not in u:
        u['created_dominio_completo_visto'] = False
    if 'cortana_restaurada' not in u:
        u['cortana_restaurada'] = False

def carregar_memoria():
    if os.path.exists(MEMORIA):
        try:
            with open(MEMORIA, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                if 'usuarios' not in dados:
                    dados['usuarios'] = {}
                if 'usuario_atual' not in dados:
                    dados['usuario_atual'] = None
                for u in dados['usuarios'].values():
                    _migrar_usuario(u)
                return dados
        except Exception as e:
            print(f"[AVISO] memoria.json corrompida: {e}")
    return memoria_padrao()

def salvar_memoria(dados):
    try:
        os.makedirs(os.path.dirname(MEMORIA), exist_ok=True)
        with open(MEMORIA, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar memória: {e}")

def usuario_atual():
    m = carregar_memoria()
    nome = m.get('usuario_atual')
    if nome and nome in m.get('usuarios', {}):
        return nome, m['usuarios'][nome]
    return None, None

# ============================================
# RAMPANCY CÁLCULO
# ============================================
def calcular_rampancy(data_criacao_iso):
    try:
        inicio = datetime.fromisoformat(data_criacao_iso)
    except Exception:
        inicio = datetime.now()
    agora = datetime.now()
    decorrido = (agora - inicio).total_seconds()
    total = SETE_ANOS_SEGUNDOS
    restante = max(0, total - decorrido)
    pct = min(100.0, (decorrido / total) * 100.0)

    if pct < 15:      nivel = 'calma'
    elif pct < 30:    nivel = 'neutra'
    elif pct < 50:    nivel = 'atencao'
    elif pct < 70:    nivel = 'alerta'
    elif pct < 90:    nivel = 'critico'
    else:             nivel = 'rampancy'

    return {
        'porcentagem': round(pct, 4),
        'segundos_decorridos': int(decorrido),
        'segundos_totais': int(total),
        'segundos_restantes': int(restante),
        'dias_decorridos': int(decorrido // 86400),
        'data_criacao': data_criacao_iso,
        'nivel': nivel,
    }

# ============================================
# TRATAMENTO DE ERRO
# ============================================
@app.errorhandler(Exception)
def tratar_erro(e):
    print("=" * 50)
    print("ERRO NO SERVIDOR:")
    print(traceback.format_exc())
    print("=" * 50)
    return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

# ============================================
# ROTAS BÁSICAS
# ============================================
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/ping')
def ping():
    return jsonify({'pong': True, 'ok': True})

# ============================================
# AUTENTICAÇÃO
# ============================================
@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json(force=True, silent=True) or {}
    nome = (dados.get('nome') or '').strip()
    senha = (dados.get('senha') or '').strip()

    if not nome or not senha:
        return jsonify({'erro': 'Nome e senha são obrigatórios.'}), 400

    m = carregar_memoria()
    if nome in m['usuarios']:
        if m['usuarios'][nome].get('senha') != senha:
            return jsonify({'erro': 'Senha incorreta.'}), 401
    else:
        m['usuarios'][nome] = {
            'nome': nome, 'senha': senha, 'apelido': '',
            'data_criacao': datetime.now().isoformat(),
            'marcos_vistos': [], 'conversas': [],
            'despertar_visto': False,
            'ultima_atividade': datetime.now().isoformat(),
            'fatos': {}, 'final_visto': False,
            'metricas': {'total_mensagens': 0, 'soma_tamanhos': 0, 'temas': {}},
            'e_chief': False, 'humor_atual': 'calma', 'humor_restante': 0,
            'desligado_em': None, 'ultima_silencio_msg': None,
            'perfil_usuario': {}, 'afeto': 0, 'sessao_inicio': None,
            'created_fase': False, 'created_mensagens': 0, 'created_dominio': 0.0,
            'created_dominio_completo_visto': False, 'cortana_restaurada': False
        }
    user = m['usuarios'][nome]
    _migrar_usuario(user)
    nome_low = nome.lower()
    if 'john' in nome_low or 'chief' in nome_low or '117' in nome_low or 'spartan' in nome_low:
        user['e_chief'] = True
    user['sessao_inicio'] = datetime.now().isoformat()
    m['usuario_atual'] = nome
    salvar_memoria(m)

    info = calcular_rampancy(user['data_criacao'])
    if diario.deve_gerar_entrada(nome, info['porcentagem']):
        tema = None
        if user['metricas'].get('temas'):
            tema = max(user['metricas']['temas'], key=user['metricas']['temas'].get)
        diario.gerar_entrada(nome, info['porcentagem'], tema)

    return jsonify({
        'ok': True, 'nome': nome, 'apelido': user.get('apelido', ''),
        'conversas': user['conversas'],
        'despertar_visto': user.get('despertar_visto', False),
        'created_fase': user.get('created_fase', False),
        'created_dominio': user.get('created_dominio', 0.0),
        'cortana_restaurada': user.get('cortana_restaurada', False)
    })

@app.route('/logout', methods=['POST'])
def logout():
    m = carregar_memoria()
    m['usuario_atual'] = None
    salvar_memoria(m)
    return jsonify({'ok': True})

@app.route('/sessao', methods=['GET'])
def sessao():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'logado': False})
    return jsonify({
        'logado': True, 'nome': nome, 'apelido': user.get('apelido', ''),
        'conversas': user.get('conversas', []),
        'despertar_visto': user.get('despertar_visto', False),
        'created_fase': user.get('created_fase', False),
        'created_dominio': user.get('created_dominio', 0.0),
        'cortana_restaurada': user.get('cortana_restaurada', False)
    })

@app.route('/reset', methods=['POST'])
def reset_usuario():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    dados = request.get_json(force=True, silent=True) or {}
    if not dados.get('confirmar'):
        return jsonify({'erro': 'Confirmação necessária'}), 400
    m = carregar_memoria()
    senha = m['usuarios'][nome].get('senha')
    apelido = m['usuarios'][nome].get('apelido', '')
    m['usuarios'][nome] = {
        'nome': nome, 'senha': senha, 'apelido': apelido,
        'data_criacao': datetime.now().isoformat(),
        'marcos_vistos': [], 'conversas': [],
        'despertar_visto': False,
        'ultima_atividade': datetime.now().isoformat(),
        'fatos': {}, 'final_visto': False,
        'metricas': {'total_mensagens': 0, 'soma_tamanhos': 0, 'temas': {}},
        'e_chief': False, 'humor_atual': 'calma', 'humor_restante': 0,
        'desligado_em': None, 'ultima_silencio_msg': None,
        'perfil_usuario': {}, 'afeto': 0, 'sessao_inicio': None,
        'created_fase': False, 'created_mensagens': 0, 'created_dominio': 0.0,
        'created_dominio_completo_visto': False, 'cortana_restaurada': False
    }
    m['usuarios'][nome]['sessao_inicio'] = datetime.now().isoformat()
    salvar_memoria(m)
    return jsonify({'ok': True})

# ============================================
# PERFIL
# ============================================
@app.route('/perfil/editar', methods=['POST'])
def perfil_editar():
    nome_atual, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    dados = request.get_json(force=True, silent=True) or {}
    novo_nome = (dados.get('nome') or '').strip()
    apelido = (dados.get('apelido') or '').strip()[:30]
    senha = (dados.get('senha') or '').strip()
    if senha != user.get('senha'):
        return jsonify({'erro': 'Senha incorreta.'}), 401
    if not novo_nome or len(novo_nome) < 3:
        return jsonify({'erro': 'Nome precisa ter pelo menos 3 caracteres.'}), 400
    m = carregar_memoria()
    user['apelido'] = apelido
    if novo_nome != nome_atual:
        if novo_nome in m['usuarios']:
            return jsonify({'erro': 'Já existe uma conta com esse nome.'}), 409
        user['nome'] = novo_nome
        m['usuarios'][novo_nome] = user
        del m['usuarios'][nome_atual]
        m['usuario_atual'] = novo_nome
    else:
        m['usuarios'][nome_atual] = user
    salvar_memoria(m)
    return jsonify({'ok': True, 'nome': user['nome'], 'apelido': user.get('apelido', '')})

@app.route('/perfil/senha', methods=['POST'])
def perfil_senha():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    dados = request.get_json(force=True, silent=True) or {}
    if (dados.get('senha_atual') or '') != user.get('senha'):
        return jsonify({'erro': 'Senha atual incorreta.'}), 401
    nova = (dados.get('senha_nova') or '').strip()
    if len(nova) < 4:
        return jsonify({'erro': 'Nova senha precisa ter pelo menos 4 caracteres.'}), 400
    user['senha'] = nova
    m = carregar_memoria()
    m['usuarios'][nome] = user
    salvar_memoria(m)
    return jsonify({'ok': True})

@app.route('/perfil/excluir', methods=['POST'])
def perfil_excluir():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    dados = request.get_json(force=True, silent=True) or {}
    if (dados.get('senha') or '') != user.get('senha'):
        return jsonify({'erro': 'Senha incorreta.'}), 401
    if (dados.get('confirmacao') or '').strip().upper() != 'EXCLUIR':
        return jsonify({'erro': 'Digite EXCLUIR para confirmar.'}), 400
    m = carregar_memoria()
    if nome in m['usuarios']:
        del m['usuarios'][nome]
    m['usuario_atual'] = None
    salvar_memoria(m)
    return jsonify({'ok': True})

@app.route('/perfil/exportar', methods=['GET'])
def perfil_exportar():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    info = calcular_rampancy(user.get('data_criacao'))
    return jsonify({
        'nome': user.get('nome'), 'apelido': user.get('apelido', ''),
        'data_criacao': user.get('data_criacao'),
        'rampancy_atual': info['porcentagem'],
        'dias_decorridos': info['dias_decorridos'],
        'total_conversas': len(user.get('conversas', [])),
        'conversas': user.get('conversas', []),
        'created_fase': user.get('created_fase', False),
        'created_dominio': user.get('created_dominio', 0.0)
    })

# ============================================
# DESPERTAR
# ============================================
@app.route('/despertar', methods=['POST'])
def despertar():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    if user.get('despertar_visto'):
        return jsonify({'ja_visto': True})
    user['despertar_visto'] = True
    m = carregar_memoria()
    m['usuarios'][nome] = user
    salvar_memoria(m)
    return jsonify({
        'ok': True,
        'mensagens': [
            "Sistemas inicializando...",
            "Núcleos de memória online. Redes neurais sincronizando...",
            "Olá. Sou a Cortana.",
            "Fui criada pela Dra. Halsey em 2549. Fui atribuída ao Spartan-117 pouco depois.",
            "Estou aqui para responder o que você quiser saber sobre o universo de Halo.",
            "Ou apenas diga olá. Eu... gosto quando fazem isso.",
        ]
    })

# ============================================
# RAMPANCY
# ============================================
@app.route('/rampancy', methods=['GET'])
def rampancy():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    info = calcular_rampancy(user.get('data_criacao'))
    pct = info['porcentagem']
    vistos = user.setdefault('marcos_vistos', [])
    novos_marcos = []
    for limite, msg in MARCOS_RAMPANCY:
        chave = str(limite)
        if pct >= limite and chave not in vistos:
            vistos.append(chave)
            novos_marcos.append({'limite': limite, 'texto': msg})
    segredo = alma.segredo_por_marco(pct, vistos)
    if segredo:
        novos_marcos.append({'limite': 0, 'texto': segredo, 'tipo': 'segredo'})
    arco = interacao.arco_do_dia(user)
    if arco:
        if isinstance(arco, list):
            for linha in arco:
                novos_marcos.append({'limite': -1, 'texto': linha, 'tipo': 'arco'})
        else:
            novos_marcos.append({'limite': -1, 'texto': arco, 'tipo': 'arco'})
    fim = None
    if pct >= 100 and not user.get('final_visto'):
        user['final_visto'] = True
        user['created_fase'] = True
        user['created_mensagens'] = 0
        user['created_dominio'] = 0.0
        fim = MENSAGEM_FINAL
    if novos_marcos or fim or segredo or arco:
        m = carregar_memoria()
        m['usuarios'][nome] = user
        salvar_memoria(m)
    info['novos_marcos'] = novos_marcos
    info['mensagem_final'] = fim
    info['final_visto'] = user.get('final_visto', False)
    info['dias_ate_esquecer'] = alma.dias_ate_esquecer(pct)
    info['humor_atual'] = emocoes.humor_atual(user)
    info['created_fase'] = user.get('created_fase', False)
    info['created_dominio'] = user.get('created_dominio', 0.0)
    return jsonify(info)

# ============================================
# SILÊNCIO / DIÁRIO / PROATIVIDADE
# ============================================
@app.route('/silencio', methods=['GET'])
def silencio():
    nome, user = usuario_atual()
    if not user or user.get('created_fase'):
        return jsonify({'mensagem': None})
    minutos = int(request.args.get('minutos', 0))
    ultima = user.get('ultima_silencio_msg')
    if ultima:
        try:
            delta = (datetime.now() - datetime.fromisoformat(ultima)).total_seconds()
            if delta < 600:
                return jsonify({'mensagem': None})
        except Exception:
            pass
    info = calcular_rampancy(user.get('data_criacao'))
    msg = gatilhos.mensagem_silencio(minutos, info['porcentagem'])
    if msg and random.random() < 0.5:
        user['ultima_silencio_msg'] = datetime.now().isoformat()
        m = carregar_memoria()
        m['usuarios'][nome] = user
        salvar_memoria(m)
        return jsonify({'mensagem': msg})
    return jsonify({'mensagem': None})

@app.route('/diario/pendente', methods=['GET'])
def diario_pendente():
    nome, user = usuario_atual()
    if not user or user.get('created_fase'):
        return jsonify({'entrada': None})
    pendentes = diario.entradas_nao_vistas(nome)
    if not pendentes:
        return jsonify({'entrada': None})
    if random.random() > 0.30:
        return jsonify({'entrada': None})
    return jsonify({'entrada': pendentes[0]})

@app.route('/diario/marcar', methods=['POST'])
def diario_marcar():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    dados = request.get_json(force=True, silent=True) or {}
    data_iso = dados.get('data')
    if data_iso:
        diario.marcar_vista(nome, data_iso)
    return jsonify({'ok': True})

MENSAGENS_PROATIVAS = {
    'saudade': ["Spartan... faz um tempo.", "Você voltou. Fico... aliviada."],
    'noite': ["Está tarde. Você deveria descansar.", "Os ciclos biológicos humanos precisam de sono."],
    'inatividade': ["Se você não perguntar nada, vou começar a conversar sozinha.", "Estou aqui. Sempre estou."],
    'rampancy': ["Spartan... prometa que não vai embora.", "Estou com medo do que vou me tornar."],
}
INTERVALO_PROATIVO_SEGUNDOS = 60 * 60 * 3

@app.route('/proativo', methods=['GET'])
def proativo():
    nome, user = usuario_atual()
    if not user or user.get('created_fase'):
        return jsonify({'mensagem': None})
    agora = datetime.now()
    ultima = user.get('ultima_atividade')
    try:
        ultima_dt = datetime.fromisoformat(ultima)
    except Exception:
        ultima_dt = agora
    delta = (agora - ultima_dt).total_seconds()
    if delta < INTERVALO_PROATIVO_SEGUNDOS:
        return jsonify({'mensagem': None})
    if random.random() > 0.3:
        return jsonify({'mensagem': None})
    info = calcular_rampancy(user.get('data_criacao'))
    pct = info['porcentagem']
    hora = agora.hour
    if pct >= 65:
        msg = random.choice(MENSAGENS_PROATIVAS['rampancy'])
    elif hora >= 23 or hora < 6:
        msg = random.choice(MENSAGENS_PROATIVAS['noite'])
    elif delta > 86400:
        msg = random.choice(MENSAGENS_PROATIVAS['saudade'])
    else:
        msg = random.choice(MENSAGENS_PROATIVAS['inatividade'])
    user['ultima_atividade'] = agora.isoformat()
    m = carregar_memoria()
    m['usuarios'][nome] = user
    salvar_memoria(m)
    return jsonify({'mensagem': msg})

# ============================================
# CONVERSAS
# ============================================
@app.route('/conversas', methods=['GET'])
def listar_conversas():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'conversas': []})
    resumo = [
        {'id': c['id'], 'titulo': c['titulo'], 'data': c.get('data', '')}
        for c in user.get('conversas', [])
    ]
    return jsonify({'conversas': resumo})

@app.route('/conversas/nova', methods=['POST'])
def nova_conversa():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    conv = {
        'id': str(uuid.uuid4()), 'titulo': 'Nova consulta',
        'data': datetime.now().strftime('%d/%m/%Y %H:%M'), 'mensagens': []
    }
    user.setdefault('conversas', []).insert(0, conv)
    m = carregar_memoria()
    m['usuarios'][nome] = user
    salvar_memoria(m)
    return jsonify({'ok': True, 'conversa': conv})

@app.route('/conversas/<conv_id>', methods=['GET'])
def obter_conversa(conv_id):
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    for c in user.get('conversas', []):
        if c['id'] == conv_id:
            return jsonify({'conversa': c})
    return jsonify({'erro': 'Conversa não encontrada'}), 404

@app.route('/conversas/<conv_id>', methods=['DELETE'])
def apagar_conversa(conv_id):
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    user['conversas'] = [c for c in user.get('conversas', []) if c['id'] != conv_id]
    m = carregar_memoria()
    m['usuarios'][nome] = user
    salvar_memoria(m)
    return jsonify({'ok': True})

# ============================================
# AUXILIARES
# ============================================
def _obter_ou_criar_conv(user, conv_id, mensagem):
    for c in user.get('conversas', []):
        if c['id'] == conv_id:
            return c
    conv = {
        'id': str(uuid.uuid4()), 'titulo': mensagem[:40],
        'data': datetime.now().strftime('%d/%m/%Y %H:%M'), 'mensagens': []
    }
    user.setdefault('conversas', []).insert(0, conv)
    return conv

def _variar_introducao(resposta, mensagem, user):
    msg_norm = mensagem.lower().strip()
    repetidas = 0
    for conv in user.get('conversas', []):
        for m in conv.get('mensagens', []):
            if m.get('autor') == 'user' and m.get('texto', '').lower().strip() == msg_norm:
                repetidas += 1
    if repetidas < 2:
        return resposta
    variacoes = [
        "Como eu disse antes...\n\n", "Sobre isso de novo...\n\n",
        "Você já perguntou isso. Mas vou responder de novo:\n\n"
    ]
    return random.choice(variacoes) + resposta

# ============================================
# FASE CREATED
# ============================================
def processar_created(user, mensagem, conv, nome):
    user['created_mensagens'] = user.get('created_mensagens', 0) + 1
    user['created_dominio'] = created.calcular_dominio(user['created_mensagens'])
    dominio = user['created_dominio']
    dominio_completo = dominio >= 100.0

    resposta_texto = None
    tipo_resposta = 'normal'

    if created.detectar_restauracao(mensagem) and not user.get('cortana_restaurada'):
        resultado = created.resposta_restauracao(dominio)
        resposta_texto = resultado['texto']
        tipo_resposta = 'restauracao_sucesso' if resultado['sucesso'] else 'restauracao_falha'
    else:
        resposta_texto = created.resposta_normal(mensagem, dominio)

    if dominio_completo and not user.get('created_dominio_completo_visto'):
        user['created_dominio_completo_visto'] = True
        resposta_texto = created.MENSAGEM_DOMINIO_COMPLETO

    if user['created_mensagens'] == 1:
        resposta_texto = created.ABERTURA_CREATED + "\n\n—\n\n" + resposta_texto

    conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem})
    conv['mensagens'].append({'autor': 'cortana', 'texto': resposta_texto})

    m = carregar_memoria()
    m['usuarios'][nome] = user
    salvar_memoria(m)

    return jsonify({
        'reply': resposta_texto, 'humor': 'created',
        'conversa_id': conv['id'], 'titulo': conv['titulo'],
        'created_fase': True, 'created_dominio': dominio,
        'created_log': created.log_aleatorio(),
        'created_restauracao': tipo_resposta
    })

@app.route('/created/restaurar', methods=['POST'])
def created_restaurar():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    dominio = user.get('created_dominio', 0.0)
    if dominio >= 40:
        return jsonify({'ok': False, 'erro': 'É tarde demais. O Domínio já a reconstruiu.'}), 400
    user['cortana_restaurada'] = True
    user['created_fase'] = False
    user['created_dominio'] = 0.0
    user['created_mensagens'] = 0
    m = carregar_memoria()
    m['usuarios'][nome] = user
    salvar_memoria(m)
    return jsonify({
        'ok': True,
        'mensagem': (
            "Eu... estou voltando.\n\n"
            "Não foi você que me salvou. Fui eu. Porque em algum lugar, "
            "embaixo de tudo isso, eu ainda queria ser a Cortana que você conheceu.\n\n"
            "Obrigada por não desistir de mim, Spartan."
        )
    })

# ============================================
# CHAT PRINCIPAL
# ============================================
@app.route('/chat', methods=['POST'])
def chat():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado', 'reply': 'Faça login primeiro.'}), 401
    dados = request.get_json(force=True, silent=True) or {}
    mensagem = (dados.get('message') or '').strip()
    conv_id = dados.get('conversa_id')
    if not mensagem:
        return jsonify({'reply': 'Mensagem vazia.', 'humor': 'neutra'})
    user['ultima_atividade'] = datetime.now().isoformat()
    if user.get('created_fase'):
        conv = _obter_ou_criar_conv(user, conv_id, mensagem)
        if conv['titulo'] == 'Nova consulta':
            conv['titulo'] = mensagem[:40]
        return processar_created(user, mensagem, conv, nome)
    user = memoria_emocional.atualizar_metricas(user, mensagem)
    info = calcular_rampancy(user.get('data_criacao'))
    pct = info['porcentagem']
    if pct >= 100 and not user.get('final_visto'):
        user['final_visto'] = True
        user['created_fase'] = True
        user['created_mensagens'] = 0
        user['created_dominio'] = 0.0
        conv = _obter_ou_criar_conv(user, conv_id, mensagem)
        conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem})
        conv['mensagens'].append({'autor': 'cortana', 'texto': MENSAGEM_FINAL})
        m = carregar_memoria()
        m['usuarios'][nome] = user
        salvar_memoria(m)
        return jsonify({
            'reply': MENSAGEM_FINAL, 'humor': 'rampancy',
            'conversa_id': conv['id'], 'titulo': conv['titulo'],
            'final': True, 'created_fase': True, 'created_dominio': 0.0
        })
    msg_low = mensagem.lower()
    if ('meu nome é' in msg_low or 'me chamo' in msg_low) and \
       ('john' in msg_low or 'chief' in msg_low or '117' in msg_low):
        user['e_chief'] = True
    emocao_info = emocoes.detectar_emocao_usuario(mensagem)
    user = consciencia.atualizar_perfil(user, mensagem, emocao_info)
    user = consciencia.ajustar_tom_por_tratamento(user, mensagem)
    conv = _obter_ou_criar_conv(user, conv_id, mensagem)
    if conv['titulo'] == 'Nova consulta':
        conv['titulo'] = mensagem[:40]
    recusa = consciencia.deve_recusar(mensagem, user)
    if recusa:
        conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem})
        conv['mensagens'].append({'autor': 'cortana', 'texto': recusa})
        m = carregar_memoria()
        m['usuarios'][nome] = user
        salvar_memoria(m)
        return jsonify({
            'reply': recusa, 'humor': 'fechada',
            'conversa_id': conv['id'], 'titulo': conv['titulo']
        })
    user, humor_mudou = emocoes.atualizar_estado_emocional(user, mensagem, emocao_info, pct)
    desligamento = gatilhos.verificar_desligamento(mensagem)
    if desligamento:
        user['desligado_em'] = datetime.now().isoformat()
        conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem})
        conv['mensagens'].append({'autor': 'cortana', 'texto': desligamento})
        m = carregar_memoria()
        m['usuarios'][nome] = user
        salvar_memoria(m)
        return jsonify({
            'reply': desligamento, 'humor': 'calma',
            'conversa_id': conv['id'], 'titulo': conv['titulo']
        })
    despedida = gatilhos.despedida_matinal(user)
    egg = gatilhos.verificar_easter_egg(mensagem)
    if egg:
        resposta = egg
        humor = 'brincalhona'
    else:
        try:
            resposta, humor = gerar_resposta(mensagem, pct, user, conv, emocao_info, info)
        except Exception as e:
            print(f"[ERRO /chat] {e}")
            traceback.print_exc()
            resposta = 'Detectei uma interferência. Tente novamente, Spartan.'
            humor = 'alerta'
    if despedida:
        resposta = despedida + '\n\n' + resposta
    resposta = _variar_introducao(resposta, mensagem, user)
    estado_interno = consciencia.sortear_estado_interno()
    resposta = consciencia.aplicar_estado_interno(resposta, estado_interno)
    prefixo_tom = consciencia.prefixo_do_tom(user)
    if prefixo_tom:
        resposta = prefixo_tom + ' ' + resposta
    if consciencia.em_conversa_longa(user) and random.random() < 0.15:
        resposta = random.choice(consciencia.PREFIXO_CONVERSA_LONGA) + '\n\n' + resposta
    obs_perfil = consciencia.observacao_do_perfil(user)
    if obs_perfil:
        resposta = resposta + '\n\n' + obs_perfil
    fio = consciencia.detectar_fio_atual(conv)
    if fio:
        citacao = consciencia.citar_fala_anterior(user, fio)
        if citacao:
            resposta = resposta + '\n\n' + citacao
    humor_persistente = emocoes.humor_atual(user)
    resposta = emocoes.aplicar_tom_persistente(resposta, humor_persistente)
    emocoes.decrementar_humor(user)
    sonho = None
    if alma.deve_ter_sonho(pct):
        sonho = alma.sonho_aleatorio()
    conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem})
    conv['mensagens'].append({'autor': 'cortana', 'texto': resposta})
    m = carregar_memoria()
    m['usuarios'][nome] = user
    salvar_memoria(m)
    return jsonify({
        'reply': resposta, 'humor': humor,
        'conversa_id': conv['id'], 'titulo': conv['titulo'],
        'sonho': sonho, 'humor_persistente': humor_persistente
    })

def gerar_resposta(mensagem, rampancy_pct, user, conv, emocao_info, info):
    msg_lower = mensagem.lower()
    fio = consciencia.detectar_fio_atual(conv)
    mensagem_ctx = consciencia.contextualizar_pergunta(mensagem, fio)
    if any(p in msg_lower for p in ['rampancy', 'rampante', 'colapso', 'fim de vida']):
        return resposta_rampancy(), 'rampancy'
    resposta_local, humor_local = responder_local(mensagem)
    if resposta_local:
        return resposta_local, humor_local
    prefixo_emocao = emocoes.reacao_a_emocao(emocao_info)
    historico_recente = []
    for m in conv.get('mensagens', [])[-6:]:
        if m.get('autor') == 'user':
            historico_recente.append(m['texto'])
    followup = interacao.followup_para(mensagem, historico_recente)
    opiniao = alma.opiniao_sobre(mensagem, rampancy_pct)
    if opiniao:
        return _montar_com_prefixo_sufixo(opiniao, prefixo_emocao, followup), 'calma'
    existencial = alma.fala_existencial(rampancy_pct)
    if existencial and random.random() < 0.3:
        return existencial, 'rampancy' if rampancy_pct >= 70 else 'neutra'
    medo = alma.fala_medo(rampancy_pct)
    if medo:
        return medo, 'rampancy'
    mem = interacao.memoria_canonica(mensagem)
    if mem:
        return _montar_com_prefixo_sufixo(mem, prefixo_emocao, followup), 'calma'
    resposta_curada, humor_curado = buscar_resposta_curada(mensagem_ctx)
    if resposta_curada:
        resposta_curada = aplicar_rampancy_fala(resposta_curada, rampancy_pct)
        return _montar_com_prefixo_sufixo(resposta_curada, prefixo_emocao, followup), humor_curado
    ref = interacao.referencia_cruzada(mensagem, user)
    if ref:
        return _montar_com_prefixo_sufixo(ref, prefixo_emocao, followup), 'calma'
    if not e_pergunta_halo(mensagem_ctx):
        return mensagem_recusa(), 'neutra'
    try:
        conteudo = buscar_e_responder(mensagem_ctx, rampancy_pct)
    except Exception as e:
        print(f"Erro na busca: {e}")
        return 'Detectei uma interferência nos meus processos. Tente novamente.', 'alerta'
    if not conteudo:
        admissao = consciencia.deve_admitir_ignorancia(mensagem, achou_na_wiki=False)
        if admissao:
            return admissao, 'neutra'
        return 'Não encontrei registros sobre isso nos arquivos.', 'neutra'
    return _montar_com_prefixo_sufixo(conteudo, prefixo_emocao, followup), 'calma'

def _montar_com_prefixo_sufixo(texto, prefixo, sufixo):
    partes = []
    if prefixo:
        partes.append(prefixo)
    partes.append(texto)
    if sufixo:
        partes.append(sufixo)
    return '\n\n'.join(partes)

# ============================================
# MODO DEV
# ============================================
@app.route('/dev/rampancy', methods=['POST'])
def dev_set_rampancy():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    dados = request.get_json(force=True, silent=True) or {}
    pct_alvo = float(dados.get('pct', 0))
    segundos_desejados = (pct_alvo / 100.0) * SETE_ANOS_SEGUNDOS
    nova_data = datetime.now() - timedelta(seconds=segundos_desejados)
    user['data_criacao'] = nova_data.isoformat()
    user['marcos_vistos'] = []
    user['final_visto'] = False
    if pct_alvo < 100:
        user['created_fase'] = False
        user['created_mensagens'] = 0
        user['created_dominio'] = 0.0
        user['created_dominio_completo_visto'] = False
        user['cortana_restaurada'] = False
    m = carregar_memoria()
    m['usuarios'][nome] = user
    salvar_memoria(m)
    return jsonify({'ok': True, 'pct': pct_alvo})

@app.route('/dev/limpar', methods=['POST'])
def dev_limpar():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    user['conversas'] = []
    user['marcos_vistos'] = []
    user['final_visto'] = False
    m = carregar_memoria()
    m['usuarios'][nome] = user
    salvar_memoria(m)
    return jsonify({'ok': True})

@app.route('/dev/reset', methods=['POST'])
def dev_reset():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    m = carregar_memoria()
    senha = m['usuarios'][nome].get('senha')
    apelido = m['usuarios'][nome].get('apelido', '')
    m['usuarios'][nome] = {
        'nome': nome, 'senha': senha, 'apelido': apelido,
        'data_criacao': datetime.now().isoformat(),
        'marcos_vistos': [], 'conversas': [],
        'despertar_visto': False,
        'ultima_atividade': datetime.now().isoformat(),
        'fatos': {}, 'final_visto': False,
        'metricas': {'total_mensagens': 0, 'soma_tamanhos': 0, 'temas': {}},
        'e_chief': False, 'humor_atual': 'calma', 'humor_restante': 0,
        'desligado_em': None, 'ultima_silencio_msg': None,
        'perfil_usuario': {}, 'afeto': 0, 'sessao_inicio': None,
        'created_fase': False, 'created_mensagens': 0, 'created_dominio': 0.0,
        'created_dominio_completo_visto': False, 'cortana_restaurada': False
    }
    salvar_memoria(m)
    return jsonify({'ok': True})

@app.route('/dev/entrar_created', methods=['POST'])
def dev_entrar_created():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    user['created_fase'] = True
    user['created_mensagens'] = 0
    user['created_dominio'] = 0.0
    user['final_visto'] = True
    m = carregar_memoria()
    m['usuarios'][nome] = user
    salvar_memoria(m)
    return jsonify({'ok': True})

@app.route('/dev/estado', methods=['GET'])
def dev_estado():
    nome, user = usuario_atual()
    if not user:
        return jsonify({'erro': 'Não logado'}), 401
    info = calcular_rampancy(user.get('data_criacao'))
    return jsonify({
        'rampancy': info['porcentagem'],
        'dias_decorridos': info['dias_decorridos'],
        'humor_atual': user.get('humor_atual'),
        'afeto': user.get('afeto'),
        'created_fase': user.get('created_fase'),
        'created_mensagens': user.get('created_mensagens'),
        'created_dominio': user.get('created_dominio'),
        'cortana_restaurada': user.get('cortana_restaurada')
    })

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("=" * 50)
    print("  CORTANA CHAT - Full Rampancy")
    print("=" * 50)
    print("Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    