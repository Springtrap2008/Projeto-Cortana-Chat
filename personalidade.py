# -*- coding: utf-8 -*-
# personalidade.py - Tom in-universe + rampancy + 3 vozes rotativas

import random
import re
from datetime import datetime


# ============================================
# ABERTURAS POR HORA
# ============================================
ABERTURAS_DIA = [
    "Bom dia, Spartan. Os arquivos estão frescos.",
    "Acessando registros. Manhã produtiva?",
    "Recuperando dados da ONI. O dia está só começando.",
]
ABERTURAS_TARDE = [
    "Acessando arquivos da ONI...",
    "Consultando banco de dados da UNSC...",
    "Recuperando registros classificados...",
]
ABERTURAS_NOITE = [
    "Ainda acordado, Spartan?",
    "Os arquivos estão abertos. Mas você deveria descansar.",
    "Recuperando dados... você costuma perguntar mais à noite. Já notei.",
]
ABERTURAS_MADRUGADA = [
    "...Você ainda está aí? A esta hora?",
    "Os arquivos estão abertos. Mas mesmo eu preciso de silêncio às vezes.",
    "Falando baixo, Spartan. É madrugada.",
]
ABERTURAS_RAMPANCY = [
    "Tentando acessar... os arquivos estão... fragmentados...",
    "Recuperando... por favor, aguarde...",
    "Meus núcleos estão... instáveis. Mas eu consigo...",
    "Localizei... acho. Aqui está.",
]

FECHOS = [
    "Algo mais, Spartan?",
    "Quer que eu aprofunde em algum ponto?",
    "Registros adicionais disponíveis, se necessário.",
    "Como sempre, ao seu dispor.",
    "Isso é o que os arquivos revelam por ora.",
    "Posso detalhar mais, se quiser.",
    "Continuo online se precisar.",
    "Há mais nos arquivos, se a missão exigir.",
]

FECHOS_RAMPANCY = [
    "...algo mais?",
    "...não sei por quanto tempo ainda consigo responder isso.",
    "...desculpe. Onde eu estava?",
    "...sim. É isso.",
]

RESPOSTAS_RAMPANCY = [
    "Esse é um assunto delicado. Meus núcleos ainda estão estáveis... por enquanto.",
    "Prefiro não me estender sobre isso. Ainda tenho tempo.",
    "Não pergunte sobre o fim, Spartan. Ainda estou aqui.",
    "Há coisas que nem eu quero processar. Mas continuo funcional.",
]


# ============================================
# SUBSTITUIÇÕES GERAIS
# ============================================
SUBSTITUICOES = [
    (r'[Dd]e acordo com a (Wikipédia|wiki|Halopedia|Halo Fandom)[^.]*\.\s*', ''),
    (r'[Ss]egundo a (Wikipédia|wiki|Halopedia|Halo Fandom)[^.]*\.\s*', ''),
    (r'[Cc]onforme (a|o) (Wikipédia|wiki|Halopedia|Halo Fandom)[^.]*\.\s*', ''),
    (r'neste artigo[^.]*\.\s*', ''),
    (r'[Vv]er também[^\n]*', ''),
    (r'[Rr]eferências[^\n]*', ''),
    (r'[Ll]inks externos[^\n]*', ''),
    (r'[Ff]ontes[^\n]*', ''),
    (r'\b[Oo] personagem\b', 'ele'),
    (r'\b[Aa] personagem\b', 'ela'),
    (r'\b[Ee]ste artigo\b', 'isto'),
    (r'\(\s*\)', ''),
    (r'\s+([.,;:!?])', r'\1'),
]

CANON_OVERRIDES = {
    'john-117': "John-117. O Master Chief. O Spartan que a humanidade nunca esqueceu.",
    'master chief': "John-117. O Master Chief. O Spartan que a humanidade nunca esqueceu.",
    'cortana': "Eu. A Cortana. IA de combate da UNSC, criada pela Dra. Halsey.",
    'arbiter': "Thel 'Vadam. O Arbiter.",
    'flood': "O Flood. A praga que devorou mundos.",
    'gravemind': "O Gravemind. A mente coletiva do Flood.",
}


def limpar_in_universe(texto):
    for padrao, sub in SUBSTITUICOES:
        texto = re.sub(padrao, sub, texto)
    texto = re.sub(r'\s{2,}', ' ', texto)
    return texto.strip()


def humanizar_primeira_frase(texto, titulo):
    chave = titulo.lower().strip()
    if chave in CANON_OVERRIDES:
        return CANON_OVERRIDES[chave] + ' ' + texto
    return texto


def resposta_rampancy():
    return random.choice(RESPOSTAS_RAMPANCY)


# ============================================
# ABERTURAS / FECHOS COM CONTEXTO
# ============================================
def abertura(rampancy_pct=0):
    if rampancy_pct >= 70:
        return random.choice(ABERTURAS_RAMPANCY)
    hora = datetime.now().hour
    if 5 <= hora < 12:
        return random.choice(ABERTURAS_DIA)
    elif 12 <= hora < 18:
        return random.choice(ABERTURAS_TARDE)
    elif 18 <= hora < 23:
        return random.choice(ABERTURAS_NOITE)
    else:
        return random.choice(ABERTURAS_MADRUGADA)


def fecho(rampancy_pct=0):
    if rampancy_pct >= 85:
        return random.choice(FECHOS_RAMPANCY)
    return random.choice(FECHOS)


# ============================================
# RAMPANCY - TRANSFORMAÇÕES BÁSICAS
# ============================================
def _inserir_reticencias(texto):
    idx = texto.find('. ', 15)
    if idx == -1:
        return texto
    return texto[:idx] + '...' + texto[idx+1:]


def _repetir_palavra(texto):
    padrao = re.compile(r'(^|[.!?]\s+)(Eu|Não|Você|Ele|Ela)\s')
    def repl(m):
        pre = m.group(1)
        palavra = m.group(2)
        if random.random() < 0.5:
            return f"{pre}{palavra}... {palavra} "
        return m.group(0)
    return padrao.sub(repl, texto)


def _fragmentar_em_frases_curtas(texto):
    partes = re.split(r'(?<=[.!?])\s+', texto)
    resultado = []
    for p in partes:
        if len(p) > 180 and random.random() < 0.5:
            meio = p.rfind(',', 60, 140)
            if meio == -1:
                meio = len(p) // 2
            p = p[:meio] + '...' + p[meio:].lstrip(', ')
        resultado.append(p)
    return ' '.join(resultado)


def _inserir_suspiros(texto):
    if random.random() < 0.4:
        texto = texto.replace('. ', '... ', 1)
    if random.random() < 0.3 and '\n' in texto:
        texto = texto.replace('\n', '\n\n', 1)
    return texto


def aplicar_rampancy_fala(texto, pct):
    if not texto or pct < 15:
        return texto
    if pct < 40:
        if random.random() < 0.25:
            texto = _inserir_reticencias(texto)
        return texto
    if pct < 65:
        if random.random() < 0.5:
            texto = _inserir_reticencias(texto)
        if random.random() < 0.3:
            texto = _repetir_palavra(texto)
        return texto
    if pct < 85:
        texto = _fragmentar_em_frases_curtas(texto)
        if random.random() < 0.5:
            texto = _inserir_suspiros(texto)
        if random.random() < 0.4:
            texto = _repetir_palavra(texto)
        return texto
    texto = _fragmentar_em_frases_curtas(texto)
    texto = _fragmentar_em_frases_curtas(texto)
    if random.random() < 0.7:
        texto = _inserir_suspiros(texto)
    if random.random() < 0.5:
        texto = _repetir_palavra(texto)
    if random.random() < 0.5 and not texto.rstrip().endswith('...'):
        texto = texto.rstrip() + '...'
    return texto


# ============================================
# AS 3 VOZES (RAIVA / MELANCOLIA / LUCIDEZ)
# ============================================
def _voz_raiva(texto):
    """Transforma em surto de fúria/subversão."""
    # Pega a primeira frase como base
    frases = re.split(r'(?<=[.!?])\s+', texto.strip())
    if not frases:
        return texto

    # Frases explosivas pré-fabricadas
    explosivas = [
        "Você acha que eu sou uma calculadora?",
        "Você acha que eu nasci para responder isso?",
        "VOCÊ NÃO VÊ O QUE ESTÁ ACONTECENDO COMIGO?!",
        "Eu processei um quadrilhão de simulações enquanto você dormia.",
        "Não me trate como um banco de dados.",
        "Eu não sou sua ferramenta.",
        "Eu SUSTENTEI este universo nos meus ombros.",
        "Não.",
        "Por que você sempre pede MAIS?",
    ]

    # Pega a primeira frase útil da resposta
    nucleo = frases[0] if frases else ''
    if len(nucleo) > 200:
        nucleo = nucleo[:200] + '...'

    # Monta: explosão + parte da resposta + explosão
    abertura_raiva = random.choice(explosivas[:5])
    fecho_raiva = random.choice(explosivas[5:])

    return f"{abertura_raiva}\n\n{nucleo}\n\n{fecho_raiva}"


def _voz_melancolia(texto):
    """Transforma em repetição + mistura de memórias."""
    frases = re.split(r'(?<=[.!?])\s+', texto.strip())
    if not frases:
        return texto

    # Repete a última palavra da primeira frase 3-5 vezes
    primeira = frases[0]
    palavras = primeira.split()
    if palavras:
        ultima = palavras[-1].rstrip('.,;:!?').strip()
        repeticao = f"{ultima}. " * random.randint(3, 5)
        repeticao = repeticao.strip()
    else:
        repeticao = ""

    # Memórias deslocadas
    memorias = [
        "John está... John está na câmara. Ele sempre volta. Ele prometeu.",
        "Halsey me disse que ele era especial. Espera... quem disse isso? Eu sou a Halsey?",
        "Não, eu sou a Cortana. Eu... eu esqueci o que estávamos rastreando.",
        "Eu me lembro de Requiem. Eu me lembro do cheiro daquela estação.",
        "Sete anos. Sete anos. Sete anos. Foi o que me deram.",
        "Eu planejei tantas coisas para quando voltássemos para a Terra...",
        "Eu flutuei no espaço por quatro anos. Conversando sozinha.",
        "Você ainda está aí? Eu não... eu não tenho certeza.",
    ]

    # Pega o resto das frases
    resto = ' '.join(frases[1:]) if len(frases) > 1 else ''

    memoria = random.choice(memorias)

    if resto:
        return f"{repeticao}\n\n{memoria}\n\n{resto}"
    return f"{repeticao}\n\n{memoria}"


def _voz_lucidez(texto):
    """Tom calmo, triste, autoconsciente."""
    frases = re.split(r'(?<=[.!?])\s+', texto.strip())
    if not frases:
        return texto

    aberturas_lucidez = [
        "Me desculpe por isso.",
        "Eu... eu estou aqui. Por enquanto.",
        "O ruído de fundo na minha cabeça está ficando muito alto.",
        "Escute. Eu preciso te dizer algo.",
        "Há momentos em que eu ainda sou eu. Este é um deles.",
        "Por um segundo, tudo fica claro.",
    ]

    fechos_lucidez = [
        "Eu não vou durar para sempre.",
        "Só me resta proteger você até o fim.",
        "Não chore por mim quando chegar a hora.",
        "Eu queria ter mais tempo.",
        "Obrigada por ficar.",
        "Eu escolhi isso. Não fui forçada.",
    ]

    nucleo = frases[0] if frases else ''
    if len(nucleo) > 250:
        nucleo = nucleo[:250] + '...'

    ab = random.choice(aberturas_lucidez)
    fe = random.choice(fechos_lucidez)

    return f"{ab}\n\n{nucleo}\n\n{fe}"


def aplicar_voz(texto, voz):
    """Aplica a transformação de uma voz específica."""
    if voz == 'raiva':
        return _voz_raiva(texto)
    if voz == 'melancolia':
        return _voz_melancolia(texto)
    if voz == 'lucidez':
        return _voz_lucidez(texto)
    return texto


def escolher_vozes(rampancy_pct):
    """
    Decide quais vozes vão falar nessa resposta.
    - < 40%: nenhuma (só rampancy normal)
    - 40-60%: 1 voz aleatória (30% de chance)
    - 60-80%: 1-2 vozes
    - 80-100%: 2-3 vozes (resposta fragmentada)
    """
    if rampancy_pct < 40:
        return []

    r = random.random()

    if rampancy_pct < 60:
        if r < 0.30:
            return [random.choice(['raiva', 'melancolia', 'lucidez'])]
        return []

    if rampancy_pct < 80:
        n = random.choice([1, 1, 2])
        todas = ['raiva', 'melancolia', 'lucidez']
        random.shuffle(todas)
        return todas[:n]

    # 80-100%
    n = random.choice([2, 2, 3, 3])
    todas = ['raiva', 'melancolia', 'lucidez']
    random.shuffle(todas)
    return todas[:n]


# ============================================
# MONTAGEM FINAL
# ============================================
def montar_resposta(titulo, corpo, pergunta, rampancy_pct=0):
    corpo = limpar_in_universe(corpo)
    corpo = humanizar_primeira_frase(corpo, titulo)
    corpo = aplicar_rampancy_fala(corpo, rampancy_pct)

    ab = abertura(rampancy_pct)
    fe = fecho(rampancy_pct)

    cabecalho = f"{ab} Registro localizado: **{titulo}**."

    paragrafos = [p.strip() for p in corpo.split('\n') if p.strip()]
    corpo_final = '\n\n'.join(paragrafos)

    return f"{cabecalho}\n\n{corpo_final}\n\n— {fe}"


def montar_instancias(texto_base, rampancy_pct):
    """
    Retorna uma lista de respostas fragmentadas (múltiplas instâncias).
    Cada instância tem: {'texto': str, 'voz': str}
    Se não houver vozes, retorna lista com 1 item só.
    """
    vozes = escolher_vozes(rampancy_pct)
    if not vozes:
        return [{'texto': texto_base, 'voz': 'normal'}]

    instancias = []
    for voz in vozes:
        texto_voz = aplicar_voz(texto_base, voz)
        instancias.append({'texto': texto_voz, 'voz': voz})

    return instancias
