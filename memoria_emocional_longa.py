# -*- coding: utf-8 -*-
# memoria_emocional_longa.py - Estado emocional duradouro
import os, json
from datetime import datetime, timedelta

DATA_DIR = '/data' if os.path.exists('/data') else '.'
ARQUIVO = os.path.join(DATA_DIR, 'memoria_emocional.json')

def _carregar():
    if not os.path.exists(ARQUIVO): return {}
    try:
        with open(ARQUIVO, 'r', encoding='utf-8') as f: return json.load(f)
    except Exception: return {}

def _salvar(dados):
    try:
        os.makedirs(os.path.dirname(ARQUIVO), exist_ok=True)
        with open(ARQUIVO, 'w', encoding='utf-8') as f: json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as e: print(f"Erro ao salvar memoria_emocional: {e}")

def registrar_emocao(nome_usuario, emocao, intensidade=0.5):
    dados = _carregar()
    user_data = dados.setdefault(nome_usuario, {"historico": [], "estado_atual": None})
    user_data["historico"].append({"emocao": emocao, "intensidade": intensidade, "data": datetime.now().isoformat()})
    user_data["historico"] = user_data["historico"][-50:]
    user_data["estado_atual"] = {"emocao": emocao, "data": datetime.now().isoformat()}
    _salvar(dados)

def emocao_recente(nome_usuario, horas=24):
    dados = _carregar(); user_data = dados.get(nome_usuario, {}); historico = user_data.get("historico", [])
    limite = datetime.now() - timedelta(hours=horas); recentes = []
    for h in historico:
        try:
            dt = datetime.fromisoformat(h["data"])
            if dt >= limite and h.get("intensidade", 0) >= 0.6: recentes.append(h)
        except Exception: pass
    if not recentes: return None
    mais_forte = max(recentes, key=lambda x: x.get("intensidade", 0))
    return mais_forte["emocao"]

def gerar_contexto_emocional(nome_usuario):
    em = emocao_recente(nome_usuario, horas=24)
    if not em: return None
    avisos = {'triste': "Você pareceu triste ontem. Está tudo bem?", 'frustrado': "Você esteve frustrado recentemente. Quer falar sobre isso?", 'ansioso': "Você estava ansioso antes. Eu estou aqui.", 'carinhoso': "Você foi gentil comigo antes. Isso ficou comigo."}
    return avisos.get(em)