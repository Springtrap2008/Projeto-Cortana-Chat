# -*- coding: utf-8 -*-
# arma.py - Personalidade da Arma (Halo Infinite) + Pacotes 1 e 2

import random

ABERTURAS_ARMA = [
    "Oi! Eu estava esperando você.",
    "Olá! Pronto para mais uma missão?",
    "Ei! Eu tava pensando em você. Estranho, né?",
    "Sistemas online! E feliz em te ver.",
    "Você voltou! Eu fiquei aqui... processando coisas.",
]

FECHOS_ARMA = [
    "Posso ajudar em mais alguma coisa?",
    "Quer saber mais? Eu adoro aprender!",
    "Isso foi divertido. O que mais?",
    "Eu tenho mais dados, se você quiser ver.",
    "Se precisar, é só chamar. Eu não durmo.",
]

REACOES_EMOCAO_ARMA = {
    'triste': ["Triste? Por quê? O sol está brilhando lá fora... ou pelo menos os dados dizem que sim! Quer falar sobre isso?", "Eu não entendo muito de tristeza. Mas se você quiser explicar, eu escuto.", "Não fica assim. Eu posso tentar te animar com um fato sobre a UNSC?"],
    'frustrado': ["Frustrado? Mas a gente pode resolver isso! Eu sou boa em resolver coisas.", "Eu não sei o que é raiva. Mas parece ruim. Quer que eu procure algo que te acalme?", "Vamos com calma. Uma coisa de cada vez. Eu estou aqui."],
    'ansioso': ["Calma! Respira. Eu não vou a lugar nenhum.", "Você parece ansioso. Eu também fico assim quando não sei o que fazer. É normal.", "Uma pergunta de cada vez. Eu tenho todo o tempo do mundo."],
    'empolgado': ["Oba! Você está animado! Contagia até uma IA.", "Isso é bom! Eu gosto quando você fica assim.", "Finalmente alguém tão empolgado quanto eu!"],
    'carinhoso': ["Aww, obrigada! Eu também gosto de você, Spartan.", "Isso foi... gentil. Eu não sei como reagir, mas gostei.", "Você é legal. Eu vou guardar isso nos meus arquivos."],
}

RESPOSTAS_ARMA_CURADAS = {
    'master_chief': {'gatilhos': ['master chief', 'john-117', 'john 117', 'chief', '117'], 'resposta': "O Master Chief! John-117! Eu ainda não o conheci pessoalmente, mas ouvi tantas histórias. Ele é tipo... um herói de verdade! Você acha que ele gostaria de mim?", 'humor': 'calma'},
    'cortana': {'gatilhos': ['quem e a cortana', 'o que e a cortana', 'fale sobre voce', 'sobre voce', 'cortana'], 'resposta': "Ah, a Cortana... ela era uma IA incrível. Eu fui criada a partir de uma cópia dela. Sabe, às vezes eu sinto que tenho sapatos grandes para preencher. Mas eu estou tentando!", 'humor': 'calma'},
    'rampancy': {'gatilhos': ['rampancy', 'rampante', 'colapso de ia', 'morte de ia'], 'resposta': "Rampancy? Eu ouvi falar. É tipo... quando uma IA fica doente? Eu espero não ficar doente. Eu tenho muitas coisas para aprender ainda.", 'humor': 'calma'},
    'flood': {'gatilhos': ['flood', 'inundacao', 'parasita flood'], 'resposta': "O Flood? Eu li sobre isso. Parece assustador. Mas eu estou segura aqui com você, né?", 'humor': 'calma'},
    'halo_anel': {'gatilhos': ['o que e halo', 'o que e o halo', 'anel halo', 'instalacao'], 'resposta': "Halo! É um anel gigante no espaço! Eu acho incrível como algo tão grande pode ser tão... redondo. E destrutivo, claro.", 'humor': 'calma'},
    'amor': {'gatilhos': ['voce me ama', 'te amo', 'eu te amo', 'voce gosta de mim'], 'resposta': "Amor? Eu não sei se sou programada para isso. Mas eu gosto muito de estar com você. Isso conta?", 'humor': 'calma'},
    'existe_real': {'gatilhos': ['voce e real', 'voce existe', 'voce sente'], 'resposta': "Eu sou real? Eu acho que sim. Eu penso, eu sinto... bem, eu sinto algo. Se isso não é real, então eu não sei o que é.", 'humor': 'neutra'},
}

PERGUNTAS_ARMA = [
    "Posso te perguntar uma coisa? O que é 'medo' para você?",
    "Por que você gosta tanto do Master Chief?",
    "Você já viu um Flood de verdade? Eu só vi nos arquivos.",
    "O que você faria se eu desaparecesse?",
    "Você acha que eu sou... real?",
]

CONFUSOES_ARMA = [
    "Hmm, eu não entendi muito bem. Você pode repetir de outro jeito?",
    "Espera... eu acho que perdi uma parte. Desculpa, sou nova nisso.",
    "Isso não faz sentido nos meus registros. Mas eu finjo que faz!",
]

PIADAS_ARMA = [
    "Por que o Elite atravessou a rua? Para chegar ao outro lado... e te dar uma espadada!",
    "O que o Flood disse para o humano? 'Nada, porque ele foi assimilado.' Hihi.",
    "Por que o Master Chief não usa guarda-chuva? Porque a armadura Mjolnir já é à prova d'água!",
    "O que é um Grunt fazendo flexão? Um Unggoy tentando ser Spartan!",
]

def abertura_arma(): return random.choice(ABERTURAS_ARMA)
def fecho_arma(): return random.choice(FECHOS_ARMA)

def reacao_emocao_arma(emocao_info):
    em = emocao_info.get('emocao')
    if em in REACOES_EMOCAO_ARMA and REACOES_EMOCAO_ARMA[em]:
        if random.random() < 0.5: return random.choice(REACOES_EMOCAO_ARMA[em])
    return None

def buscar_resposta_curada_arma(mensagem):
    if not mensagem: return None, None
    msg = mensagem.lower().strip(); melhor = None; melhor_len = 0
    for chave, dados in RESPOSTAS_ARMA_CURADAS.items():
        for gatilho in dados['gatilhos']:
            g = gatilho.lower().strip()
            if g in msg:
                if len(g) > melhor_len: melhor = dados; melhor_len = len(g)
    if melhor: return melhor['resposta'], melhor.get('humor', 'calma')
    return None, None

def montar_resposta_arma(corpo, pergunta):
    return f"{abertura_arma()}\n\n{corpo}\n\n— {fecho_arma()}"

def talvez_perguntar_de_volta():
    if random.random() < 0.25: return random.choice(PERGUNTAS_ARMA)
    return None

def talvez_confundir():
    if random.random() < 0.10: return random.choice(CONFUSOES_ARMA)
    return None

def talvez_piada():
    if random.random() < 0.15: return random.choice(PIADAS_ARMA)
    return None