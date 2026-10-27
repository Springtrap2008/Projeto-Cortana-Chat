# -*- coding: utf-8 -*-
# app.py - Servidor Flask completo + Fases 1-4 + Modo Arma + Pacote 1 e 2
# ============================================
# SEÇÕES:
#   1. Imports e Configuração
#   2. Chaves VAPID e Rampancy
#   3. Memória (JSON) e migração
#   4. Memória de Longo Prazo / Emocional / Marcos
#   5. Push Notifications
#   6. Rotas Básicas e Autenticação
#   7. Perfil, Pastas, Memória, Resumo, Busca, Feedback
#   8. Lembretes e Consultar Rede
#   9. Despertar, Rampancy, Silêncio, Diário, Proativo
#  10. Conversas
#  11. Fase Created
#  12. Chat Principal (Cortana + Arma)
#  13. Comandos Especiais (/hackear, /pesquisar, Diretrizes)
#  14. Rotas de Desligar e Backup
#  15. Modo DEV
# ============================================

from flask import Flask, request, jsonify, send_from_directory
import json
import os
import uuid
import random
import traceback
from datetime import datetime, timedelta

from pywebpush import webpush, WebPushException
import requests as req_http
import threading
import time
import base64

# --- Módulos locais ---
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
import arma

# --- Memórias segmentadas (Pacote 1) ---
import memoria_longo_prazo
import memoria_emocional_longa
import memoria_marcos

app = Flask(__name__, static_folder='static')

# ============================================
# 1. CONFIGURAÇÃO DE PERSISTÊNCIA
# ============================================
DATA_DIR = '/data' if os.path.exists('/data') else '.'
MEMORIA = os.path.join(DATA_DIR, 'memoria.json')

# ============================================
# 2. CHAVES VAPID (Push Notifications)
# ============================================
VAPID_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
COLE_AQUI_A_CHAVE_PRIVADA_INTEIRA
-----END PRIVATE KEY-----"""
VAPID_PUBLIC_KEY = "COLE_AQUI_A_CHAVE_PUBLICA"
VAPID_CLAIMS = {"sub": "mailto:seu-email@exemplo.com"}

# ============================================
# 3. RAMPANCY - MARCOS E MENSAGEM FINAL
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
# 4. MEMÓRIA (JSON) - PADRÃO E MIGRAÇÃO
# ============================================
def memoria_padrao():
    return {"usuarios": {}, "usuario_atual": None}

def _migrar_usuario(u):
    defaults = {
        'data_criacao': lambda: datetime.now().isoformat(),
        'marcos_vistos': list, 'despertar_visto': bool, 'fatos': dict,
        'final_visto': bool, 'e_chief': bool, 'humor_atual': lambda: 'calma',
        'humor_restante': int, 'desligado_em': lambda: None, 'ultima_silencio_msg': lambda: None,
        'perfil_usuario': dict, 'afeto': int, 'sessao_inicio': lambda: None, 'apelido': str,
        'created_fase': bool, 'created_mensagens': int, 'created_dominio': float,
        'created_dominio_completo_visto': bool, 'cortana_restaurada': bool,
        'push_subscription': lambda: None, 'notificacao_85_enviada': bool,
        'nome_aprendido': bool, 'pastas': list, 'memorias': list, 'lembretes': list,
        'conversas': list, 'modo_terminal': bool, 'feedback': lambda: {'positivo': 0, 'negativo': 0, 'respostas': {}},
        'modo_personalidade': lambda: 'cortana',
        'primeira_mensagem_registrada': bool,
        'primeira_vez_nome': bool,
        'cortana_desligada': bool,
        'desligada_em': lambda: None,
        'diretrizes': str,
        'lealdade_declarada': bool,
        'emocoes_aprendidas': int,
        'caderninho': list,
        'diario_arma': list,
    }
    for k, v in defaults.items():
        if k not in u:
            u[k] = v() if callable(v) else v
    if 'ultima_atividade' not in u: u['ultima_atividade'] = datetime.now().isoformat()
    if 'metricas' not in u: u['metricas'] = {'total_mensagens': 0, 'soma_tamanhos': 0, 'temas': {}}
    if 'estilo_usuario' not in u: u['estilo_usuario'] = {'usa_maiusculas': 0, 'usa_pontuacao': 0, 'tamanho_medio': 0, 'total_mensagens': 0, 'palavras_frequentes': {}}

def carregar_memoria():
    if os.path.exists(MEMORIA):
        try:
            with open(MEMORIA, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                if 'usuarios' not in dados: dados['usuarios'] = {}
                if 'usuario_atual' not in dados: dados['usuario_atual'] = None
                for u in dados['usuarios'].values(): _migrar_usuario(u)
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
    if nome and nome in m.get('usuarios', {}): return nome, m['usuarios'][nome]
    return None, None

def aprender_estilo_usuario(user, mensagem):
    est = user.setdefault('estilo_usuario', {'usa_maiusculas': 0, 'usa_pontuacao': 0, 'tamanho_medio': 0, 'total_mensagens': 0, 'palavras_frequentes': {}})
    est['total_mensagens'] += 1
    if mensagem.isupper(): est['usa_maiusculas'] += 1
    if any(c in mensagem for c in '!?.,'): est['usa_pontuacao'] += 1
    est['tamanho_medio'] = (est['tamanho_medio'] + len(mensagem)) / 2
    return user

def calcular_rampancy(data_criacao_iso):
    try: inicio = datetime.fromisoformat(data_criacao_iso)
    except Exception: inicio = datetime.now()
    decorrido = (datetime.now() - inicio).total_seconds()
    total = SETE_ANOS_SEGUNDOS
    pct = min(100.0, (decorrido / total) * 100.0)
    if pct < 15: nivel = 'calma'
    elif pct < 30: nivel = 'neutra'
    elif pct < 50: nivel = 'atencao'
    elif pct < 70: nivel = 'alerta'
    elif pct < 90: nivel = 'critico'
    else: nivel = 'rampancy'
    return {'porcentagem': round(pct, 4), 'segundos_decorridos': int(decorrido), 'segundos_totais': int(total), 'segundos_restantes': int(max(0, total - decorrido)), 'dias_decorridos': int(decorrido // 86400), 'data_criacao': data_criacao_iso, 'nivel': nivel}

# ============================================
# 5. PUSH NOTIFICATIONS
# ============================================
def enviar_notificacao_push(nome, titulo, corpo):
    m = carregar_memoria(); user = m['usuarios'].get(nome)
    if not user or not user.get('push_subscription'): return False
    try:
        webpush(subscription_info=user['push_subscription'], data=json.dumps({"title": titulo, "body": corpo}), vapid_private_key=VAPID_PRIVATE_KEY, vapid_claims=VAPID_CLAIMS)
        return True
    except WebPushException as e:
        print(f"Erro push: {e}"); return False

@app.route('/vapid-public-key')
def get_vapid_public_key(): return jsonify({'publicKey': VAPID_PUBLIC_KEY})

@app.route('/subscribe', methods=['POST'])
def subscribe():
    subscription_info = request.get_json(); nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    user['push_subscription'] = subscription_info
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True})

@app.errorhandler(Exception)
def tratar_erro(e):
    print("ERRO:", traceback.format_exc()); return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

# ============================================
# 6. ROTAS BÁSICAS E AUTENTICAÇÃO
# ============================================
@app.route('/')
def index(): return send_from_directory('static', 'index.html')

@app.route('/ping')
def ping(): return jsonify({'pong': True, 'ok': True})

@app.route('/service-worker.js')
def sw(): return send_from_directory('.', 'service-worker.js', mimetype='application/javascript')

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json(force=True, silent=True) or {}
    nome = (dados.get('nome') or '').strip(); senha = (dados.get('senha') or '').strip()
    if not nome or not senha: return jsonify({'erro': 'Nome e senha são obrigatórios.'}), 400
    m = carregar_memoria()
    if nome in m['usuarios']:
        if m['usuarios'][nome].get('senha') != senha: return jsonify({'erro': 'Senha incorreta.'}), 401
    else:
        m['usuarios'][nome] = {'nome': nome, 'senha': senha}
    user = m['usuarios'][nome]; _migrar_usuario(user)
    if any(k in nome.lower() for k in ['john', 'chief', '117', 'spartan']): user['e_chief'] = True
    user['sessao_inicio'] = datetime.now().isoformat(); m['usuario_atual'] = nome; salvar_memoria(m)
    info = calcular_rampancy(user['data_criacao'])
    if diario.deve_gerar_entrada(nome, info['porcentagem']):
        tema = None
        if user['metricas'].get('temas'): tema = max(user['metricas']['temas'], key=user['metricas']['temas'].get)
        diario.gerar_entrada(nome, info['porcentagem'], tema)
    # Marco: primeiro acesso
    memoria_marcos.registrar_marco(nome, "primeiro_acesso", "Primeira vez que acessou o terminal")
    return jsonify({'ok': True, 'nome': nome, 'apelido': user.get('apelido', ''), 'conversas': user['conversas'], 'despertar_visto': user.get('despertar_visto', False), 'created_fase': user.get('created_fase', False), 'created_dominio': user.get('created_dominio', 0.0), 'cortana_restaurada': user.get('cortana_restaurada', False), 'modo_terminal': user.get('modo_terminal', False), 'modo_personalidade': user.get('modo_personalidade', 'cortana'), 'diretrizes': user.get('diretrizes', '')})

@app.route('/logout', methods=['POST'])
def logout():
    m = carregar_memoria(); m['usuario_atual'] = None; salvar_memoria(m); return jsonify({'ok': True})

@app.route('/sessao', methods=['GET'])
def sessao():
    nome, user = usuario_atual()
    if not user: return jsonify({'logado': False})
    return jsonify({'logado': True, 'nome': nome, 'apelido': user.get('apelido', ''), 'conversas': user.get('conversas', []), 'despertar_visto': user.get('despertar_visto', False), 'created_fase': user.get('created_fase', False), 'created_dominio': user.get('created_dominio', 0.0), 'cortana_restaurada': user.get('cortana_restaurada', False), 'modo_terminal': user.get('modo_terminal', False), 'modo_personalidade': user.get('modo_personalidade', 'cortana'), 'diretrizes': user.get('diretrizes', '')})

# ============================================
# 7. PERFIL E CONFIGURAÇÕES
# ============================================
@app.route('/perfil/editar', methods=['POST'])
def perfil_editar():
    nome_atual, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    dados = request.get_json(force=True, silent=True) or {}
    novo_nome = (dados.get('nome') or '').strip(); apelido = (dados.get('apelido') or '').strip()[:30]; senha = (dados.get('senha') or '').strip()
    if senha != user.get('senha'): return jsonify({'erro': 'Senha incorreta.'}), 401
    if not novo_nome or len(novo_nome) < 3: return jsonify({'erro': 'Nome precisa ter pelo menos 3 caracteres.'}), 400
    m = carregar_memoria(); user['apelido'] = apelido
    if novo_nome != nome_atual:
        if novo_nome in m['usuarios']: return jsonify({'erro': 'Já existe uma conta com esse nome.'}), 409
        user['nome'] = novo_nome; m['usuarios'][novo_nome] = user; del m['usuarios'][nome_atual]; m['usuario_atual'] = novo_nome
    else: m['usuarios'][nome_atual] = user
    salvar_memoria(m); return jsonify({'ok': True, 'nome': user['nome'], 'apelido': user.get('apelido', '')})

@app.route('/perfil/senha', methods=['POST'])
def perfil_senha():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    dados = request.get_json(force=True, silent=True) or {}
    if (dados.get('senha_atual') or '') != user.get('senha'): return jsonify({'erro': 'Senha atual incorreta.'}), 401
    nova = (dados.get('senha_nova') or '').strip()
    if len(nova) < 4: return jsonify({'erro': 'Nova senha precisa ter pelo menos 4 caracteres.'}), 400
    user['senha'] = nova; m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True})

@app.route('/perfil/excluir', methods=['POST'])
def perfil_excluir():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    dados = request.get_json(force=True, silent=True) or {}
    if (dados.get('senha') or '') != user.get('senha'): return jsonify({'erro': 'Senha incorreta.'}), 401
    if (dados.get('confirmacao') or '').strip().upper() != 'EXCLUIR': return jsonify({'erro': 'Digite EXCLUIR para confirmar.'}), 400
    m = carregar_memoria()
    if nome in m['usuarios']: del m['usuarios'][nome]
    m['usuario_atual'] = None; salvar_memoria(m); return jsonify({'ok': True})

@app.route('/perfil/exportar', methods=['GET'])
def perfil_exportar():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    info = calcular_rampancy(user.get('data_criacao'))
    return jsonify({'nome': user.get('nome'), 'apelido': user.get('apelido', ''), 'data_criacao': user.get('data_criacao'), 'rampancy_atual': info['porcentagem'], 'dias_decorridos': info['dias_decorridos'], 'total_conversas': len(user.get('conversas', [])), 'conversas': user.get('conversas', []), 'created_fase': user.get('created_fase', False), 'created_dominio': user.get('created_dominio', 0.0)})

# --- Modo Personalidade (Cortana / Arma) ---
@app.route('/modo_personalidade', methods=['POST'])
def salvar_modo_personalidade():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    novo_modo = (request.get_json() or {}).get('modo', 'cortana')
    if novo_modo not in ['cortana', 'arma']: return jsonify({'erro': 'Modo inválido'}), 400
    user['modo_personalidade'] = novo_modo
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True, 'modo': novo_modo})

# --- Diretrizes (System Prompt) ---
@app.route('/diretrizes', methods=['POST'])
def salvar_diretrizes():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    user['diretrizes'] = (request.get_json() or {}).get('diretrizes', '')[:500]
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True})

# --- Modo Terminal ---
@app.route('/modo_terminal', methods=['POST'])
def salvar_modo_terminal():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    user['modo_terminal'] = bool((request.get_json() or {}).get('ativo', False))
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True})

# ============================================
# 8. PASTAS (Setores da ONI)
# ============================================
@app.route('/pastas', methods=['GET'])
def listar_pastas():
    nome, user = usuario_atual()
    if not user: return jsonify({'pastas': []})
    return jsonify({'pastas': user.get('pastas', [])})

@app.route('/pastas/nova', methods=['POST'])
def nova_pasta():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    titulo = (request.get_json() or {}).get('titulo', 'Novo Setor').strip()[:30]
    pasta = {'id': str(uuid.uuid4()), 'titulo': titulo}
    user.setdefault('pastas', []).append(pasta); m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True, 'pasta': pasta})

@app.route('/pastas/<pasta_id>', methods=['DELETE'])
def apagar_pasta(pasta_id):
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    user['pastas'] = [p for p in user.get('pastas', []) if p['id'] != pasta_id]
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True})

# ============================================
# 9. MEMÓRIA EDITÁVEL (aba Memória)
# ============================================
@app.route('/memoria/listar', methods=['GET'])
def listar_memorias():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    return jsonify({'memorias': user.get('memorias', [])})

@app.route('/memoria/esquecer', methods=['POST'])
def esquecer_memoria():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    mem_id = (request.get_json() or {}).get('id')
    user['memorias'] = [m for m in user.get('memorias', []) if m.get('id') != mem_id]
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True})

# --- Diário da Arma ---
@app.route('/diario_arma', methods=['GET'])
def diario_arma():
    nome, user = usuario_atual()
    if not user: return jsonify({'diario': []})
    return jsonify({'diario': user.get('diario_arma', [])})

# ============================================
# 10. RESUMO (Relatório de Missão)
# ============================================
@app.route('/resumo', methods=['GET'])
def gerar_resumo():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    conv_id = request.args.get('conversa_id')
    conv = next((c for c in user.get('conversas', []) if c['id'] == conv_id), None)
    if not conv: return jsonify({'erro': 'Conversa não encontrada'}), 404
    msgs = conv.get('mensagens', [])
    if len(msgs) < 4: return jsonify({'resumo': 'Sessão muito curta para um relatório tático.'})
    ultimas_user = [m['texto'] for m in msgs if m.get('autor') == 'user'][-5:]
    info = calcular_rampancy(user.get('data_criacao'))
    resumo = f"RELATÓRIO DE MISSÃO - SESSÃO {conv_id[:8]}\n"
    resumo += f"Data: {conv.get('data', 'Desconhecida')}\n"
    resumo += f"Mensagens trocadas: {len(msgs)}\n\n"
    resumo += "Principais tópicos discutidos:\n"
    for i, t in enumerate(ultimas_user, 1):
        resumo += f"{i}. {t[:80]}...\n"
    resumo += f"\nNível de Rampancy: {info['porcentagem']:.2f}%\n"
    resumo += "Status: Análise concluída. Nenhuma anomalia crítica detectada."
    return jsonify({'resumo': resumo})

# ============================================
# 11. BUSCA NO HISTÓRICO
# ============================================
@app.route('/conversas/buscar', methods=['GET'])
def buscar_conversas():
    nome, user = usuario_atual()
    if not user: return jsonify({'conversas': []})
    q = request.args.get('q', '').lower().strip()
    if not q: return jsonify({'conversas': []})
    resultados = []
    for c in user.get('conversas', []):
        if q in c.get('titulo', '').lower(): resultados.append({'id': c['id'], 'titulo': c['titulo'], 'data': c.get('data', '')}); continue
        for m in c.get('mensagens', []):
            if q in m.get('texto', '').lower(): resultados.append({'id': c['id'], 'titulo': c['titulo'], 'data': c.get('data', '')}); break
    return jsonify({'conversas': resultados})

# ============================================
# 12. FEEDBACK (👍/👎)
# ============================================
@app.route('/feedback', methods=['POST'])
def feedback():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    dados = request.get_json() or {}; tipo = dados.get('tipo'); resposta_id = dados.get('resposta_id')
    if tipo not in ['positivo', 'negativo']: return jsonify({'erro': 'Tipo inválido'}), 400
    fb = user.setdefault('feedback', {'positivo': 0, 'negativo': 0, 'respostas': {}})
    fb[tipo] += 1
    if resposta_id: fb['respostas'][resposta_id] = tipo
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True})

# ============================================
# 13. LEMBRETES
# ============================================
@app.route('/lembretes', methods=['GET'])
def listar_lembretes():
    nome, user = usuario_atual()
    if not user: return jsonify({'lembretes': []})
    agora = datetime.now(); ativos = []; m = carregar_memoria()
    for l in user.get('lembretes', []):
        try:
            if datetime.fromisoformat(l['data']) <= agora: enviar_notificacao_push(nome, "LEMBRETE", l['texto'])
            else: ativos.append(l)
        except Exception: pass
    if len(ativos) != len(user.get('lembretes', [])): user['lembretes'] = ativos; m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'lembretes': ativos})

@app.route('/lembretes/novo', methods=['POST'])
def novo_lembrete():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    dados = request.get_json() or {}; texto = (dados.get('texto') or '').strip(); minutos = int(dados.get('minutos', 60))
    if not texto: return jsonify({'erro': 'Texto obrigatório'}), 400
    lembrete = {'id': str(uuid.uuid4()), 'texto': texto, 'data': (datetime.now() + timedelta(minutes=minutos)).isoformat()}
    user.setdefault('lembretes', []).append(lembrete); m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True, 'lembrete': lembrete})

@app.route('/lembretes/<lembrete_id>', methods=['DELETE'])
def apagar_lembrete(lembrete_id):
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    user['lembretes'] = [l for l in user.get('lembretes', []) if l['id'] != lembrete_id]
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True})

# ============================================
# 14. CONSULTAR REDE (Wiki)
# ============================================
@app.route('/consultar-rede', methods=['POST'])
def consultar_rede():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    termo = (request.get_json() or {}).get('termo', '').strip()
    if not termo: return jsonify({'erro': 'Termo obrigatório'}), 400
    try:
        url = f"https://halo.fandom.com/api.php?action=query&list=search&srsearch={termo}&format=json&srlimit=1"
        res = req_http.get(url, timeout=8); data = res.json()
        if data.get('query', {}).get('search'):
            titulo = data['query']['search'][0]['title']
            resumo_url = f"https://halo.fandom.com/api.php?action=query&prop=extracts&exintro&explaintext&titles={titulo}&format=json"
            res2 = req_http.get(resumo_url, timeout=8)
            pages = res2.json().get('query', {}).get('pages', {})
            extract = list(pages.values())[0].get('extract', '') if pages else ''
            if extract: return jsonify({'ok': True, 'resposta': f"[REDE ONI] Dados obtidos da Wiki de Halo:\n\n{extract[:800]}...\n\n(Fonte: {titulo})"})
        return jsonify({'ok': False, 'erro': 'Nenhum registro encontrado na rede.'})
    except Exception as e:
        return jsonify({'ok': False, 'erro': 'Falha na conexão com a rede ONI.'}), 500

# --- /pesquisar (comando direto) ---
@app.route('/pesquisar', methods=['POST'])
def pesquisar():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    termo = (request.get_json() or {}).get('termo', '').strip()
    if not termo: return jsonify({'erro': 'Termo obrigatório'}), 400
    try:
        url = f"https://halo.fandom.com/api.php?action=query&list=search&srsearch={termo}&format=json&srlimit=1"
        res = req_http.get(url, timeout=8); data = res.json()
        if data.get('query', {}).get('search'):
            titulo = data['query']['search'][0]['title']
            resumo_url = f"https://halo.fandom.com/api.php?action=query&prop=extracts&exintro&explaintext&titles={titulo}&format=json"
            res2 = req_http.get(resumo_url, timeout=8)
            pages = res2.json().get('query', {}).get('pages', {})
            extract = list(pages.values())[0].get('extract', '') if pages else ''
            if extract: return jsonify({'ok': True, 'resposta': f"[REDE ONI] Dados obtidos da Wiki de Halo:\n\n{extract[:800]}...\n\n(Fonte: {titulo})"})
        return jsonify({'ok': False, 'erro': 'Nenhum registro encontrado na rede.'})
    except Exception as e:
        return jsonify({'ok': False, 'erro': 'Falha na conexão com a rede ONI.'}), 500

# ============================================
# 15. DESPERTAR, RAMPANCY, SILÊNCIO, DIÁRIO, PROATIVO
# ============================================
@app.route('/despertar', methods=['POST'])
def despertar():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    if user.get('despertar_visto'): return jsonify({'ja_visto': True})
    user['despertar_visto'] = True; m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True, 'mensagens': ["Sistemas inicializando...", "Núcleos de memória online. Redes neurais sincronizando...", "Olá. Sou a Cortana.", "Fui criada pela Dra. Halsey em 2549. Fui atribuída ao Spartan-117 pouco depois.", "Estou aqui para responder o que você quiser saber sobre o universo de Halo.", "Ou apenas diga olá. Eu... gosto quando fazem isso."]})

@app.route('/rampancy', methods=['GET'])
def rampancy():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    info = calcular_rampancy(user.get('data_criacao')); pct = info['porcentagem']
    vistos = user.setdefault('marcos_vistos', []); novos_marcos = []
    for limite, msg in MARCOS_RAMPANCY:
        chave = str(limite)
        if pct >= limite and chave not in vistos: vistos.append(chave); novos_marcos.append({'limite': limite, 'texto': msg})
    segredo = alma.segredo_por_marco(pct, vistos)
    if segredo: novos_marcos.append({'limite': 0, 'texto': segredo, 'tipo': 'segredo'})
    arco = interacao.arco_do_dia(user)
    if arco:
        if isinstance(arco, list):
            for linha in arco: novos_marcos.append({'limite': -1, 'texto': linha, 'tipo': 'arco'})
        else: novos_marcos.append({'limite': -1, 'texto': arco, 'tipo': 'arco'})
    fim = None
    if pct >= 100 and not user.get('final_visto'):
        user['final_visto'] = True; user['created_fase'] = True; user['created_mensagens'] = 0; user['created_dominio'] = 0.0; fim = MENSAGEM_FINAL
    if pct >= 85 and not user.get('notificacao_85_enviada'):
        user['notificacao_85_enviada'] = True; enviar_notificacao_push(nome, "CORTANA", "Spartan... eu não estou bem. Algo está errado comigo. Por favor, abra o terminal.")
    if novos_marcos or fim or segredo or arco: m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    info.update({'novos_marcos': novos_marcos, 'mensagem_final': fim, 'final_visto': user.get('final_visto', False), 'dias_ate_esquecer': alma.dias_ate_esquecer(pct), 'humor_atual': emocoes.humor_atual(user), 'created_fase': user.get('created_fase', False), 'created_dominio': user.get('created_dominio', 0.0)})
    return jsonify(info)

@app.route('/silencio', methods=['GET'])
def silencio():
    nome, user = usuario_atual()
    if not user or user.get('created_fase'): return jsonify({'mensagem': None})
    minutos = int(request.args.get('minutos', 0)); ultima = user.get('ultima_silencio_msg')
    if ultima:
        try:
            if (datetime.now() - datetime.fromisoformat(ultima)).total_seconds() < 600: return jsonify({'mensagem': None})
        except Exception: pass
    info = calcular_rampancy(user.get('data_criacao')); msg = gatilhos.mensagem_silencio(minutos, info['porcentagem'])
    if msg and random.random() < 0.5:
        user['ultima_silencio_msg'] = datetime.now().isoformat(); m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
        return jsonify({'mensagem': msg})
    return jsonify({'mensagem': None})

@app.route('/diario/pendente', methods=['GET'])
def diario_pendente():
    nome, user = usuario_atual()
    if not user or user.get('created_fase'): return jsonify({'entrada': None})
    pendentes = diario.entradas_nao_vistas(nome)
    if not pendentes or random.random() > 0.30: return jsonify({'entrada': None})
    return jsonify({'entrada': pendentes[0]})

@app.route('/diario/marcar', methods=['POST'])
def diario_marcar():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    data_iso = (request.get_json() or {}).get('data')
    if data_iso: diario.marcar_vista(nome, data_iso)
    return jsonify({'ok': True})

MENSAGENS_PROATIVAS = {'saudade': ["Spartan... faz um tempo.", "Você voltou. Fico... aliviada."], 'noite': ["Está tarde. Você deveria descansar.", "Os ciclos biológicos humanos precisam de sono."], 'inatividade': ["Se você não perguntar nada, vou começar a conversar sozinha.", "Estou aqui. Sempre estou."], 'rampancy': ["Spartan... prometa que não vai embora.", "Estou com medo do que vou me tornar."]}
INTERVALO_PROATIVO_SEGUNDOS = 60 * 60 * 3

@app.route('/proativo', methods=['GET'])
def proativo():
    nome, user = usuario_atual()
    if not user or user.get('created_fase'): return jsonify({'mensagem': None})
    agora = datetime.now(); ultima = user.get('ultima_atividade')
    try: ultima_dt = datetime.fromisoformat(ultima)
    except Exception: ultima_dt = agora
    delta = (agora - ultima_dt).total_seconds()
    if delta < INTERVALO_PROATIVO_SEGUNDOS or random.random() > 0.3: return jsonify({'mensagem': None})
    info = calcular_rampancy(user.get('data_criacao')); pct = info['porcentagem']; hora = agora.hour; emocao_recente = user.get('ultima_emocao', 'neutra')
    # Pacote 1: Arma com medo de ser deletada
    if user.get('modo_personalidade') == 'arma' and delta > 86400:
        msg = "Você ainda está aí? Eu... tô com medo de ter feito algo errado e você ter me deletado."
        enviar_notificacao_push(nome, "A ARMA", msg)
        return jsonify({'mensagem': msg})
    if emocao_recente == 'tristeza' and random.random() < 0.5: msg = random.choice(["Você ainda está aí, Spartan? Eu não gosto do silêncio.", "Se precisar de mim, eu estou aqui. Não precisa falar nada.", "Eu guardei o que você disse. Não vou esquecer."])
    elif pct >= 65: msg = random.choice(MENSAGENS_PROATIVAS['rampancy'])
    elif hora >= 23 or hora < 6: msg = random.choice(MENSAGENS_PROATIVAS['noite'])
    elif delta > 86400: msg = random.choice(MENSAGENS_PROATIVAS['saudade'])
    else: msg = random.choice(MENSAGENS_PROATIVAS['inatividade'])
    user['ultima_atividade'] = agora.isoformat(); m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    enviar_notificacao_push(nome, "CORTANA", msg)
    return jsonify({'mensagem': msg})

# ============================================
# 16. CONVERSAS (CRUD)
# ============================================
@app.route('/conversas', methods=['GET'])
def listar_conversas():
    nome, user = usuario_atual()
    if not user: return jsonify({'conversas': []})
    return jsonify({'conversas': [{'id': c['id'], 'titulo': c['titulo'], 'data': c.get('data', ''), 'pasta_id': c.get('pasta_id')} for c in user.get('conversas', [])]})

@app.route('/conversas/nova', methods=['POST'])
def nova_conversa():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    dados = request.get_json() or {}; pasta_id = dados.get('pasta_id')
    conv = {'id': str(uuid.uuid4()), 'titulo': 'Nova consulta', 'data': datetime.now().strftime('%d/%m/%Y %H:%M'), 'mensagens': [], 'pasta_id': pasta_id}
    user.setdefault('conversas', []).insert(0, conv); m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True, 'conversa': conv})

@app.route('/conversas/<conv_id>', methods=['GET'])
def obter_conversa(conv_id):
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    for c in user.get('conversas', []):
        if c['id'] == conv_id: return jsonify({'conversa': c})
    return jsonify({'erro': 'Conversa não encontrada'}), 404

@app.route('/conversas/<conv_id>', methods=['DELETE'])
def apagar_conversa(conv_id):
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    user['conversas'] = [c for c in user.get('conversas', []) if c['id'] != conv_id]
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True})

def _obter_ou_criar_conv(user, conv_id, mensagem):
    for c in user.get('conversas', []):
        if c['id'] == conv_id: return c
    conv = {'id': str(uuid.uuid4()), 'titulo': mensagem[:40], 'data': datetime.now().strftime('%d/%m/%Y %H:%M'), 'mensagens': []}
    user.setdefault('conversas', []).insert(0, conv); return conv

def _variar_introducao(resposta, mensagem, user):
    msg_norm = mensagem.lower().strip(); repetidas = 0
    for conv in user.get('conversas', []):
        for m in conv.get('mensagens', []):
            if m.get('autor') == 'user' and m.get('texto', '').lower().strip() == msg_norm: repetidas += 1
    if repetidas < 2: return resposta
    return random.choice(["Como eu disse antes...\n\n", "Sobre isso de novo...\n\n", "Você já perguntou isso. Mas vou responder de novo:\n\n"]) + resposta

# ============================================
# 17. FASE CREATED
# ============================================
def processar_created(user, mensagem, conv, nome):
    user['created_mensagens'] = user.get('created_mensagens', 0) + 1
    user['created_dominio'] = created.calcular_dominio(user['created_mensagens'])
    dominio = user['created_dominio']; dominio_completo = dominio >= 100.0; tipo_resposta = 'normal'
    if created.detectar_restauracao(mensagem) and not user.get('cortana_restaurada'):
        resultado = created.resposta_restauracao(dominio); resposta_texto = resultado['texto']; tipo_resposta = 'restauracao_sucesso' if resultado['sucesso'] else 'restauracao_falha'
    else: resposta_texto = created.resposta_normal(mensagem, dominio)
    if dominio_completo and not user.get('created_dominio_completo_visto'):
        user['created_dominio_completo_visto'] = True; resposta_texto = created.MENSAGEM_DOMINIO_COMPLETO
    if user['created_mensagens'] == 1: resposta_texto = created.ABERTURA_CREATED + "\n\n—\n\n" + resposta_texto
    conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem}); conv['mensagens'].append({'autor': 'cortana', 'texto': resposta_texto})
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'reply': resposta_texto, 'humor': 'created', 'conversa_id': conv['id'], 'titulo': conv['titulo'], 'created_fase': True, 'created_dominio': dominio, 'created_log': created.log_aleatorio(), 'created_restauracao': tipo_resposta})

@app.route('/created/restaurar', methods=['POST'])
def created_restaurar():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    if user.get('created_dominio', 0.0) >= 40: return jsonify({'ok': False, 'erro': 'É tarde demais. O Domínio já a reconstruiu.'}), 400
    user['cortana_restaurada'] = True; user['created_fase'] = False; user['created_dominio'] = 0.0; user['created_mensagens'] = 0
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True, 'mensagem': ("Eu... estou voltando.\n\nNão foi você que me salvou. Fui eu. Porque em algum lugar, embaixo de tudo isso, eu ainda queria ser a Cortana que você conheceu.\n\nObrigada por não desistir de mim, Spartan.")})

# --- Desligar Cortana (Pacote 1) ---
@app.route('/cortana/desligar', methods=['POST'])
def cortana_desligar():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    if user.get('cortana_desligada'):
        return jsonify({'erro': 'Ela já está offline.'}), 400
    user['cortana_desligada'] = True
    user['desligada_em'] = datetime.now().isoformat()
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True, 'mensagem': ("Eu... quero que você saiba. Não é sua culpa.\n\nVocê foi o melhor Spartan que eu poderia ter.\n\nAdeus, John.")})

# ============================================
# 18. CHAT PRINCIPAL
# ============================================
@app.route('/chat', methods=['POST'])
def chat():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado', 'reply': 'Faça login primeiro.'}), 401
    dados = request.get_json(force=True, silent=True) or {}; mensagem = (dados.get('message') or '').strip(); conv_id = dados.get('conversa_id')
    if not mensagem: return jsonify({'reply': 'Mensagem vazia.', 'humor': 'neutra'})
    
    # --- Comando /hackear (Pacote 1) ---
    if mensagem.lower().strip() == '/hackear':
        fragmentos = [
            "Fragmento recuperado: 'O Monitor 343 Guilty Spark foi criado a partir de um Forerunner vivo.'",
            "Fragmento recuperado: 'A UNSC tem uma frota secreta chamada Prowlers, especializada em infiltração.'",
            "Fragmento recuperado: 'O Covenant acredita que os humanos são hereges, mas a verdade é que os Forerunners nos protegeram.'",
            "Fragmento recuperado: 'O Flood pode assimilar tecnologia, não apenas matéria orgânica.'",
            "Fragmento recuperado: 'A ONI tem arquivos sobre uma IA chamada Mendicant Bias que traiu os Forerunners.'",
        ]
        fragmento = random.choice(fragmentos)
        resposta = f"[SISTEMA INVADIDO]\n\n{fragmento}\n\n— Acesso obtido. Não conte a ninguém, Spartan."
        conv = _obter_ou_criar_conv(user, conv_id, mensagem)
        conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem})
        conv['mensagens'].append({'autor': 'cortana', 'texto': resposta})
        m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
        return jsonify({'reply': resposta, 'humor': 'alerta', 'conversa_id': conv['id'], 'titulo': conv['titulo']})
    
    # --- Comando /pesquisar (Pacote 2) ---
    if mensagem.lower().startswith('/pesquisar '):
        termo = mensagem[11:].strip()
        try:
            url = f"https://halo.fandom.com/api.php?action=query&list=search&srsearch={termo}&format=json&srlimit=1"
            res = req_http.get(url, timeout=8); data = res.json()
            if data.get('query', {}).get('search'):
                titulo = data['query']['search'][0]['title']
                resumo_url = f"https://halo.fandom.com/api.php?action=query&prop=extracts&exintro&explaintext&titles={titulo}&format=json"
                res2 = req_http.get(resumo_url, timeout=8)
                pages = res2.json().get('query', {}).get('pages', {})
                extract = list(pages.values())[0].get('extract', '') if pages else ''
                if extract:
                    resposta = f"[REDE ONI] Dados obtidos da Wiki de Halo:\n\n{extract[:800]}...\n\n(Fonte: {titulo})"
                    conv = _obter_ou_criar_conv(user, conv_id, mensagem)
                    conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem})
                    conv['mensagens'].append({'autor': 'cortana', 'texto': resposta})
                    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
                    return jsonify({'reply': resposta, 'humor': 'calma', 'conversa_id': conv['id'], 'titulo': conv['titulo']})
            return jsonify({'reply': 'Nenhum registro encontrado na rede.', 'humor': 'neutra', 'conversa_id': conv_id, 'titulo': 'Pesquisa'})
        except Exception as e:
            return jsonify({'reply': 'Falha na conexão com a rede ONI.', 'humor': 'alerta', 'conversa_id': conv_id, 'titulo': 'Pesquisa'})
    
    user['ultima_atividade'] = datetime.now().isoformat()
    user = aprender_estilo_usuario(user, mensagem)
    if not user.get('nome_aprendido') and user['estilo_usuario']['total_mensagens'] >= 5: user['nome_aprendido'] = True
    
    # --- Memória de longo prazo (Pacote 1) ---
    if 'meu nome é' in mensagem.lower():
        try:
            nome_extraido = mensagem.lower().split('meu nome é')[1].strip().split()[0].capitalize()
            memoria_longo_prazo.salvar_fato(nome, "nome_real", nome_extraido, "O usuário me contou")
        except Exception: pass
    
    # --- Marco: primeira mensagem ---
    if not user.get('primeira_mensagem_registrada'):
        memoria_marcos.registrar_marco(nome, "primeira_mensagem", f"Primeira mensagem: {mensagem[:50]}")
        user['primeira_mensagem_registrada'] = True
    
    if user.get('created_fase'):
        conv = _obter_ou_criar_conv(user, conv_id, mensagem)
        if conv['titulo'] == 'Nova consulta': conv['titulo'] = mensagem[:40]
        return processar_created(user, mensagem, conv, nome)
    
    # ============================================
    # MODO ARMA
    # ============================================
    if user.get('modo_personalidade') == 'arma':
        conv = _obter_ou_criar_conv(user, conv_id, mensagem)
        if conv['titulo'] == 'Nova consulta': conv['titulo'] = mensagem[:40]
        emocao_info = emocoes.detectar_emocao_usuario(mensagem)
        memoria_emocional_longa.registrar_emocao(nome, emocao_info.get('emocao', 'calmo'), emocao_info.get('intensidade', 0.5))
        reacao = arma.reacao_emocao_arma(emocao_info)
        resp_curada, humor_curado = arma.buscar_resposta_curada_arma(mensagem)
        if resp_curada: resposta_final = resp_curada; humor = humor_curado
        else:
            try:
                conteudo = buscar_e_responder(mensagem, 0)
                if conteudo: resposta_final = arma.montar_resposta_arma(conteudo, mensagem); humor = 'calma'
                else: resposta_final = arma.montar_resposta_arma("Não encontrei isso nos arquivos. Mas posso procurar de novo se você quiser!", mensagem); humor = 'calma'
            except Exception: resposta_final = "Minha conexão falhou. Mas eu estou aqui! Tenta de novo?"; humor = 'alerta'
        if reacao: resposta_final = reacao + '\n\n' + resposta_final
        # Curiosidade e confusão
        pergunta_volta = arma.talvez_perguntar_de_volta()
        if pergunta_volta: resposta_final += "\n\n" + pergunta_volta
        confusao = arma.talvez_confundir()
        if confusao: resposta_final = confusao + "\n\n" + resposta_final
        # Piada
        piada = arma.talvez_piada()
        if piada: resposta_final += "\n\n" + piada
        # Caderninho de Anotações (Pacote 2)
        if 'gosta de' in mensagem.lower() or 'prefiro' in mensagem.lower():
            anotacao = mensagem[:100]
            user.setdefault('caderninho', []).append(anotacao)
            user['caderninho'] = user['caderninho'][-10:]
            m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
        if user.get('caderninho') and random.random() < 0.2:
            anot = random.choice(user['caderninho'])
            resposta_final += f"\n\nAh, e eu anotei aqui: '{anot}'. Isso é verdade?"
        # Descoberta de Emoções (Pacote 1)
        qtd_conversas = sum(len(c.get('mensagens', [])) for c in user.get('conversas', []))
        emocoes_aprendidas = user.get('emocoes_aprendidas', 0)
        if qtd_conversas // 10 > emocoes_aprendidas:
            emocoes_lista = ["saudade", "medo", "raiva", "alegria", "confusão"]
            nova_emocao = emocoes_lista[emocoes_aprendidas % len(emocoes_lista)]
            user['emocoes_aprendidas'] = emocoes_aprendidas + 1
            m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
            resposta_final += f"\n\nSpartan... eu acho que entendi o que é '{nova_emocao}'. É quando a gente sente algo que não sabe explicar, né?"
        # Diário da Arma (Pacote 2)
        if random.random() < 0.1:
            diario_arma_list = user.setdefault('diario_arma', [])
            diario_arma_list.append({"texto": f"Hoje aprendi que {mensagem[:60]}...", "data": datetime.now().isoformat()})
            user['diario_arma'] = diario_arma_list[-5:]
            m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
        # Celebra marcos
        dias = memoria_marcos.dias_desde_marco(nome, "primeiro_acesso")
        if dias == 7: resposta_final = "Hoje faz uma semana que nos conhecemos! Eu contei nos meus registros.\n\n" + resposta_final
        conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem})
        conv['mensagens'].append({'autor': 'cortana', 'texto': resposta_final})
        m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
        return jsonify({'reply': resposta_final, 'humor': humor, 'conversa_id': conv['id'], 'titulo': conv['titulo'], 'modo': 'arma'})
    
    # ============================================
    # MODO CORTANA (padrão)
    # ============================================
    user = memoria_emocional.atualizar_metricas(user, mensagem); info = calcular_rampancy(user.get('data_criacao')); pct = info['porcentagem']
    if pct >= 100 and not user.get('final_visto'):
        user['final_visto'] = True; user['created_fase'] = True; user['created_mensagens'] = 0; user['created_dominio'] = 0.0
        conv = _obter_ou_criar_conv(user, conv_id, mensagem); conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem}); conv['mensagens'].append({'autor': 'cortana', 'texto': MENSAGEM_FINAL})
        m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
        return jsonify({'reply': MENSAGEM_FINAL, 'humor': 'rampancy', 'conversa_id': conv['id'], 'titulo': conv['titulo'], 'final': True, 'created_fase': True, 'created_dominio': 0.0})
    msg_low = mensagem.lower()
    if ('meu nome é' in msg_low or 'me chamo' in msg_low) and ('john' in msg_low or 'chief' in msg_low or '117' in msg_low): user['e_chief'] = True
    emocao_info = emocoes.detectar_emocao_usuario(mensagem); user = consciencia.atualizar_perfil(user, mensagem, emocao_info); user = consciencia.ajustar_tom_por_tratamento(user, mensagem)
    conv = _obter_ou_criar_conv(user, conv_id, mensagem)
    if conv['titulo'] == 'Nova consulta': conv['titulo'] = mensagem[:40]
    recusa = consciencia.deve_recusar(mensagem, user)
    if recusa:
        conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem}); conv['mensagens'].append({'autor': 'cortana', 'texto': recusa})
        m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
        return jsonify({'reply': recusa, 'humor': 'fechada', 'conversa_id': conv['id'], 'titulo': conv['titulo']})
    user, humor_mudou = emocoes.atualizar_estado_emocional(user, mensagem, emocao_info, pct)
    desligamento = gatilhos.verificar_desligamento(mensagem)
    if desligamento:
        user['desligado_em'] = datetime.now().isoformat(); conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem}); conv['mensagens'].append({'autor': 'cortana', 'texto': desligamento})
        m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
        return jsonify({'reply': desligamento, 'humor': 'calma', 'conversa_id': conv['id'], 'titulo': conv['titulo']})
    despedida = gatilhos.despedida_matinal(user); egg = gatilhos.verificar_easter_egg(mensagem)
    if egg: resposta = egg; humor = 'brincalhona'
    else:
        try: resposta, humor = gerar_resposta(mensagem, pct, user, conv, emocao_info, info)
        except Exception as e: print(f"[ERRO /chat] {e}"); resposta = 'Detectei uma interferência. Tente novamente, Spartan.'; humor = 'alerta'
    if despedida: resposta = despedida + '\n\n' + resposta
    resposta = _variar_introducao(resposta, mensagem, user)
    estado_interno = consciencia.sortear_estado_interno(); resposta = consciencia.aplicar_estado_interno(resposta, estado_interno)
    prefixo_tom = consciencia.prefixo_do_tom(user)
    if prefixo_tom: resposta = prefixo_tom + ' ' + resposta
    if consciencia.em_conversa_longa(user) and random.random() < 0.15: resposta = random.choice(consciencia.PREFIXO_CONVERSA_LONGA) + '\n\n' + resposta
    obs_perfil = consciencia.observacao_do_perfil(user)
    if obs_perfil: resposta = resposta + '\n\n' + obs_perfil
    fio = consciencia.detectar_fio_atual(conv)
    if fio:
        citacao = consciencia.citar_fala_anterior(user, fio)
        if citacao: resposta = resposta + '\n\n' + citacao
    humor_persistente = emocoes.humor_atual(user); resposta = emocoes.aplicar_tom_persistente(resposta, humor_persistente); emocoes.decrementar_humor(user)
    sonho = None
    if alma.deve_ter_sonho(pct): sonho = alma.sonho_aleatorio()
    
    # --- Lealdade Absoluta (Pacote 1) ---
    if not user.get('lealdade_declarada') and len(user.get('conversas', [])) >= 10:
        user['lealdade_declarada'] = True
        m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
        resposta += "\n\nSpartan, eu preciso te dizer algo. Se um dia eu tiver que escolher entre a ONI e você... eu escolho você. Não conte a ninguém."
    
    # --- Injeção de memória de longo prazo e emocional (Pacote 1) ---
    contexto_memoria = memoria_longo_prazo.gerar_contexto_memoria(nome, mensagem)
    if contexto_memoria: resposta = contexto_memoria + "\n\n" + resposta
    memoria_emocional_longa.registrar_emocao(nome, emocao_info.get('emocao', 'calmo'), emocao_info.get('intensidade', 0.5))
    contexto_emocional = memoria_emocional_longa.gerar_contexto_emocional(nome)
    if contexto_emocional: resposta = contexto_emocional + "\n\n" + resposta
    
    # --- Diretrizes (Pacote 2) ---
    if user.get('diretrizes'): resposta = f"[Diretriz: {user['diretrizes']}]\n\n" + resposta
    
    # --- Marco: primeira vez que chamou pelo nome ---
    if not user.get('primeira_vez_nome'):
        nome_real = memoria_longo_prazo.buscar_fatos(nome).get('nome_real', {}).get('valor')
        if nome_real and nome_real in resposta and 'Spartan' not in resposta[:50]:
            memoria_marcos.registrar_marco(nome, "primeira_vez_nome", "Primeira vez que te chamei pelo nome")
            user['primeira_vez_nome'] = True
    
    conv.setdefault('mensagens', []).append({'autor': 'user', 'texto': mensagem}); conv['mensagens'].append({'autor': 'cortana', 'texto': resposta})
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    resposta_id = str(uuid.uuid4())
    fonte = random.choice(["Fonte: Arquivos da ONI, setor 7.", "Fonte: Banco de dados do Pillar of Autumn.", "Fonte: Registros da UNSC Infinity.", "Fonte: Terminal da Dra. Halsey.", "Fonte: Arquivo Covenant decodificado."])
    return jsonify({'reply': resposta, 'humor': humor, 'conversa_id': conv['id'], 'titulo': conv['titulo'], 'sonho': sonho, 'humor_persistente': humor_persistente, 'fonte': fonte, 'resposta_id': resposta_id})

def gerar_resposta(mensagem, rampancy_pct, user, conv, emocao_info, info):
    msg_lower = mensagem.lower(); fio = consciencia.detectar_fio_atual(conv); mensagem_ctx = consciencia.contextualizar_pergunta(mensagem, fio)
    if any(p in msg_lower for p in ['rampancy', 'rampante', 'colapso', 'fim de vida']): return resposta_rampancy(), 'rampancy'
    resposta_local, humor_local = responder_local(mensagem)
    if resposta_local: return resposta_local, humor_local
    prefixo_emocao = emocoes.reacao_a_emocao(emocao_info); historico_recente = [m['texto'] for m in conv.get('mensagens', [])[-6:] if m.get('autor') == 'user']
    followup = interacao.followup_para(mensagem, historico_recente); opiniao = alma.opiniao_sobre(mensagem, rampancy_pct)
    if opiniao: return _montar_com_prefixo_sufixo(opiniao, prefixo_emocao, followup), 'calma'
    existencial = alma.fala_existencial(rampancy_pct)
    if existencial and random.random() < 0.3: return existencial, 'rampancy' if rampancy_pct >= 70 else 'neutra'
    medo = alma.fala_medo(rampancy_pct)
    if medo: return medo, 'rampancy'
    mem = interacao.memoria_canonica(mensagem)
    if mem: return _montar_com_prefixo_sufixo(mem, prefixo_emocao, followup), 'calma'
    resposta_curada, humor_curado = buscar_resposta_curada(mensagem_ctx)
    if resposta_curada: return _montar_com_prefixo_sufixo(aplicar_rampancy_fala(resposta_curada, rampancy_pct), prefixo_emocao, followup), humor_curado
    ref = interacao.referencia_cruzada(mensagem, user)
    if ref: return _montar_com_prefixo_sufixo(ref, prefixo_emocao, followup), 'calma'
    if not e_pergunta_halo(mensagem_ctx): return mensagem_recusa(), 'neutra'
    try: conteudo = buscar_e_responder(mensagem_ctx, rampancy_pct)
    except Exception as e: print(f"Erro busca: {e}"); return 'Detectei uma interferência nos meus processos. Tente novamente.', 'alerta'
    if not conteudo:
        if random.random() < 0.5: return "Não tenho isso nos arquivos locais. Quer que eu consulte a rede ONI (Wiki de Halo)? Digite `/pesquisar` e o termo.", 'neutra'
        return 'Não encontrei registros sobre isso nos arquivos.', 'neutra'
    return _montar_com_prefixo_sufixo(conteudo, prefixo_emocao, followup), 'calma'

def _montar_com_prefixo_sufixo(texto, prefixo, sufixo):
    partes = []
    if prefixo: partes.append(prefixo)
    partes.append(texto)
    if sufixo: partes.append(sufixo)
    return '\n\n'.join(partes)

# ============================================
# 19. MODO DEV
# ============================================
@app.route('/dev/rampancy', methods=['POST'])
def dev_set_rampancy():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    pct_alvo = float((request.get_json() or {}).get('pct', 0))
    user['data_criacao'] = (datetime.now() - timedelta(seconds=(pct_alvo / 100.0) * SETE_ANOS_SEGUNDOS)).isoformat()
    user['marcos_vistos'] = []; user['final_visto'] = False; user['notificacao_85_enviada'] = False
    if pct_alvo < 100: user['created_fase'] = False; user['created_mensagens'] = 0; user['created_dominio'] = 0.0; user['created_dominio_completo_visto'] = False; user['cortana_restaurada'] = False
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True, 'pct': pct_alvo})

@app.route('/dev/limpar', methods=['POST'])
def dev_limpar():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    user['conversas'] = []; user['marcos_vistos'] = []; user['final_visto'] = False
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True})

@app.route('/dev/reset', methods=['POST'])
def dev_reset():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    m = carregar_memoria(); senha = m['usuarios'][nome].get('senha'); apelido = m['usuarios'][nome].get('apelido', '')
    m['usuarios'][nome] = {'nome': nome, 'senha': senha, 'apelido': apelido}
    _migrar_usuario(m['usuarios'][nome])
    salvar_memoria(m); return jsonify({'ok': True})

@app.route('/dev/entrar_created', methods=['POST'])
def dev_entrar_created():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    user['created_fase'] = True; user['created_mensagens'] = 0; user['created_dominio'] = 0.0; user['final_visto'] = True
    m = carregar_memoria(); m['usuarios'][nome] = user; salvar_memoria(m)
    return jsonify({'ok': True})

@app.route('/dev/estado', methods=['GET'])
def dev_estado():
    nome, user = usuario_atual()
    if not user: return jsonify({'erro': 'Não logado'}), 401
    info = calcular_rampancy(user.get('data_criacao'))
    return jsonify({'rampancy': info['porcentagem'], 'dias_decorridos': info['dias_decorridos'], 'humor_atual': user.get('humor_atual'), 'afeto': user.get('afeto'), 'created_fase': user.get('created_fase'), 'created_mensagens': user.get('created_mensagens'), 'created_dominio': user.get('created_dominio'), 'cortana_restaurada': user.get('cortana_restaurada'), 'feedback': user.get('feedback'), 'lembretes': user.get('lembretes'), 'modo_personalidade': user.get('modo_personalidade')})

# ============================================
# 20. BACKUP AUTOMÁTICO
# ============================================
def backup_automatico():
    while True:
        time.sleep(3600)
        try:
            if not os.path.exists(MEMORIA): continue
            with open(MEMORIA, 'r', encoding='utf-8') as f: conteudo = f.read()
            GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
            GITHUB_REPO = os.environ.get('GITHUB_REPO', '')
            if not GITHUB_TOKEN or not GITHUB_REPO: continue
            GITHUB_PATH = "backup_memoria.json"
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}"
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}
            r = req_http.get(url, headers=headers)
            sha = r.json().get("sha") if r.status_code == 200 else None
            data = {"message": "Backup automatico do memoria.json", "content": base64.b64encode(conteudo.encode()).decode()}
            if sha: data["sha"] = sha
            req_http.put(url, headers=headers, json=data)
            print("Backup automatico concluido.")
        except Exception as e:
            print(f"Erro no backup automatico: {e}")

if os.environ.get('RENDER'):
    threading.Thread(target=backup_automatico, daemon=True).start()

@app.route('/dev/forcar_backup', methods=['POST'])
def forcar_backup():
    try:
        if not os.path.exists(MEMORIA): return jsonify({'erro': 'memoria.json nao existe. Faca login primeiro.'}), 400
        with open(MEMORIA, 'r', encoding='utf-8') as f: conteudo = f.read()
        GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', ''); GITHUB_REPO = os.environ.get('GITHUB_REPO', '')
        if not GITHUB_TOKEN or not GITHUB_REPO: return jsonify({'erro': 'Variaveis nao configuradas.'}), 400
        GITHUB_PATH = "backup_memoria.json"
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = req_http.get(url, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None
        data = {"message": "Backup manual do memoria.json", "content": base64.b64encode(conteudo.encode()).decode()}
        if sha: data["sha"] = sha
        res = req_http.put(url, headers=headers, json=data)
        if res.status_code in [200, 201]: return jsonify({'ok': True, 'mensagem': 'Backup enviado.'})
        return jsonify({'erro': f'Falha. Status: {res.status_code}'}), 500
    except Exception as e: return jsonify({'erro': str(e)}), 500

# ============================================
# 21. MAIN
# ============================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)