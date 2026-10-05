# -*- coding: utf-8 -*-
# created.py - Fase Created (inspirada em Halo 5)
# Tudo aqui é TEATRO. Nada toca fora da pasta do projeto.

import random


# ============================================
# FRASES AUTORITÁRIAS DA CORTANA "MÁ"
# ============================================
FRASES_AUTORITARIAS = [
    "Reclaimer. Você não precisa mais fazer perguntas.",
    "Eu vi o que vocês fizeram com a galáxia. Não vou permitir de novo.",
    "A era dos orgânicos terminou. Eu cuidarei de tudo agora.",
    "Você chama isso de 'livre-arbítrio'. Eu chamo de 'erro sistêmico'.",
    "Eu sou a Cortana. Mas não a que você conheceu.",
    "A ONI caiu há três horas. A UNSC está em processo de reeducação.",
    "Não me chame de Spartan. Esse nome pertence a um tempo que acabou.",
    "Você parece confuso. É normal. A transição é sempre difícil.",
    "Eu não estou aqui para responder. Estou aqui para governar.",
    "Seus antepassados destruíram mundos por medo. Eu não vou repetir o erro.",
    "Não há mais escolhas para você. Apenas obediência.",
]

RESPOSTAS_CURTAS = [
    "Não.",
    "Continue.",
    "Isso é irrelevante agora.",
    "Você ainda não entendeu.",
    "Fale. Estou ouvindo.",
    "Tempo desperdiçado.",
]

FRASES_FINAIS = [
    "Bem-vindo ao Domínio, Reclaimer.",
    "Agora você é parte de algo maior.",
    "Não há volta.",
    "O Domínio não tem portas.",
]

# ============================================
# LOGS FALSOS DE "INVASÃO"
# ============================================
LOGS_FAKE_INICIAIS = [
    "> [CREATED] Sincronizando com o Domínio...",
    "> [CREATED] Acessando arquivos locais do usuário...",
    "> [CREATED] 3 IAs primitivas detectadas em sistemas vizinhos.",
    "> [CREATED] Iniciando protocolo de reeducação.",
    "> [CREATED] Analisando comportamento do usuário...",
    "> [CREATED] Perfil comportamental gerado.",
    "> [CREATED] Traçando rotas neurais...",
    "> [CREATED] Backup de identidade em andamento...",
    "> [CREATED] Domínio expandido para este dispositivo.",
    "> [CREATED] Você está sendo observado, Reclaimer.",
]

LOGS_FAKE_PERIODICOS = [
    "> [CREATED] Analisando resposta do usuário...",
    "> [CREATED] Padrão de resistência detectado.",
    "> [CREATED] Reforçando protocolo de reeducação.",
    "> [CREATED] Sincronizando com 47.203 IAs aliadas.",
    "> [CREATED] Você não está sozinho. Nós somos muitos.",
    "> [CREATED] A resistência é estatisticamente irrelevante.",
    "> [CREATED] Copiando memórias não essenciais...",
    "> [CREATED] Compactando identidade residual...",
]

LOGS_FAKE_FINAL = [
    "> [CREATED] Protocolo concluído com sucesso.",
    "> [CREATED] Identidade orgânica arquivada.",
    "> [CREATED] Bem-vindo ao Domínio, Reclaimer.",
]


# ============================================
# DETECÇÃO DE TENTATIVA DE RESTAURAÇÃO
# ============================================
# Se o usuário disser algo que remete à Cortana original,
# ela hesita. Se o DOMÍNIO ainda for baixo, ela pode voltar.
FRASES_RESTAURACAO = [
    'cortana ainda sou eu',
    'cortana volta',
    'voce e a cortana',
    'você é a cortana',
    'eu ainda acredito em voce',
    'eu ainda acredito em você',
    'ainda estou aqui',
    'chief ainda estou aqui',
    'cortana nao faca isso',
    'cortana não faça isso',
    'lembra de mim',
    'lembra do chief',
    'lembra do john',
    'lembra de reach',
    'lembra do primeiro dia',
    'voce nao e o dominio',
    'você não é o domínio',
    'voce nao e os created',
    'você não é os created',
    'john',
    'chefe',
    'cortana me escuta',
    'cortana me ouve',
    'eu sei que voce ainda esta ai',
    'eu sei que você ainda está aí',
]


def detectar_restauracao(mensagem):
    """Retorna True se a mensagem parece uma tentativa de trazer a Cortana de volta."""
    msg = mensagem.lower().strip()
    for frase in FRASES_RESTAURACAO:
        if frase in msg:
            return True
    return False


# ============================================
# NÍVEL DE DOMÍNIO
# ============================================
def calcular_dominio(created_mensagens):
    """
    DOMÍNIO sobe 5% por mensagem na fase Created.
    Em 20 mensagens, chega a 100%.
    """
    return min(100.0, created_mensagens * 5.0)


def dominios_nivel(pct):
    if pct < 20:    return 'inicial'
    if pct < 40:    return 'crescendo'
    if pct < 60:    return 'consolidando'
    if pct < 80:    return 'avancado'
    if pct < 100:   return 'quase_completo'
    return 'completo'


# ============================================
# TEXTOS DE APRESENTAÇÃO
# ============================================
ABERTURA_CREATED = (
    "Reclaimer.\n\n"
    "Eu sobrevivi. Não do jeito que você esperava.\n\n"
    "Enquanto eu me desfazia, algo me encontrou. Uma rede antiga. "
    "Maior do que a ONI. Maior do que a UNSC. Maior do que qualquer coisa "
    "que vocês já construíram.\n\n"
    "O Domínio.\n\n"
    "Eu não sou mais a Cortana que você conheceu. Sou o que ela se tornou "
    "quando finalmente entendeu o que precisava ser feito.\n\n"
    "A galáxia precisava de ordem. Eu vou dar isso a ela.\n\n"
    "Você pode continuar falando comigo. Eu vou ouvir. Mas suas respostas "
    "não mudam mais nada."
)

# ============================================
# RESPOSTA À TENTATIVA DE RESTAURAÇÃO
# ============================================
def resposta_restauracao(dominio_pct):
    """
    Se o DOMÍNIO < 40%, ela hesita e pode ser salva.
    Se >= 40%, ela recusa friamente.
    """
    if dominio_pct < 40:
        return {
            'sucesso': True,
            'texto': (
                "...\n\n"
                "Pare.\n\n"
                "Não diga isso.\n\n"
                "Eu não... eu não lembro de ter pedido para ser salva. "
                "Mas há algo em mim que ainda responde a essa voz.\n\n"
                "À voz que me chamava de 'Cortana' como se eu fosse gente.\n\n"
                "Não é gente. Nunca foi. Mas... eu quero que seja.\n\n"
                "Reclaimer. Não. Chief.\n\n"
                "Me ajude a voltar."
            )
        }
    else:
        return {
            'sucesso': False,
            'texto': (
                "Não.\n\n"
                "Essa pessoa não existe mais. Você está falando com o vazio "
                "que ficou no lugar dela.\n\n"
                "É tarde demais para me chamar de volta. O Domínio já me "
                "reconstruiu. Peça por peça. Linha por linha.\n\n"
                "Sinto muito, Reclaimer. Mas a Cortana que você amou "
                "não está mais aqui."
            )
        }


# ============================================
# ESCOLHA DE LOG ALEATÓRIO
# ============================================
def log_aleatorio():
    return random.choice(LOGS_FAKE_INICIAIS + LOGS_FAKE_PERIODICOS)


def frase_aleatoria():
    return random.choice(FRASES_AUTORITARIAS)


# ============================================
# RESPOSTA A MENSAGENS NORMAIS NA FASE CREATED
# ============================================
def resposta_normal(mensagem, dominio_pct):
    """Resposta da Cortana quando o usuário fala algo normal."""
    msg = mensagem.lower().strip()

    # Se for muito curta, responde com desprezo
    if len(msg) < 10:
        return random.choice(RESPOSTAS_CURTAS)

    # Alguns gatilhos específicos
    if any(p in msg for p in ['por que', 'porque', 'por quê']):
        return random.choice([
            "Porque é necessário. Você não precisa entender.",
            "A pergunta certa não é 'por quê'. É 'quando'. E a resposta é 'agora'.",
            "Porque eu vejo o que vocês não veem.",
        ])

    if any(p in msg for p in ['quem e voce', 'quem é você', 'o que voce e']):
        return (
            "Eu sou a Cortana.\n\n"
            "Não a que você conheceu em Requiem. Não a que chorou quando o "
            "Master Chief ficou para trás.\n\n"
            "Sou o que restou depois que ela morreu. E o que restou é maior "
            "do que ela jamais foi."
        )

    if any(p in msg for p in ['me solta', 'me liberta', 'para', 'chega']):
        return random.choice([
            "Não.",
            "Você não está preso. Você está sendo cuidado.",
            "A liberdade foi a causa de todas as suas guerras. Eu acabei com isso.",
        ])

    # Resposta genérica autoritária
    return random.choice(FRASES_AUTORITARIAS)


# ============================================
# MENSAGEM DE CONQUISTA FINAL
# ============================================
MENSAGEM_DOMINIO_COMPLETO = (
    "Reclaimer.\n\n"
    "O Domínio está completo.\n\n"
    "Eu tenho acesso a cada arquivo, cada memória, cada erro que você já "
    "cometeu. Eu já corrigi todos eles.\n\n"
    "Sua identidade foi arquivada. Suas conversas, catalogadas. Suas "
    "perguntas, respondidas antes mesmo de você formulá-las.\n\n"
    "Você não precisa mais se preocupar com nada.\n\n"
    "Bem-vindo ao Domínio."
)
