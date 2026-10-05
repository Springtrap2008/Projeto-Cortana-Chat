# -*- coding: utf-8 -*-
# arrumar.py - Retraduz artigos em inglês e remove duplicatas

import json
import os
import re
import sys
import time
import hashlib
import shutil
from datetime import datetime

import baixar_wiki

ARQUIVO = 'wiki_local.json'
BACKUP = 'wiki_local.backup.json'

PALAVRAS_INGLES = [
    ' the ', ' and ', ' of ', ' is ', ' was ', ' were ', ' has ', ' have ',
    ' which ', ' their ', ' this ', ' that ', ' with ', ' from ', ' they ',
    ' would ', ' could ', ' should ', ' been ', ' being ', ' are ', ' his ',
    ' her ', ' its ', ' will ', ' can ', ' may ', ' might ', ' into ',
    ' over ', ' when ', ' where ', ' what ', ' who ', ' how ',
]

PREFERENCIAS = {
    'catherine elizabeth halsey': ['catherine halsey', 'dr. halsey'],
    'noble six': ['spartan-b312'],
    'ellen anders': ['professor anders'],
    'isodidact': ['bornstellar'],
    'foe hammer': ['carol rawley'],
    'lord hood': ['terrence hood', 'admiral hood'],
    'black-box': ['bb'],
    'kurt-051': ['kurt ambrose'],
    "sesa 'refumee": ['sesa refumee'],
    "rtas 'vadum": ['rtas', 'half-jaw'],
    'reclaimer': ['reclaimers'],
    'mjolnir': ['mjolnir powered assault armor'],
    'pillar of autumn': ['unsc pillar of autumn'],
    'zeta halo': ['instalação 07', 'installation 07'],
    'spi armor': ['spi'],
}

PRIORITARIOS = [
    'cortana', 'john-117', 'master chief', 'arbiter', 'unsc',
    'covenant', 'flood', 'forerunners', 'created', 'oni',
]


def carregar():
    with open(ARQUIVO, 'r', encoding='utf-8') as f:
        return json.load(f)


def salvar(dados):
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def e_ingles(texto):
    if not texto:
        return False
    amostra = texto[:2500].lower()
    score = sum(1 for p in PALAVRAS_INGLES if p in amostra)
    return score >= 10


def normalizar_conteudo(texto):
    if not texto:
        return ''
    amostra = texto[:400].lower()
    amostra = re.sub(r'\s+', ' ', amostra)
    amostra = re.sub(r'[^\w\s]', '', amostra)
    return amostra.strip()


def hash_conteudo(texto):
    norm = normalizar_conteudo(texto)
    return hashlib.md5(norm.encode('utf-8')).hexdigest()


# ============================================
# RETRADUÇÃO
# ============================================
def retraduzir(local, só_relatorio=False):
    em_ingles = [chave for chave, info in local.items()
                 if e_ingles(info.get('conteudo', ''))]

    print('=' * 60)
    print('  ARTIGOS EM INGLÊS')
    print('=' * 60)
    print(f'  Total: {len(em_ingles)} de {len(local)}')

    if not em_ingles:
        print('  Nada para retraduzir.')
        return 0, 0

    def prioridade(chave):
        return 0 if chave in PRIORITARIOS else 1

    em_ingles.sort(key=prioridade)

    print()
    for chave in em_ingles:
        titulo = local[chave].get('titulo', chave)
        marca = ' ★' if chave in PRIORITARIOS else ''
        print(f'  - {titulo}{marca}')

    if só_relatorio:
        return len(em_ingles), 0

    print()
    resposta = input('Retraduzir todos? (s/n): ').strip().lower()
    if resposta != 's':
        return len(em_ingles), 0

    print()
    sucesso = 0
    falhas = 0

    for i, chave in enumerate(em_ingles, 1):
        info = local[chave]
        titulo = info.get('titulo', chave)
        print(f'[{i}/{len(em_ingles)}] {titulo}', end=' ', flush=True)

        try:
            traduzido = baixar_wiki.traduzir_en_pt(info.get('conteudo', ''))

            if traduzido and not e_ingles(traduzido):
                info['conteudo'] = traduzido
                info['idioma'] = 'pt'
                sucesso += 1
                print('OK')
            else:
                falhas += 1
                print('falhou (mantendo EN)')
        except Exception as e:
            falhas += 1
            print(f'ERRO: {e}')

        time.sleep(1.5)

        if i % 3 == 0:
            salvar(local)

    salvar(local)
    print()
    print(f'  Retraduzidos: {sucesso}')
    print(f'  Falhas:       {falhas}')
    return len(em_ingles), sucesso


# ============================================
# DUPLICATAS
# ============================================
def detectar_duplicatas(local):
    grupos = {}
    for chave, info in local.items():
        h = hash_conteudo(info.get('conteudo', ''))
        if not h:
            continue
        grupos.setdefault(h, []).append(chave)
    return {h: chaves for h, chaves in grupos.items() if len(chaves) > 1}


def escolher_principal(chaves, local):
    """Escolhe qual CHAVE manter, respeitando PREFERENCIAS."""
    # 1. Se alguma chave é preferida explicitamente, é ela
    for chave in chaves:
        if chave in PREFERENCIAS:
            return chave

    # 2. Remove as que estão marcadas para remover
    todas_remover = set()
    for lista in PREFERENCIAS.values():
        todas_remover.update(lista)

    candidatas = [c for c in chaves if c not in todas_remover]
    if candidatas:
        chaves = candidatas

    # 3. Fallback: idioma PT, tamanho, chave mais curta
    def score(chave):
        info = local[chave]
        idioma_pt = 1 if info.get('idioma') == 'pt' else 0
        tamanho = len(info.get('conteudo', ''))
        len_chave = -len(chave)
        return (idioma_pt, tamanho, len_chave)

    return max(chaves, key=score)


def remover_duplicatas(local, só_relatorio=False):
    """Remove duplicatas mantendo a chave preferida + o conteúdo mais longo."""
    duplicatas = detectar_duplicatas(local)

    print()
    print('=' * 60)
    print('  DUPLICATAS DETECTADAS')
    print('=' * 60)
    print(f'  Grupos com conteúdo idêntico: {len(duplicatas)}')

    if not duplicatas:
        print('  Nenhuma duplicata.')
        return 0

    total_remover = sum(len(chaves) - 1 for chaves in duplicatas.values())
    print(f'  Artigos a remover: {total_remover}')
    print()

    # Monta o plano
    plano = []
    for h, chaves in duplicatas.items():
        preferida = escolher_principal(chaves, local)

        # Pega o conteúdo mais longo entre todos do grupo
        melhor_conteudo = ''
        for c in chaves:
            cont = local[c].get('conteudo', '')
            if len(cont) > len(melhor_conteudo):
                melhor_conteudo = cont

        info_pref = local[preferida]
        titulo_final = info_pref.get('titulo', preferida)
        fonte_final = info_pref.get('fonte', '')
        idioma_final = info_pref.get('idioma', 'pt')

        removidos = [c for c in chaves if c != preferida]

        plano.append({
            'chave': preferida,
            'titulo': titulo_final,
            'conteudo': melhor_conteudo,
            'fonte': fonte_final,
            'idioma': idioma_final,
            'remover': removidos
        })

        print(f'  Manter: {titulo_final}')
        for c in removidos:
            titulo = local[c].get('titulo', c)
            print(f'    Remover: {titulo}')

    if só_relatorio:
        return total_remover

    print()
    resposta = input('Remover duplicatas? (s/n): ').strip().lower()
    if resposta != 's':
        return 0

    removidos_count = 0
    for p in plano:
        for c in p['remover']:
            if c in local:
                del local[c]
                removidos_count += 1

        # Substitui a chave preferida com o melhor conteúdo
        local[p['chave']] = {
            'titulo': p['titulo'],
            'conteudo': p['conteudo'],
            'fonte': p['fonte'],
            'idioma': p['idioma']
        }

    salvar(local)
    print()
    print(f'  Removidos: {removidos_count}')
    return removidos_count


# ============================================
# BACKUP
# ============================================
def fazer_backup():
    if not os.path.exists(ARQUIVO):
        print(f'[ERRO] {ARQUIVO} não encontrado.')
        return False

    if os.path.exists(BACKUP):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        antigo = f'wiki_local.backup_{timestamp}.json'
        shutil.move(BACKUP, antigo)
        print(f'  Backup antigo movido para: {antigo}')

    shutil.copy(ARQUIVO, BACKUP)
    tamanho = os.path.getsize(BACKUP) / 1024
    print(f'  Backup criado: {BACKUP} ({tamanho:.1f} KB)')
    return True


# ============================================
# MAIN
# ============================================
def main():
    só_relatorio = '--só-relatorio' in sys.argv or '--so-relatorio' in sys.argv
    sem_retraduzir = '--sem-retraduzir' in sys.argv

    print('=' * 60)
    print('  ARRUMAR - Wiki Local da Cortana')
    print('=' * 60)
    print()

    if not os.path.exists(ARQUIVO):
        print(f'[ERRO] {ARQUIVO} não encontrado.')
        print('Rode primeiro: baixar_wiki.bat')
        return

    if not só_relatorio:
        print('[1/3] Fazendo backup...')
        if not fazer_backup():
            return
    else:
        print('[MODO RELATÓRIO] Nada será alterado.')
    print()

    local = carregar()
    total_antes = len(local)

    if not sem_retraduzir:
        print('[2/3] Verificando artigos em inglês...')
        retraduzir(local, só_relatorio)
    else:
        print('[2/3] Retradução pulada (--sem-retraduzir)')
    print()

    local = carregar()

    print('[3/3] Verificando duplicatas...')
    remover_duplicatas(local, só_relatorio)
    print()

    local = carregar()
    total_depois = len(local)

    print('=' * 60)
    print('  RESUMO')
    print('=' * 60)
    print(f'  Artigos antes:    {total_antes}')
    print(f'  Artigos depois:   {total_depois}')
    print(f'  Diferença:        {total_antes - total_depois}')

    em_ingles = sum(1 for v in local.values()
                    if e_ingles(v.get('conteudo', '')))
    print(f'  Em inglês ainda:  {em_ingles}')

    if not só_relatorio and os.path.exists(BACKUP):
        print(f'  Backup: {BACKUP}')

    print('=' * 60)
    print()
    print('Pronto. Pode usar o iniciar.bat normalmente.')


if __name__ == '__main__':
    main()
