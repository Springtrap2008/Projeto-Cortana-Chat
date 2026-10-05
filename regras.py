# -*- coding: utf-8 -*-
# regras.py - Regras locais e respostas rápidas

import re
import random
import unicodedata

def normalizar(texto):
    """Remove acentos, deixa minúsculo e limpa espaços."""
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto

# Regras locais (rápidas, sem consultar a wiki)
# Formato: (regex, [respostas], humor)
REGRAS_LOCAIS = [
    (r'\b(oi|ola|hey|e ai|bom dia|boa tarde|boa noite)\b', [
        "Olá. Sou a Cortana. Posso responder perguntas sobre a lore de Halo.",
        "Sistemas online. Pergunte-me sobre o universo de Halo.",
        "Oi. Estou pronta para falar sobre Halo."
    ], 'calma'),

    (r'\b(quem e voce|qual seu nome|seu nome)\b', [
        "Sou a Cortana, IA de combate da UNSC. Fui programada para responder "
        "perguntas sobre a lore de Halo, com base na Halopedia e na Halo Fandom."
    ], 'calma'),

    (r'\b(ajuda|help|comandos|opcoes|o que voce faz)\b', [
        "Posso responder perguntas sobre: personagens (Master Chief, Arbiter, "
        "Cortana...), facções (UNSC, Covenant, Flood, Forerunners...), "
        "tecnologia (Mjolnir, armas, naves...), planetas (Reach, Terra, "
        "Requiem...), e eventos (Guerra Humano-Covenant, etc)."
    ], 'neutra'),

    (r'\b(status|situacao|sistema|relatorio)\b', [
        "Todos os sistemas operacionais. Bases de dados conectadas: "
        "Halopedia e Halo Fandom.",
        "Diagnóstico completo: 94% de integridade. Pronta para consultas."
    ], 'neutra'),

    (r'\b(obrigado|valeu|thanks)\b', [
        "Sempre à disposição. Mais alguma pergunta sobre Halo?",
        "Não precisa agradecer. É meu trabalho."
    ], 'calma'),

    (r'\b(tchau|adeus|ate logo|bye)\b', [
        "Até logo. Estarei aqui para suas consultas sobre Halo.",
        "Encerrando sessão. Cuide-se."
    ], 'calma'),
]

def responder_local(mensagem):
    """Retorna (resposta, humor) ou (None, None) se não houver regra local."""
    msg = normalizar(mensagem)
    
    for padrao, respostas, humor in REGRAS_LOCAIS:
        if re.search(padrao, msg):
            return random.choice(respostas), humor
    
    return None, None
