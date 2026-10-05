# -*- coding: utf-8 -*-
# gatekeeper.py - Verifica se a pergunta é sobre a lore de Halo

import re

TERMOS_HALO = [
    # Facções
    'unsc', 'covenant', 'forerunner', 'flood', 'banished', 'promethean',
    'elite', 'sangheili', 'grunt', 'unggoy', 'brute', 'jiralhanae',
    'jackal', 'kig-yar', 'hunter', 'mgalekgolo', 'prophet', 'hierarch',
    'precursor', 'ancilla', 'monitor', 'guardian', 'created',
    # Personagens
    'master chief', 'john-117', 'cortana', 'arbiter', 'thel vadam',
    'captain keyes', 'miranda keyes', 'johnson', 'guilty spark',
    'didact', 'librarian', 'gravemind', 'noble six', 'emile', 'jorge',
    'carter', 'kat', 'jun', 'locke', 'lasky', 'palmer',
    'halsey', 'mendez', 'blue team', 'osiris', 'atlas', 'atn',
    'chief', 'espartano', 'spartan',
    # Organizações
    'oni', 'odst', 'majestic', 'infinity', 'pillar of autumn',
    'noble team', 'red team', 'blue team',
    # Tecnologia
    'mjolnir', 'energy sword', 'needler', 'assault rifle', 'magnum',
    'plasma', 'shield', 'warthog', 'scorpion', 'pelican', 'broadsword',
    'longsword', 'falcon', 'hornet', 'mongoose', 'ghost', 'banshee',
    'wraith', 'phantom', 'spirit', 'seraph', 'mantis',
    # Lugares / instalações
    'halo', 'installation', 'ring', 'ark', 'reach', 'harvest',
    'earth', 'terra', 'onyx', 'requiem', 'genesis', 'mombasa',
    'new mombasa', 'blood gulch', 'high charity', 'covenant holy city',
    # Eventos e conceitos
    'covenant war', 'human-covenant', 'reclaimer', 'composer',
    'domain', 'mantle', 'rampancy', 'great journey', 'forerunner war',
    'forerunner-flood', 'flood war', 'harvest campaign',
    # Jogos / mídia
    'halo combat evolved', 'halo 2', 'halo 3', 'halo 4', 'halo 5',
    'halo infinite', 'halo reach', 'halo odst', 'halo wars',
    'spartan ops', 'fireteam', 'infinite',
    # Lore em geral
    'lore', 'canon', 'universo halo', 'historia de halo',
    'linha do tempo', 'cronologia', 'enciclopedia', 'wiki',
]

PALAVRAS_PERGUNTA = [
    'quem e', 'quem foi', 'quem sao', 'o que e', 'o que foi', 'o que sao',
    'onde fica', 'onde esta', 'onde foi', 'como funciona', 'como surgiu',
    'qual a historia', 'qual o papel', 'qual foi', 'me fale sobre',
    'fale sobre', 'sobre', 'explica', 'explique', 'descreva',
    'me conta sobre', 'conta sobre', 'pesquise sobre', 'busque sobre',
]

def normalizar(texto):
    """Remove acentos e deixa minúsculo."""
    import unicodedata
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    return texto

def e_pergunta_halo(mensagem):
    """Retorna True se a mensagem parece ser sobre a lore de Halo."""
    if not mensagem or not mensagem.strip():
        return False
    
    msg = normalizar(mensagem)
    
    # Verifica termos diretos
    for termo in TERMOS_HALO:
        if termo in msg:
            return True
    
    # Verifica se é uma pergunta usando palavras-chave + termo Halo
    if any(p in msg for p in PALAVRAS_PERGUNTA):
        # Se a pergunta tem "halo" em algum lugar, aceita
        if 'halo' in msg:
            return True
    
    return False

def mensagem_recusa():
    """Mensagem padrão de recusa para temas fora de Halo."""
    return ("Sinto muito, mas fui programada para responder exclusivamente "
            "perguntas sobre o universo de Halo. Posso falar sobre personagens, "
            "facções, tecnologia, planetas, eventos históricos e a lore em geral. "
            "O que você gostaria de saber?")
    