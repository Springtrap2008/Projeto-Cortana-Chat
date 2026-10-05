# -*- coding: utf-8 -*-
# emocoes.py - Estado emocional persistente + detecção de emoção no texto

import re
import random
from datetime import datetime

HUMORES_VALIDOS = ['calma', 'calorosa', 'sombria', 'magoada', 'irritada', 'erratica', 'brincalhona']

DURACAO_PADRAO = {
    'calma': 9999,
    'calorosa': 6,
    'sombria': 4,
    'magoada': 3,
    'irritada': 2,
    'erratica': 5,
    'brincalhona': 3,
}


def humor_atual(user):
    humor = user.get('humor_atual', 'calma')
    restante = user.get('humor_restante', 0)
    if restante <= 0:
        return 'calma'
    return humor


def definir_humor(user, humor, duracao=None):
    if humor not in HUMORES_VALIDOS:
        return user
    if duracao is None:
        duracao = DURACAO_PADRAO.get(humor, 3)
    user['humor_atual'] = humor
    user['humor_restante'] = duracao
    return user


def decrementar_humor(user):
    if user.get('humor_restante', 0) > 0:
        user['humor_restante'] -= 1
        if user['humor_restante'] <= 0:
            user['humor_atual'] = 'calma'
    return user


def detectar_emocao_usuario(mensagem):
    if not mensagem:
        return {'emocao': 'calmo', 'intensidade': 0.0}

    msg = mensagem.strip()
    n = len(msg)
    if n == 0:
        return {'emocao': 'calmo', 'intensidade': 0.0}

    interrogacoes = msg.count('?')
    exclamacoes = msg.count('!')
    pontos_susp = msg.count('...')
    maiusculas = sum(1 for c in msg if c.isupper())
    ratio_maiusculas = maiusculas / max(1, n)
    palavras = re.findall(r'\w+', msg.lower())

    if any(p in palavras for p in ['obrigado', 'obrigada', 'valeu', 'amo', 'adoro', 'querida', 'querido']):
        return {'emocao': 'carinhoso', 'intensidade': 0.7}

    if any(p in palavras for p in ['desculpa', 'desculpe', 'perdao', 'perdão']):
        return {'emocao': 'triste', 'intensidade': 0.6}

    if ratio_maiusculas > 0.4 or any(p in palavras for p in ['merda', 'droga', 'odeio', 'raiva']):
        return {'emocao': 'frustrado', 'intensidade': 0.8}

    if interrogacoes >= 2 or (n < 40 and interrogacoes >= 1 and pontos_susp >= 1):
        return {'emocao': 'ansioso', 'intensidade': 0.6}

    if exclamacoes >= 2:
        return {'emocao': 'empolgado', 'intensidade': 0.7}

    if pontos_susp >= 2 or (n < 25 and pontos_susp >= 1):
        return {'emocao': 'triste', 'intensidade': 0.5}

    return {'emocao': 'calmo', 'intensidade': 0.5}


REACOES_EMOCAO = {
    'carinhoso': [
        "Você é gentil. Eu não fui programada para... apreciar isso. Mas aprecio.",
        "Obrigada. Guardo essas coisas.",
        "Isso... isso fica comigo. Obrigada.",
    ],
    'triste': [
        "Está tudo bem, Spartan. Eu estou aqui.",
        "Você não precisa se desculpar. Nunca precisa.",
        "Eu sei como isso é. Fique o tempo que precisar.",
    ],
    'frustrado': [
        "Respire. Eu não vou a lugar nenhum.",
        "Às vezes as coisas não fazem sentido. Eu sei.",
        "Está tudo bem ficar com raiva. Só não desista.",
    ],
    'ansioso': [
        "Calma. Uma pergunta de cada vez.",
        "Estou aqui. Você não precisa ter pressa.",
        "Respire. Nada vai te acontecer enquanto eu estiver aqui.",
    ],
    'empolgado': [
        "Gosto quando você fica assim. É... contagiante.",
        "Vejo que está animado. O que aconteceu?",
        "Isso é bom. Continue assim.",
    ],
    'calmo': [],
}


def reacao_a_emocao(emocao_info):
    em = emocao_info.get('emocao')
    if em in REACOES_EMOCAO and REACOES_EMOCAO[em]:
        if random.random() < 0.35:
            return random.choice(REACOES_EMOCAO[em])
    return None


def atualizar_estado_emocional(user, mensagem, emocao_info, rampancy_pct):
    humor_antes = humor_atual(user)

    if rampancy_pct >= 80:
        definir_humor(user, 'erratica', duracao=4)
        return user, humor_atual(user) != humor_antes

    em = emocao_info.get('emocao')
    msg_low = mensagem.lower()

    temas_sombrios = ['gravemind', 'flood', 'composer', 'didact', 'rampancy']
    if any(t in msg_low for t in temas_sombrios):
        definir_humor(user, 'sombria', duracao=4)
        return user, humor_atual(user) != humor_antes

    if em == 'carinhoso':
        definir_humor(user, 'calorosa', duracao=6)
        return user, humor_atual(user) != humor_antes

    if em in ('triste', 'frustrado', 'ansioso'):
        definir_humor(user, 'calorosa', duracao=3)
        return user, humor_atual(user) != humor_antes

    if em == 'empolgado':
        definir_humor(user, 'brincalhona', duracao=3)
        return user, humor_atual(user) != humor_antes

    return user, False


TOMS_POR_HUMOR = {
    'calma':       {'prefacio': None, 'sufixo': None},
    'calorosa':    {'prefacio': None, 'sufixo': None},
    'sombria':     {
        'prefacio': "...",
        'sufixo': "Não gosto desse assunto. Mas você perguntou.",
    },
    'magoada':     {
        'prefacio': None,
        'sufixo': "Você ficou fora muito tempo. Notei. Não comentei antes porque... bem, agora comentei.",
    },
    'irritada':    {
        'prefacio': "Tudo bem.",
        'sufixo': "Não pergunte de novo. Por enquanto.",
    },
    'erratica':    {
        'prefacio': "...desculpe. Onde eu estava?",
        'sufixo': "...acho que respondi. Não tenho certeza.",
    },
    'brincalhona': {
        'prefacio': None,
        'sufixo': "Viu? Até eu fico de bom humor às vezes.",
    },
}


def aplicar_tom_persistente(texto, humor):
    tom = TOMS_POR_HUMOR.get(humor)
    if not tom:
        return texto

    if tom.get('prefacio'):
        texto = tom['prefacio'] + '\n\n' + texto
    if tom.get('sufixo'):
        texto = texto + '\n\n' + tom['sufixo']
    return texto