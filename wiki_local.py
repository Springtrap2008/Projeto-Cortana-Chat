# -*- coding: utf-8 -*-
# wiki_local.py - Busca offline em wiki_local.json

import os
import json
import re
import unicodedata

ARQUIVO_LOCAL = 'wiki_local.json'

_cache = None


def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    return texto


def _carregar():
    global _cache
    if _cache is not None:
        return _cache
    if os.path.exists(ARQUIVO_LOCAL):
        try:
            with open(ARQUIVO_LOCAL, 'r', encoding='utf-8') as f:
                _cache = json.load(f)
                return _cache
        except Exception as e:
            print(f"[wiki_local] Erro ao carregar: {e}")
            _cache = {}
            return _cache
    _cache = {}
    return _cache


def tem_artigo():
    return len(_carregar()) > 0


def buscar_local(consulta):
    dados = _carregar()
    if not dados:
        return None

    q = normalizar(consulta)

    for p in ['quem e', 'quem foi', 'o que e', 'o que foi', 'me fale sobre',
              'fale sobre', 'sobre', 'explica', 'explique', 'como funciona',
              'qual a historia', 'qual o papel', 'a historia de', 'o que sao',
              'quem sao', 'onde fica', 'onde esta']:
        q = q.replace(p, '')
    q = q.strip()

    if not q:
        return None

    if q in dados:
        return dados[q]

    melhor = None
    melhor_pontos = 0

    for chave, info in dados.items():
        titulo_norm = normalizar(info.get('titulo', ''))
        if not titulo_norm:
            continue

        pontos = 0
        if q == titulo_norm:
            pontos = 100
        elif q in titulo_norm:
            pontos = 60 + len(q) / max(1, len(titulo_norm)) * 40
        elif titulo_norm in q:
            pontos = 50 + len(titulo_norm) / max(1, len(q)) * 40
        else:
            palavras_q = set(q.split())
            palavras_t = set(titulo_norm.split())
            comuns = palavras_q & palavras_t
            if comuns:
                pontos = 20 + len(comuns) * 8

        if pontos > melhor_pontos:
            melhor_pontos = pontos
            melhor = info

    if melhor and melhor_pontos >= 40:
        return melhor

    if melhor_pontos < 40:
        for chave, info in dados.items():
            if q in normalizar(info.get('conteudo', '')):
                return info

    return None


def listar_titulos():
    dados = _carregar()
    return [info.get('titulo', '?') for info in dados.values()]


def recarregar():
    global _cache
    _cache = None
    return _carregar()
