# -*- coding: utf-8 -*-
# limpar_errados.py - Remove entradas erradas do wiki_local.json

import json
import os

ARQUIVO_LOCAL = 'wiki_local.json'

# Chaves que baixaram artigos ERRADOS na última execução
CHAVES_ERRADAS = [
    'terra',              # baixou "Base Segundo Terra" em vez de "Earth"
    'a arca',             # baixou "Audio log" em vez de "Installation 00"
    'nova alexandria',    # baixou "Skyline (map)" em vez de "New Alexandria"
    'batalha da terra',   # baixou "Base Segundo Terra" em vez de "Battle of Earth"
    'batalha de voi',     # baixou "Battle of Ven III" em vez de "Battle of Voi"
    'batalha da arca',    # baixou "Phoenix Log" em vez de "Battle of Installation 00"
    'halo point of light',# baixou "Halo Novels" em vez de "Halo: Point of Light"
]


def main():
    if not os.path.exists(ARQUIVO_LOCAL):
        print('wiki_local.json nao encontrado.')
        return

    with open(ARQUIVO_LOCAL, 'r', encoding='utf-8') as f:
        local = json.load(f)

    print('=' * 60)
    print('  LIMPEZA DE ENTRADAS ERRADAS')
    print('=' * 60)
    print(f'  Total antes: {len(local)}')
    print()

    removidas = 0
    for chave in CHAVES_ERRADAS:
        if chave in local:
            info = local[chave]
            titulo = info.get('titulo', chave)
            titulo_real = info.get('titulo_real', '?')
            print(f'  Removendo: {titulo} -> (estava "{titulo_real}")')
            del local[chave]
            removidas += 1
        else:
            print(f'  (nao encontrado: {chave})')

    with open(ARQUIVO_LOCAL, 'w', encoding='utf-8') as f:
        json.dump(local, f, ensure_ascii=False, indent=2)

    print()
    print('=' * 60)
    print(f'  Removidas: {removidas}')
    print(f'  Total agora: {len(local)}')
    print('=' * 60)
    print()
    print('Pronto. Agora rode baixar_wiki.bat para baixar')
    print('os artigos com os nomes CORRETOS.')


if __name__ == '__main__':
    main()
    