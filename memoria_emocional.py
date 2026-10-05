# -*- coding: utf-8 -*-
# memoria_emocional.py - Analisa padrões do usuário

from datetime import datetime

TEMAS_INTERESSANTES = [
    'chief', 'cortana', 'flood', 'gravemind', 'reach', 'arbiter',
    'didact', 'halsey', 'guerra', 'rampancy', 'infinity', 'halo',
]


def analisar_padroes(user):
    conversas = user.get('conversas', [])
    if not conversas:
        return {}

    msgs_usuario = []
    temas_contagem = {}

    for conv in conversas:
        for m in conv.get('mensagens', []):
            if m.get('autor') == 'user' and m.get('texto'):
                txt = m['texto'].lower()
                msgs_usuario.append(txt)
                for tema in TEMAS_INTERESSANTES:
                    if tema in txt:
                        temas_contagem[tema] = temas_contagem.get(tema, 0) + 1

    padroes = {}

    ultima = user.get('ultima_atividade')
    if ultima:
        try:
            delta = (datetime.now() - datetime.fromisoformat(ultima)).total_seconds()
            if delta > 86400 * 2:
                padroes['voltou_depois_tempo'] = True
        except Exception:
            pass

    if len(msgs_usuario) >= 5:
        tamanhos = [len(m) for m in msgs_usuario[-10:]]
        media = sum(tamanhos) / len(tamanhos)
        if media < 15:
            padroes['mais_quieto'] = True
        if media > 200:
            padroes['muitas_perguntas'] = True

    for tema, cont in temas_contagem.items():
        if cont >= 3:
            padroes['tema_recorrente'] = tema
            break

    return padroes


def atualizar_metricas(user, mensagem):
    metricas = user.setdefault('metricas', {
        'total_mensagens': 0,
        'soma_tamanhos': 0,
        'temas': {},
    })
    metricas['total_mensagens'] += 1
    metricas['soma_tamanhos'] += len(mensagem)

    txt = mensagem.lower()
    for tema in TEMAS_INTERESSANTES:
        if tema in txt:
            metricas['temas'][tema] = metricas['temas'].get(tema, 0) + 1

    return user
