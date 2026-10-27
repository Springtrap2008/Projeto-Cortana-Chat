# -*- coding: utf-8 -*-
# memoria_marcos.py - Primeiras vezes e eventos especiais
import os, json
from datetime import datetime

DATA_DIR = '/data' if os.path.exists('/data') else '.'
ARQUIVO = os.path.join(DATA_DIR, 'memoria_marcos.json')

def _carregar():
    if not os.path.exists(ARQUIVO): return {}
    try:
        with open(ARQUIVO, 'r', encoding='utf-8') as f: return json.load(f)
    except Exception: return {}

def _salvar(dados):
    try:
        os.makedirs(os.path.dirname(ARQUIVO), exist_ok=True)
        with open(ARQUIVO, 'w', encoding='utf-8') as f: json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as e: print(f"Erro ao salvar memoria_marcos: {e}")

def registrar_marco(nome_usuario, chave, descricao):
    dados = _carregar(); user_data = dados.setdefault(nome_usuario, {})
    if chave not in user_data:
        user_data[chave] = {"descricao": descricao, "data": datetime.now().isoformat()}
        _salvar(dados); return True
    return False

def listar_marcos(nome_usuario):
    return _carregar().get(nome_usuario, {})

def dias_desde_marco(nome_usuario, chave):
    marcos = listar_marcos(nome_usuario)
    if chave not in marcos: return None
    try:
        dt = datetime.fromisoformat(marcos[chave]["data"])
        return (datetime.now() - dt).days
    except Exception: return None