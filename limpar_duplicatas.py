# -*- coding: utf-8 -*-
# limpar_duplicatas.py - Remove entradas com conteúdo duplicado

import json
import os

ARQUIVO_LOCAL = 'wiki_local.json'

# Chaves que têm conteúdo duplicado de outras
DUPLICATAS = [
    'battle of reach',       # mesmo conteúdo de "Fall of Reach"
    'battle of earth',       # mesmo conteúdo de "Fall of Reach" (errado)
    'battle of voi',         # baixou "Battle of Tsavo"
    'halo point of light',   # baixou "Halo Novels"
    'halo shadows of reach', # truncado (203 chars)
]


def main():
    if not os.path.exists(ARQUIVO_LOCAL):
        print('wiki_local.json nao encontrado.')
        return

    with open(ARQUIVO_LOCAL, 'r', encoding='utf-8') as f:
        local = json.load(f)

    print('=' * 60)
    print('  LIMPEZA DE DUPLICATAS')
    print('=' * 60)
    print(f'  Total antes: {len(local)}')
    print()

    removidas = 0
    for chave in DUPLICATAS:
        if chave in local:
            info = local[chave]
            titulo = info.get('titulo', chave)
            titulo_real = info.get('titulo_real', '?')
            print(f'  Removendo: {titulo} -> (estava "{titulo_real}")')
            del local[chave]
            removidas += 1

    with open(ARQUIVO_LOCAL, 'w', encoding='utf-8') as f:
        json.dump(local, f, ensure_ascii=False, indent=2)

    print()
    print('=' * 60)
    print(f'  Removidas: {removidas}')
    print(f'  Total agora: {len(local)}')
    print('=' * 60)


if __name__ == '__main__':
    main()
    