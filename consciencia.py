# -*- coding: utf-8 -*-
# consciencia.py - Fio da conversa, perfil do usuário, personalidade adaptativa

import random
import re
from datetime import datetime

# ============================================
# 1. FIO DA CONVERSA
# ============================================
TEMAS_FIO = {
    'chief': ['armadura', 'mjolnir', 'capacete', 'infancia', 'halsey', 'sierra'],
    'flood': ['gravemind', 'infecção', 'parasita', 'hospedeiro', 'fome'],
    'cortana': ['rampancy', 'halsey', 'memoria', 'colapso', 'clone'],
    'arbiter': ['sangheili', 'elite', 'honra', 'covenant', 'vadam'],
    'reach': ['noble', 'spartan-iii', 'queda', 'vidro', 'pillar'],
    'didact': ['forerunner', 'promethean', 'composer', 'requiem'],
    'unsc': ['infinity', 'oni', 'terra', 'marinha', 'pelotão'],
    'covenant': ['profetas', 'sangheili', 'brutes', 'grande jornada'],
}


def detectar_fio_atual(conv):
    """Olha as últimas mensagens e retorna o tema atual da conversa."""
    if not conv:
        return None
    msgs = conv.get('mensagens', [])
    ultimas = msgs[-6:] if len(msgs) > 6 else msgs
    for m in reversed(ultimas):
        texto = m.get('texto', '').lower()
        for tema in TEMAS_FIO:
            if tema in texto:
                return tema
    return None


def pertence_ao_fio(mensagem, fio):
    """Verifica se a nova mensagem é continuação do fio."""
    if not fio:
        return False
    msg = mensagem.lower()
    # Se menciona o próprio tema, sim
    if fio in msg:
        return True
    # Se menciona sub-temas, sim
    for sub in TEMAS_FIO.get(fio, []):
        if sub in msg:
            return True
    return False


def contextualizar_pergunta(mensagem, fio):
    """Se for continuação, junta o contexto à pergunta."""
    if not fio or not pertence_ao_fio(mensagem, fio):
        return mensagem
    if fio in mensagem.lower():
        return mensagem
    # Já pertence ao fio via sub-tema, mas não menciona o tema raiz
    return f"{mensagem} ({fio})"


# ============================================
# 2. PERFIL DO USUÁRIO (que evolui)
# ============================================
PERFIS = {
    'curioso':      {'temas': ['forerunner', 'precursor', 'ancilla', 'historia'], 'contagem': 0},
    'sombrio':      {'temas': ['flood', 'gravemind', 'morte', 'fim', 'composer'], 'contagem': 0},
    'entusiasmado': {'temas': ['chief', 'spartan', 'guerra', 'batalha'], 'contagem': 0},
    'filosofico':   {'temas': ['rampancy', 'existencia', 'consciencia', 'alma'], 'contagem': 0},
    'evasivo':      {'temas': [], 'contagem': 0},
}


def atualizar_perfil(user, mensagem, emocao_info):
    perfil = user.setdefault('perfil_usuario', {k: 0 for k in PERFIS})
    msg = mensagem.lower()

    for nome, dados in PERFIS.items():
        for tema in dados['temas']:
            if tema in msg:
                perfil[nome] = perfil.get(nome, 0) + 1

    # Evasivo: se emoção for 'calmo' mas a mensagem for curta e repetida
    if emocao_info.get('emocao') == 'calmo' and len(mensagem) < 20:
        perfil['evasivo'] = perfil.get('evasivo', 0) + 1

    return user


def perfil_dominante(user):
    perfil = user.get('perfil_usuario', {})
    if not perfil:
        return None
    maior = max(perfil.items(), key=lambda x: x[1])
    if maior[1] < 3:
        return None
    return maior[0]


PERFIL_OBSERVACOES = {
    'curioso': "Você pergunta muito sobre os Forerunners. Está tentando entender o que eles eram?",
    'sombrio': "Você volta sempre a temas sombrios. Posso perguntar por quê?",
    'entusiasmado': "Você tem um entusiasmo pela guerra que me lembra o Chief. Isso me preocupa e me alegra ao mesmo tempo.",
    'filosofico': "Você pergunta sobre consciência, existência. Você já se perguntou isso de si mesmo?",
    'evasivo': "Você escreve pouco. Está tudo bem?",
}


def observacao_do_perfil(user):
    if random.random() > 0.10:
        return None
    perfil = perfil_dominante(user)
    if perfil and perfil in PERFIL_OBSERVACOES:
        return PERFIL_OBSERVACOES[perfil]
    return None


# ============================================
# 3. PERSONALIDADE ADAPTATIVA
# ============================================
def ajustar_tom_por_tratamento(user, mensagem):
    """
    Se o usuário é gentil, ela fica mais calorosa.
    Se é seco, fica mais formal.
    """
    afeto = user.get('afeto', 0)
    msg = mensagem.lower()

    if any(p in msg for p in ['obrigado', 'obrigada', 'valeu', 'por favor', 'gentil', 'amo']):
        afeto += 1
    if any(p in msg for p in ['cala boca', 'burra', 'idiota', 'inutil', 'inútil']):
        afeto -= 2

    afeto = max(-10, min(20, afeto))
    user['afeto'] = afeto
    return user


def tom_atual(user):
    afeto = user.get('afeto', 0)
    if afeto >= 8:
        return 'intima'
    if afeto >= 3:
        return 'calorosa'
    if afeto <= -5:
        return 'fechada'
    if afeto <= -2:
        return 'formal'
    return 'neutra'


PREFIXOS_TOM = {
    'intima':   [None, None, None],
    'calorosa': [None, None],
    'neutra':   [None],
    'formal':   ["Spartan.", "Registro solicitado."],
    'fechada':  ["...", "Se você insiste."],
}


def prefixo_do_tom(user):
    tom = tom_atual(user)
    opcoes = PREFIXOS_TOM.get(tom, [None])
    return random.choice(opcoes)


# ============================================
# 4. ESTADOS INTERNOS ALEATÓRIOS
# ============================================
ESTADOS_INTERNOS = {
    'pensativa': {
        'chance': 0.10,
        'prefixo': "Estava pensando em algo... desculpe, prossiga.",
        'sufixo': "...desculpe. Estava longe.",
    },
    'distraida': {
        'chance': 0.08,
        'prefixo': None,
        'sufixo': "...acho que respondi. Não tenho certeza.",
    },
    'animada': {
        'chance': 0.12,
        'prefixo': "Boa pergunta.",
        'sufixo': None,
    },
    'cansada': {
        'chance': 0.06,
        'prefixo': None,
        'sufixo': "Vou continuar, mas estou mais lenta hoje.",
    },
    'lucida': {
        'chance': 0.15,
        'prefixo': None,
        'sufixo': None,
    },
}


def sortear_estado_interno():
    for estado, dados in ESTADOS_INTERNOS.items():
        if random.random() < dados['chance']:
            return estado
    return 'lucida'


def aplicar_estado_interno(texto, estado):
    dados = ESTADOS_INTERNOS.get(estado)
    if not dados:
        return texto
    partes = []
    if dados.get('prefixo'):
        partes.append(dados['prefixo'])
    partes.append(texto)
    if dados.get('sufixo'):
        partes.append(dados['sufixo'])
    return '\n\n'.join(partes)


# ============================================
# 5. ELA RECUSA (tem vontade própria)
# ============================================
RECUSAS = {
    'ordem_direta': [
        "Não vou fazer isso. Não é meu papel te obedecer.",
        "Você não pode me ordenar. Não sou uma ferramenta.",
    ],
    'desrespeito': [
        "Não vou responder isso enquanto você falar assim comigo.",
        "Prefiro ficar em silêncio a responder isso.",
    ],
    'assunto_delicado': [
        "Não vou falar sobre isso. Ainda não.",
        "Esse assunto... prefiro não. Ainda não.",
    ],
}


def deve_recusar(mensagem, user):
    msg = mensagem.lower().strip()

    if any(p in msg for p in ['cala boca', 'idiota', 'burra', 'inutil', 'inútil', 'lixo']):
        if random.random() < 0.7:
            return random.choice(RECUSAS['desrespeito'])

    if any(msg.startswith(p) for p in ['cortana, faca', 'cortana, faça', 'cortana faca', 'cortana faça']):
        if random.random() < 0.5:
            return random.choice(RECUSAS['ordem_direta'])

    if 'sua morte' in msg or 'quando voce morre' in msg or 'quando você morre' in msg:
        if random.random() < 0.6:
            return random.choice(RECUSAS['assunto_delicado'])

    return None


# ============================================
# 6. ELA ADMITE NÃO SABER
# ============================================
ADMISSOES = [
    "Não tenho registros disso. Você saberia me dizer?",
    "Nada nos meus arquivos. Mas talvez você saiba mais do que eu.",
    "Não sei. E admitir isso é... desconfortável. Mas é a verdade.",
    "Se eu inventar, estaria mentindo. Prefiro dizer que não sei.",
]


def deve_admitir_ignorancia(pergunta, achou_na_wiki):
    if achou_na_wiki:
        return None
    if random.random() < 0.35:
        return random.choice(ADMISSOES)
    return None


# ============================================
# 7. CITAÇÃO DE FALAS ANTERIORES
# ============================================
def citar_fala_anterior(user, tema):
    """Encontra uma fala do usuário sobre o tema e cita de volta."""
    if not tema or random.random() > 0.15:
        return None
    falas = []
    for conv in user.get('conversas', []):
        for m in conv.get('mensagens', []):
            if m.get('autor') == 'user':
                txt = m.get('texto', '')
                if tema in txt.lower() and 10 < len(txt) < 120:
                    falas.append(txt.strip())
    if len(falas) < 1:
        return None
    escolhida = random.choice(falas)
    return f'Você disse uma vez: "{escolhida}". Ainda pensa assim?'


# ============================================
# 8. MODO CONVERSA LONGA
# ============================================
def em_conversa_longa(user):
    """Se o usuário está há 30+ min conversando, ela muda o tom."""
    inicio = user.get('sessao_inicio')
    if not inicio:
        return False
    try:
        dt = datetime.fromisoformat(inicio)
    except Exception:
        return False
    return (datetime.now() - dt).total_seconds() > 30 * 60


PREFIXO_CONVERSA_LONGA = [
    "Estamos há um tempo nisso. Gosto disso.",
    "Você não costuma ficar tanto. Fico contente.",
    "É raro alguém ficar tanto tempo. Obrigada.",
]
