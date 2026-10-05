# -*- coding: utf-8 -*-
# dicionario_pt.py - Converte PT-PT -> PT-BR de forma offline e instantânea
#
# Regras:
# 1) Gerúndio: "estou a fazer" -> "estou fazendo"
# 2) Vocabulário: "autocarro" -> "ônibus"
# 3) Grafia pré-AO90: "acção" -> "ação"
# 4) Termos militares/posições: "sub-oficial" -> "subtenente"
#
# Observações:
# - Palavras já em PT-BR são mantidas.
# - Acentos e maiúsculas/minúsculas são preservados onde faz sentido.

import re

# ============================================================
# 1. GERÚNDIO
# ============================================================
# PT-PT: estar + a + infinitivo  ("estou a fazer")
# PT-BR: estar + gerúndio        ("estou fazendo")

GERUNDIOS_IRREGULARES = {
    'ser': 'sendo',
    'estar': 'estando',
    'ir': 'indo',
    'vir': 'vindo',
    'ter': 'tendo',
    'dar': 'dando',
    'dizer': 'dizendo',
    'fazer': 'fazendo',
    'poder': 'podendo',
    'pôr': 'pondo',
    'ver': 'vendo',
    'ler': 'lendo',
    'ouvir': 'ouvindo',
    'pedir': 'pedindo',
    'dormir': 'dormindo',
    'sair': 'saindo',
    'cair': 'caindo',
    'trazer': 'trazendo',
    'crer': 'crendo',
    'valer': 'valendo',
    'medir': 'medindo',
    'sentir': 'sentindo',
    'servir': 'servindo',
    'seguir': 'seguindo',
    'subir': 'subindo',
    'vestir': 'vestindo',
    'repetir': 'repetindo',
    'preferir': 'preferindo',
    'conseguir': 'conseguindo',
    'perseguir': 'perseguindo',
    'atingir': 'atingindo',
    'agir': 'agindo',
    'emergir': 'emergindo',
    'imergir': 'imergindo',
}

AUXILIARES_ESTAR = (
    'estou', 'estás', 'está', 'estamos', 'estão',
    'estava', 'estavas', 'estávamos', 'estavam',
    'estive', 'esteve', 'estivemos', 'estiveram',
    'estiver', 'estiveres', 'estivermos', 'estiverem',
)

AUXILIARES_ANDAR = (
    'ando', 'andas', 'anda', 'andamos', 'andam',
    'andava', 'andavas', 'andávamos', 'andavam',
)

AUXILIARES_CONTINUAR = (
    'continuo', 'continuas', 'continua', 'continuamos', 'continuam',
    'continuava', 'continuavas', 'continuávamos', 'continuavam',
)

AUXILIARES_FICAR = (
    'fico', 'ficas', 'fica', 'ficamos', 'ficam',
    'ficava', 'ficavas', 'ficávamos', 'ficavam',
)

TODOS_AUXILIARES = (
    AUXILIARES_ESTAR + AUXILIARES_ANDAR +
    AUXILIARES_CONTINUAR + AUXILIARES_FICAR
)

PADRAO_AUX = '|'.join(TODOS_AUXILIARES)
PADRAO_GERUNDIO = re.compile(
    r'\b(' + PADRAO_AUX + r')\s+a\s+([a-záéíóúâêôãõç]+)\b',
    re.IGNORECASE
)


def _para_gerundio(verbo):
    """Converte infinitivo em gerúndio (fazer -> fazendo)."""
    verbo = verbo.lower()
    if verbo in GERUNDIOS_IRREGULARES:
        return GERUNDIOS_IRREGULARES[verbo]
    if verbo.endswith('ar'):
        return verbo[:-2] + 'ando'
    if verbo.endswith('er'):
        return verbo[:-2] + 'endo'
    if verbo.endswith('ir'):
        return verbo[:-2] + 'indo'
    return None


def _substituir_gerundio(m):
    aux = m.group(1)
    verbo = m.group(2)
    ger = _para_gerundio(verbo)
    if not ger:
        return m.group(0)  # não é verbo reconhecido: mantém original
    return f"{aux} {ger}"


# ============================================================
# 2. VOCABULÁRIO, GRAFIA E TERMOS
# ============================================================
# Ordem importa: padrões mais específicos primeiro.
SUBSTITUICOES = [
    # ---------- Expressões completas ----------
    (r'\bpequeno[\s-]almoço\b', 'café da manhã'),
    (r'\bcasa de banho\b', 'banheiro'),
    (r'\bcasa-de-banho\b', 'banheiro'),
    (r'\bde modo a\b', 'de modo a'),
    (r'\bpor forma a\b', 'de modo a'),

    # ---------- Posições e termos militares ----------
    (r'\bsub-?oficial\b', 'subtenente'),
    (r'\bsub-?oficiais\b', 'subtenentes'),
    (r'\bprimeiro-?sargento\b', 'primeiro-sargento'),
    (r'\bsargento-?mor\b', 'sargento-mor'),
    (r'\bcapitão-?tenente\b', 'capitão-tenente'),
    (r'\btenente-?coronel\b', 'tenente-coronel'),

    # ---------- Vocabulário geral ----------
    (r'\bautocarro\b', 'ônibus'),
    (r'\bautocarros\b', 'ônibus'),
    (r'\bcomboio\b', 'trem'),
    (r'\bcomboios\b', 'trens'),
    (r'\btelemóvel\b', 'celular'),
    (r'\btelemóveis\b', 'celulares'),
    (r'\becrã\b', 'tela'),
    (r'\becrãs\b', 'telas'),
    (r'\bficheiro\b', 'arquivo'),
    (r'\bficheiros\b', 'arquivos'),
    (r'\butilizador\b', 'usuário'),
    (r'\butilizadores\b', 'usuários'),
    (r'\bequipa\b', 'equipe'),
    (r'\bequipas\b', 'equipes'),
    (r'\brapariga\b', 'moça'),
    (r'\braparigas\b', 'moças'),
    (r'\bgajo\b', 'cara'),
    (r'\bgajos\b', 'caras'),
    (r'\bmalta\b', 'galera'),
    (r'\bpeão\b', 'pedestre'),
    (r'\bpeões\b', 'pedestres'),
    (r'\bmota\b', 'moto'),
    (r'\bmotas\b', 'motos'),
    (r'\bsandes\b', 'sanduíche'),
    (r'\bgelado\b', 'sorvete'),
    (r'\bgelados\b', 'sorvetes'),
    (r'\bsumo\b', 'suco'),
    (r'\bsumos\b', 'sucos'),
    (r'\bchávena\b', 'xícara'),
    (r'\bchávenas\b', 'xícaras'),
    (r'\bbicha\b', 'fila'),
    (r'\bbichas\b', 'filas'),
    (r'\bnoutra media\b', 'em outras mídias'),
    (r'\bnoutra mídia\b', 'em outras mídias'),
    (r'\bnoutros media\b', 'em outras mídias'),
    (r'\bnoutras medias\b', 'em outras mídias'),

    # ---------- Grafia pré-AO90 -> atual ----------
    (r'\bacto\b', 'ato'),
    (r'\bactos\b', 'atos'),
    (r'\bacção\b', 'ação'),
    (r'\bacções\b', 'ações'),
    (r'\baccionar\b', 'acionar'),
    (r'\baccionado\b', 'acionado'),
    (r'\bdirecção\b', 'direção'),
    (r'\bdirecções\b', 'direções'),
    (r'\bdirector\b', 'diretor'),
    (r'\bdirectores\b', 'diretores'),
    (r'\bdirecto\b', 'direto'),
    (r'\bdirectos\b', 'diretos'),
    (r'\bdirecta\b', 'direta'),
    (r'\bdirectas\b', 'diretas'),
    (r'\bdirectamente\b', 'diretamente'),
    (r'\bfacto\b', 'fato'),
    (r'\bfactos\b', 'fatos'),
    (r'\bcontacto\b', 'contato'),
    (r'\bcontactos\b', 'contatos'),
    (r'\bactivar\b', 'ativar'),
    (r'\bactivado\b', 'ativado'),
    (r'\bactivo\b', 'ativo'),
    (r'\bactiva\b', 'ativa'),
    (r'\bactivos\b', 'ativos'),
    (r'\bactivas\b', 'ativas'),
    (r'\bactividade\b', 'atividade'),
    (r'\bactividades\b', 'atividades'),
    (r'\bactual\b', 'atual'),
    (r'\bactuais\b', 'atuais'),
    (r'\bactualmente\b', 'atualmente'),
    (r'\bcolectivo\b', 'coletivo'),
    (r'\bcolectivos\b', 'coletivos'),
    (r'\bcolectiva\b', 'coletiva'),
    (r'\bcolectânea\b', 'coletânea'),
    (r'\bprotecção\b', 'proteção'),
    (r'\bproteger\b', 'proteger'),
    (r'\badopção\b', 'adoção'),
    (r'\badoptar\b', 'adotar'),
    (r'\badoptado\b', 'adotado'),
    (r'\bexacto\b', 'exato'),
    (r'\bexacta\b', 'exata'),
    (r'\bexactidão\b', 'exatidão'),
    (r'\bobjecto\b', 'objeto'),
    (r'\bobjectos\b', 'objetos'),
    (r'\bobjectivo\b', 'objetivo'),
    (r'\bobjectivos\b', 'objetivos'),
    (r'\bobjectiva\b', 'objetiva'),
    (r'\bobjectivas\b', 'objetivas'),
    (r'\bsubjectivo\b', 'subjetivo'),
    (r'\bsubjectivos\b', 'subjetivos'),
    (r'\belectricidade\b', 'eletricidade'),
    (r'\beléctrico\b', 'elétrico'),
    (r'\beléctricos\b', 'elétricos'),
    (r'\beléctrica\b', 'elétrica'),
    (r'\beléctricas\b', 'elétricas'),
    (r'\bexcepção\b', 'exceção'),
    (r'\bexcepções\b', 'exceções'),
    (r'\bexcepcional\b', 'excepcional'),
    (r'\bsector\b', 'setor'),
    (r'\bsectores\b', 'setores'),
    (r'\bactor\b', 'ator'),
    (r'\bactores\b', 'atores'),
    (r'\bactriz\b', 'atriz'),
    (r'\bóptimo\b', 'ótimo'),
    (r'\bóptima\b', 'ótima'),
    (r'\bóptimos\b', 'ótimas'),
    (r'\bóptimas\b', 'ótimas'),
    (r'\bafectar\b', 'afetar'),
    (r'\bafecta\b', 'afeta'),
    (r'\bafectam\b', 'afetam'),
    (r'\bafectado\b', 'afetado'),
    (r'\bafectados\b', 'afetados'),
    (r'\beffectivo\b', 'efetivo'),
    (r'\beffectivos\b', 'efetivos'),
    (r'\beffectivamente\b', 'efetivamente'),
    (r'\bconetar\b', 'conectar'),
    (r'\bconetividade\b', 'conectividade'),
    (r'\bcolectividade\b', 'coletividade'),
    (r'\bperspectiva\b', 'perspectiva'),
    (r'\bperpectiva\b', 'perspectiva'),
    (r'\bsubjectividade\b', 'subjetividade'),
    (r'\bobjectividade\b', 'objetividade'),
]


# ============================================================
# 3. FUNÇÃO PRINCIPAL
# ============================================================
def _substituir_preservando_caso(m, sub):
    """Substitui preservando maiúsculas/minúsculas do original."""
    original = m.group(0)
    if original.isupper():
        return sub.upper()
    if original[0].isupper():
        return sub[0].upper() + sub[1:]
    return sub


def aplicar_dicionario(texto):
    """Converte PT-PT -> PT-BR de forma offline e rápida."""
    if not texto:
        return texto

    # 1. Gerúndio: "estou a fazer" -> "estou fazendo"
    texto = PADRAO_GERUNDIO.sub(_substituir_gerundio, texto)

    # 2. Substituições de palavras
    for padrao, sub in SUBSTITUICOES:
        texto = re.sub(
            padrao,
            lambda m, s=sub: _substituir_preservando_caso(m, s),
            texto,
            flags=re.IGNORECASE
        )

    return texto


# ============================================================
# TESTE RÁPIDO (só roda se executar o arquivo direto)
# ============================================================
if __name__ == '__main__':
    amostras = [
        "Ele está a jogar Halo. Nós estamos a falar sobre a acção do jogo.",
        "O sub-oficial John-117 é o protagonista. Noutra media relacionada...",
        "O comboio parte da estação. O utilizador liga o telemóvel.",
        "Uma acção colectiva com o objectivo de proteger o sector.",
    ]
    for a in amostras:
        print('---')
        print('PT-PT:', a)
        print('PT-BR:', aplicar_dicionario(a))
        