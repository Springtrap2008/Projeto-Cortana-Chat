# -*- coding: utf-8 -*-
# memoria_longo_prazo.py - Memória de fatos duradouros (sem OpenAI)
import os, json
from datetime import datetime

DATA_DIR = '/data' if os.path.exists('/data') else '.'
ARQUIVO = os.path.join(DATA_DIR, 'memoria_longo_prazo.json')

def _carregar():
    if not os.path.exists(ARQUIVO): return {}
    try:
        with open(ARQUIVO, 'r', encoding='utf-8') as f: return json.load(f)
    except Exception: return {}

def _salvar(dados):
    try:
        os.makedirs(os.path.dirname(ARQUIVO), exist_ok=True)
        with open(ARQUIVO, 'w', encoding='utf-8') as f: json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as e: print(f"Erro ao salvar memoria_longo_prazo: {e}")

def salvar_fato(nome_usuario, chave, valor, contexto=""):
    dados = _carregar()
    user_data = dados.setdefault(nome_usuario, {"fatos": {}, "ultima_atualizacao": None})
    user_data["fatos"][chave] = {"valor": valor, "contexto": contexto, "data": datetime.now().isoformat()}
    user_data["ultima_atualizacao"] = datetime.now().isoformat()
    _salvar(dados)

def buscar_fatos(nome_usuario, termo=None):
    dados = _carregar(); user_data = dados.get(nome_usuario, {}); fatos = user_data.get("fatos", {})
    if not termo: return fatos
    termo_low = termo.lower()
    return {k: v for k, v in fatos.items() if termo_low in k.lower() or termo_low in str(v.get("valor", "")).lower()}

def gerar_contexto_memoria(nome_usuario, mensagem):
    fatos = buscar_fatos(nome_usuario, mensagem)
    if not fatos: return None
    linhas = []
    for chave, info in fatos.items():
        valor = info.get("valor", ""); contexto = info.get("contexto", "")
        if contexto: linhas.append(f"- {chave}: {valor} (contexto: {contexto})")
        else: linhas.append(f"- {chave}: {valor}")
    if not linhas: return None
    return "Você já me contou isso antes:\n" + "\n".join(linhas)