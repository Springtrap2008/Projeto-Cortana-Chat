# -*- coding: utf-8 -*-
# baixar_wiki.py - Baixa artigos com busca inteligente e nomes corrigidos

import requests
import json
import os
import re
import sys
import time
import html as html_module

HEADERS = {'User-Agent': 'CortanaChatbot/1.0 (projeto pessoal de fã)'}
ARQUIVO_LOCAL = 'wiki_local.json'
ARQUIVO_FALHAS = 'falhas.txt'

WIKIS = [
    {'nome': 'fandom_pt', 'api': 'https://pt-br.halo.fandom.com/api.php', 'idioma': 'pt'},
    {'nome': 'fandom_en', 'api': 'https://halo.fandom.com/api.php',       'idioma': 'en'},
    {'nome': 'halopedia', 'api': 'https://www.halopedia.org/api.php',     'idioma': 'en'},
]


ARTIGOS = [
    # PERSONAGENS
    'John-117', 'Master Chief', 'Cortana', 'Arbiter', 'Thel Vadam',
    'Gravemind', 'Didact', 'Librarian', 'Catherine Elizabeth Halsey',
    'Avery Johnson', 'Miranda Keyes', 'Jacob Keyes',
    'Noble Six', 'SPARTAN-B312',
    '343 Guilty Spark', 'Jameson Locke', 'Thomas Lasky', 'Sarah Palmer',
    'Edward Buck', "Rtas 'Vadum", 'Mendicant Bias', 'Atriox',
    'High Prophet of Truth', 'High Prophet of Regret', 'High Prophet of Mercy',
    'Jorge-052', 'Emile-A239', 'Carter-A259', 'Kat-B320', 'Jun-A266',
    'Fred-104', 'Kelly-087', 'Linda-058', 'Jerome-092', 'Alice-130', 'Douglas-042',
    'Sergeant Forge', 'Serina', 'Ellen Anders', 'Captain Cutter',
    'Master Builder', 'IsoDidact', 'Bornstellar-Makes-Eternal-Lasting',
    'Offensive Bias', 'Warden Eternal', 'Exuberant Witness', 'The Weapon',
    'The Harbinger', 'Escharum', 'Jega Rdomnai',
    'Andrew Del Rio', 'Sergeant Stacker', 'Sergeant Banks', 'Chips Dubbo',
    'Wallace Jenkins', 'Carol Rawley', 'Terrence Hood',
    'Margaret Parangosky', 'Serin Osman', 'Black-Box',
    'Kurt-051', 'Franklin Mendez', 'Musa-096',
    'Tom-B292', 'Lucy-B091',
    'Roland (AI)', 'Isabel (AI)',
    "Sesa 'Refumee", 'Tartarus',
    'Preston Cole', 'Hieronymus Stanforth',
    'Faber-of-Will-and-Might',

    # FACÇÕES (nomes em inglês porque existem nas wikis)
    'UNSC', 'Covenant', 'Flood', 'Forerunners', 'Precursors',
    'Banished', 'Created', 'ONI', 'Prometheans', 'Hierarchs',
    'Sangheili', 'Jiralhanae', 'Unggoy', 'Kig-Yar', 'Mgalekgolo',
    "Yanme'e", 'Huragok', "San'Shyuum",
    'Reclaimers', 'Ecumene', 'Ancilla', 'Guardians',
    'SPARTAN-II', 'SPARTAN-III', 'SPARTAN-IV', 'ORION Project',
    'ODST', 'Noble Team', 'Blue Team', 'Red Team', 'Fireteam Osiris',
    'Fireteam Majestic', 'Sword of Sanghelios',
    'Swords of Sanghelios', 'New Colonial Alliance', 'Insurrectionists',

    # TECNOLOGIA
    'Mjolnir', 'SPI Armor', 'Slipspace', 'Shaw-Fujikawa Translight Engine',
    'Composer', 'Cole Protocol',
    'MAC', 'Archer Missile', 'Shiva', 'Nova Bomba',
    'Smart AI', 'Dumb AI', 'Rampancy',
    'Geas', 'Mantle of Responsibility', 'Domain',

    # NAVES
    'UNSC Infinity', 'Pillar of Autumn', 'UNSC In Amber Clad',
    'UNSC Forward Unto Dawn', 'UNSC Savannah', 'UNSC Spirit of Fire',
    'Shadow of Intent', 'Truth and Reconciliation', 'High Charity',
    'Longsword', 'Broadsword', 'Sabre', 'Pelican',
    'Phantom', 'Spirit', 'Seraph', 'Banshee',
    'Warthog', 'Scorpion', 'Mantis', 'Mongoose',
    'Wraith', 'Ghost', 'Chopper', 'Revenant',
    'Scarab', 'Kraken', 'Lich',

    # ARMAS
    'Energy Sword', 'Plasma Rifle', 'Plasma Pistol',
    'Needler', 'Spiker', 'Brute Shot', 'Gravity Hammer',
    'Carbine', 'Beam Rifle', 'Focus Rifle',
    'DMR', 'Battle Rifle', 'Assault Rifle', 'SMG', 'Magnum',
    'Sniper Rifle', 'Rocket Launcher', 'Spartan Laser', 'Shotgun',
    'Sentinel Beam', 'Fuel Rod Cannon',
    'Boltshot', 'Lightrifle', 'Suppressor', 'Scattershot',
    'Incineration Cannon', 'Binary Rifle', 'Railgun',

    # LUGARES (nomes em inglês para evitar artigos errados)
    'Reach', 'Earth', 'Harvest', 'Sanghelios', 'Doisac', 'Balaho',
    'High Charity', 'Installation 04', 'Installation 05', 'Installation 00',
    'Installation 03', 'Installation 06', 'Installation 07',
    'The Ark', 'Requiem', 'Genesis', 'Onyx', 'Shield World 006',
    'New Mombasa', 'Mombasa', 'Voi', 'New Alexandria',
    'Corbulo Academy of Military Science', 'Circinius IV', 'Meridian', 'Kamchatka',
    'Draco III', 'Madrigal', 'Venezia', 'Sunaion',
    'Zeta Halo', 'Alpha Halo', 'Delta Halo',
    'Eayn', 'Palamok',

    # EVENTOS
    'Human-Covenant War', 'Fall of Reach',
    'Battle of Installation 04', 'Battle of Mombasa',
    'Battle of Installation 00', 'Battle of Requiem', 'Battle of Meridian',
    'Battle of Genesis', 'Battle of Installation 07', 'Battle of Kamchatka',
    'Battle of Sunaion', 'Battle of Voi (2552)',
    'Great Journey', 'Human-Forerunner War', 'Forerunner-Flood War',
    'Blooding Years', 'Great Schism',
    'Operation: RED FLAG', 'Operation: UPPERCUT', 'Operation: TORPEDO',
    'Operation: TREBUCHET',
    'Battle of Harvest', 'Battle of Tsavo',

    # JOGOS
    'Halo Combat Evolved', 'Halo 2', 'Halo 3', 'Halo 3 ODST',
    'Halo Reach', 'Halo 4', 'Halo 5 Guardians', 'Halo Infinite',
    'Halo Wars', 'Halo Wars 2',
    'Halo The Master Chief Collection',
    'Halo Spartan Assault', 'Halo Spartan Strike',

    # LIVROS
    'Halo The Fall of Reach', 'Halo The Flood', 'Halo First Strike',
    'Halo Ghosts of Onyx', 'Halo Contact Harvest', 'Halo Cryptum',
    'Halo Primordium', 'Halo Silentium', 'Halo Glasslands',
    'Halo The Thursday War', 'Halo Mortal Dictata', 'Halo New Blood',
    'Halo Hunters in the Dark', 'Halo Last Light', 'Halo Retribution',
    'Halo Silent Storm', 'Halo Oblivion', 'Halo Divine Wind', 'Halo: Point of Light',

    # MÍDIA
    'Halo Legends', 'Halo 4: Forward Unto Dawn', 'Halo Nightfall',
    'Red vs Blue',

    # CONCEITOS
    'Reclaimer', 'Monitor',
    'Neural Physics',
    'Proto-Gravemind', 'Infection Form', 'Combat Form',
    'Carrier Form', 'Pure Form', 'Keymind',
    'Halos', 'Ark',
    'Promethean Knight', 'Promethean Soldier', 'Promethean Watcher',
    'Promethean Crawler',
    'Warden Eternal', 'The Created',
]


def carregar_local():
    if os.path.exists(ARQUIVO_LOCAL):
        try:
            with open(ARQUIVO_LOCAL, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def salvar_local(dados):
    with open(ARQUIVO_LOCAL, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def chave_artigo(titulo):
    return titulo.lower().strip()


# ============================================
# ALIASES — artigos que são o mesmo, mas têm nomes diferentes
# ============================================
ALIASES = [
    {'master chief', 'john-117', 'john 117', 'chief', '117', 'spartan-117'},
    {'noble six', 'spartan-b312', 'b312'},
    {'arbiter', 'thel vadam', "thel 'vadam"},
    {'catherine elizabeth halsey', 'catherine halsey', 'dra halsey', 'dr halsey', 'halsey'},
    {'avery johnson', 'sargento johnson', 'sargento major johnson', 'johnson'},
    {'miranda keyes', 'comandante keyes'},
    {'jacob keyes', 'capitao keyes', 'captain keyes'},
    {'earth', 'terra'},
    {'reach', 'planeta reach'},
    {'installation 04', 'instalacao 04', 'alpha halo'},
    {'installation 05', 'instalacao 05', 'delta halo'},
    {'installation 07', 'instalacao 07', 'zeta halo'},
    {'installation 00', 'instalacao 00', 'the ark', 'a arca'},
    {'high charity', 'cidade santa'},
    {'banished', 'banidos'},
    {'hierarchs', 'hierarcas'},
    {'guardians', 'guardioes'},
    {'guardian', 'guardiao'},
    {'precursors', 'precursores'},
    {'forerunners', 'forerunner'},
    {'orion project', 'programa orion', 'spartan-i program'},
    {'new mombasa', 'nova mombasa'},
    {'new alexandria', 'nova alexandria'},
    {'venezia', 'veneza'},
    {'energy sword', 'espada de energia'},
    {'mantle of responsibility', 'manto da responsabilidade'},
    {'human-covenant war', 'guerra humano-covenant'},
    {'fall of reach', 'queda de reach', 'batalha de reach', 'battle of reach'},
    {'battle of earth', 'batalha da terra'},
    {'battle of installation 00', 'batalha da arca', 'battle of the ark'},
    {'battle of voi (2552)', 'battle of voi', 'batalha de voi'},
    {'great journey', 'grande jornada'},
    {'great schism', 'grande cisma'},
    {'operation: red flag', 'operacao red flag', 'operacao: red flag'},
    {'operation: uppercut', 'operacao uppercut'},
    {'operation: torpedo', 'operacao torpedo'},
    {'operation: trebuchet', 'operacao trebuchet'},
    {'battle of harvest', 'batalha de harvest'},
    {'sanghelios', 'sanghelios planeta'},
    {"yanme'e", 'yanmee', 'yanme e'},
    {"san'shyuum", 'san shyuum', 'profetas'},
    {'spi armor', 'armadura spi'},
    {'shaw-fujikawa translight engine', 'motor de dobra', 'slipspace drive'},
]


def _normalizar_chave(titulo):
    """Remove pontuação e normaliza para comparar."""
    t = titulo.lower().strip()
    t = re.sub(r'[:\-_]', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()


def _encontrar_alias(titulo):
    """Retorna o grupo de aliases do título, ou None."""
    chave = _normalizar_chave(titulo)
    for grupo in ALIASES:
        grupo_norm = {_normalizar_chave(a) for a in grupo}
        if chave in grupo_norm:
            return grupo_norm
    return None


def ja_tem_artigo(local, titulo):
    """
    Verifica se o artigo já existe, considerando:
    1. Chave exata
    2. Título ou título_real iguais
    3. Aliases conhecidos
    """
    chave = chave_artigo(titulo)
    if chave in local:
        return True

    # Compara com aliases
    aliases = _encontrar_alias(titulo)
    chaves_para_buscar = {chave}
    if aliases:
        chaves_para_buscar.update(aliases)
    chaves_para_buscar = {_normalizar_chave(c) for c in chaves_para_buscar}

    for k, v in local.items():
        t = _normalizar_chave(v.get('titulo', ''))
        tr = _normalizar_chave(v.get('titulo_real', ''))
        k_norm = _normalizar_chave(k)

        if t in chaves_para_buscar or tr in chaves_para_buscar or k_norm in chaves_para_buscar:
            return True

    return False

SECOES_IGNORAR = [
    'design do personagem', 'design', 'produção', 'desenvolvimento',
    'recepção', 'críticas', 'curiosidades', 'trivia', 'galeria',
    'referências', 'notas', 'ver também', 'links externos', 'fontes',
    'jogabilidade', 'dublagem', 'vozes', 'merchandise', 'prêmios',
    'development', 'production', 'reception', 'gallery', 'references',
    'notes', 'see also', 'external links', 'behind the scenes',
    'appearances', 'sources', 'easter eggs',
]


def remover_secoes_irrelevantes(texto):
    linhas = texto.split('\n')
    resultado = []
    ignorar = False
    for linha in linhas:
        m = re.match(r'^\s*=+\s*(.+?)\s*=+\s*$', linha)
        if m:
            titulo = m.group(1).strip().lower()
            limpo = re.sub(r'[^\w\s]', '', titulo).strip()
            ignorar = any(sec in limpo for sec in SECOES_IGNORAR)
            continue
        if not ignorar:
            resultado.append(linha)
    return '\n'.join(resultado)


def limpar_texto_wiki(texto):
    texto = remover_secoes_irrelevantes(texto)
    texto = re.sub(r'\[\d+\]', '', texto)
    texto = re.sub(r"'{2,}", '', texto)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    texto = re.sub(r'[ \t]+', ' ', texto)
    return texto.strip()


def limpar_html_para_texto(html):
    html = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.DOTALL)
    html = re.sub(r'<table[^>]*>.*?</table>', ' ', html,
                  flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<sup[^>]*class="[^"]*reference[^"]*"[^>]*>.*?</sup>',
                  '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'\n\n\1\n\n', html,
                  flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'</p>', '\n\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    texto = re.sub(r'<[^>]+>', ' ', html)
    texto = html_module.unescape(texto)
    texto = re.sub(r'\[\d+\]', '', texto)
    texto = re.sub(r'[ \t]+', ' ', texto)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return limpar_texto_wiki(texto)


def limpar_wikitext(texto):
    texto = re.sub(r'\{\{[^{}]*\}\}', '', texto)
    texto = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]+)\]\]', r'\1', texto)
    texto = re.sub(r'\[https?://[^\s\]]+\s+([^\]]+)\]', r'\1', texto)
    texto = re.sub(r'=+\s*(.*?)\s*=+', r'\n\n\1\n\n', texto)
    texto = re.sub(r'<ref[^>]*>.*?</ref>', '', texto, flags=re.DOTALL)
    texto = re.sub(r'<ref[^>]*/>', '', texto)
    texto = re.sub(r'<[^>]+>', '', texto)
    texto = re.sub(r"'{2,}", '', texto)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    texto = re.sub(r'[ \t]+', ' ', texto)
    return limpar_texto_wiki(texto)


def buscar_titulos(wiki, termo, limite=3):
    params = {
        'action': 'query', 'list': 'search', 'srsearch': termo,
        'srlimit': limite, 'format': 'json', 'origin': '*'
    }
    try:
        r = requests.get(wiki['api'], params=params, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return []
        dados = r.json()
        resultados = dados.get('query', {}).get('search', [])
        return [item['title'] for item in resultados]
    except Exception:
        return []


def tentar_extracts(wiki, titulo):
    params = {
        'action': 'query', 'prop': 'extracts', 'titles': titulo,
        'format': 'json', 'explaintext': 1, 'redirects': 1, 'origin': '*'
    }
    try:
        r = requests.get(wiki['api'], params=params, headers=HEADERS, timeout=15)
        dados = r.json()
        for pid, pagina in dados.get('query', {}).get('pages', {}).items():
            if 'extract' in pagina and pagina['extract'].strip():
                txt = limpar_texto_wiki(pagina['extract'])
                if txt and len(txt) > 80:
                    return txt
    except Exception:
        pass
    return None


def tentar_parse(wiki, titulo):
    params = {
        'action': 'parse', 'page': titulo, 'format': 'json',
        'prop': 'text', 'redirects': 1, 'origin': '*'
    }
    try:
        r = requests.get(wiki['api'], params=params, headers=HEADERS, timeout=15)
        dados = r.json()
        if 'error' in dados:
            return None
        html = dados.get('parse', {}).get('text', {}).get('*', '')
        if html:
            txt = limpar_html_para_texto(html)
            if txt and len(txt) > 80:
                return txt
    except Exception:
        pass
    return None


def baixar_artigo(titulo):
    for wiki in WIKIS:
        print(f"   [{wiki['nome']}]", end=' ', flush=True)

        conteudo = tentar_extracts(wiki, titulo)
        titulo_real = titulo

        if not conteudo:
            print("buscando...", end=' ', flush=True)
            titulos = buscar_titulos(wiki, titulo, limite=3)
            if titulos:
                for t in titulos:
                    print(f"[{t}]", end=' ', flush=True)
                    conteudo = tentar_extracts(wiki, t)
                    if conteudo:
                        titulo_real = t
                        break

        if not conteudo and titulo_real != titulo:
            conteudo = tentar_parse(wiki, titulo_real)

        if conteudo:
            print(f"OK ({len(conteudo)} chars)")
            if len(conteudo) > 4000:
                conteudo = conteudo[:4000].rsplit('.', 1)[0] + '.'
            return {
                'titulo': titulo,
                'titulo_real': titulo_real,
                'conteudo': conteudo,
                'idioma': wiki['idioma'],
                'fonte': wiki['nome']
            }
        else:
            print('vazio')

    return None


def _traduzir_pedaco(pedaco):
    for tentativa in range(3):
        try:
            url = 'https://translate.googleapis.com/translate_a/single'
            params = {'client': 'gtx', 'sl': 'en', 'tl': 'pt', 'dt': 't', 'q': pedaco}
            r = requests.get(url, params=params, headers=HEADERS, timeout=20)

            if r.status_code == 429:
                espera = 5 * (tentativa + 1)
                print(f'\n   [429] esperando {espera}s...', end=' ', flush=True)
                time.sleep(espera)
                continue

            if r.status_code != 200:
                time.sleep(2)
                continue

            dados = r.json()
            return ''.join(parte[0] for parte in dados[0] if parte[0])

        except Exception as e:
            print(f'\n   [tent {tentativa+1}: {e}]', end=' ', flush=True)
            time.sleep(2)
    return None


def traduzir_en_pt(texto):
    if not texto:
        return texto
    if len(texto) <= 3000:
        resultado = _traduzir_pedaco(texto)
        return resultado if resultado else texto

    pedacos = []
    restante = texto
    while len(restante) > 0:
        if len(restante) <= 3000:
            pedacos.append(restante)
            break
        corte = restante[:3000].rfind('. ')
        if corte < 1000:
            corte = restante[:3000].rfind(' ')
        if corte < 500:
            corte = 3000
        pedacos.append(restante[:corte + 1])
        restante = restante[corte + 1:].lstrip()

    traduzidos = []
    for pedaco in pedacos:
        t = _traduzir_pedaco(pedaco)
        if t:
            traduzidos.append(t)
        else:
            traduzidos.append(pedaco)
        time.sleep(0.8)
    return '\n\n'.join(traduzidos)


def main():
    limpar = '--limpar' in sys.argv
    forcar = '--forcar' in sys.argv
    retry = '--retry' in sys.argv
    relatorio = '--relatorio' in sys.argv

    if limpar and os.path.exists(ARQUIVO_LOCAL):
        os.remove(ARQUIVO_LOCAL)
        print('[--limpar] Cache removido.')

    local = carregar_local()

    if relatorio:
        print('=' * 60)
        print('  RELATÓRIO DE ARTIGOS')
        print('=' * 60)
        print(f'  Total baixados: {len(local)}')
        em_pt = sum(1 for v in local.values() if v.get('idioma') == 'pt')
        em_en = sum(1 for v in local.values() if v.get('idioma') == 'en')
        print(f'  Em português:   {em_pt}')
        print(f'  Em inglês:      {em_en}')

        faltando = [a for a in ARTIGOS if not ja_tem_artigo(local, a)]
        print(f'  Não baixados:   {len(faltando)}')

        print('\n  Artigos em inglês:')
        for chave, info in local.items():
            if info.get('idioma') == 'en':
                print(f'    - {info.get("titulo", chave)}')

        if faltando:
            print('\n  Não baixados:')
            for f in faltando:
                print(f'    - {f}')
        return

    if retry:
        pendentes = [k for k, v in local.items() if v.get('idioma') == 'en']
        if not pendentes:
            print('Nada para retraduzir.')
            return
        print(f'Retraduzindo {len(pendentes)} artigos...\n')
        for i, chave in enumerate(pendentes, 1):
            info = local[chave]
            print(f'[{i}/{len(pendentes)}] {info.get("titulo", chave)}')
            traduzido = traduzir_en_pt(info.get('conteudo', ''))
            if traduzido.strip() != info.get('conteudo', '').strip():
                info['conteudo'] = traduzido
                info['idioma'] = 'pt'
                print('   OK')
            else:
                print('   falhou')
            time.sleep(1)
            if i % 5 == 0:
                salvar_local(local)
        salvar_local(local)
        print('\nConcluído.')
        return

    print('=' * 60)
    print('  CORTANA - DOWNLOAD DA WIKI LOCAL')
    print('=' * 60)
    print(f'  Artigos na lista: {len(ARTIGOS)}')
    print(f'  Já baixados: {len(local)}')

    if forcar:
        faltando = ARTIGOS
    else:
        faltando = [a for a in ARTIGOS if not ja_tem_artigo(local, a)]

    print(f'  A baixar: {len(faltando)}')
    print('=' * 60)
    print()

    if not faltando:
        print('Tudo já foi baixado.')
        return

    inicio = time.time()
    sucessos = 0
    falhas = 0
    pulados = 0
    falhas_lista = []

    for i, titulo in enumerate(faltando, 1):
        print(f'\n[{i}/{len(faltando)}] {titulo}')

        local = carregar_local()
        if ja_tem_artigo(local, titulo):
            print('   [já tem, pulando]')
            pulados += 1
            continue

        try:
            dados = baixar_artigo(titulo)
        except KeyboardInterrupt:
            print('\n\n[!] Interrompido. Salvando...')
            salvar_local(local)
            return
        except Exception as e:
            print(f'   ERRO: {e}')
            dados = None

        if dados:
            if dados['idioma'] == 'en':
                print('   traduzindo...', end=' ', flush=True)
                try:
                    traduzido = traduzir_en_pt(dados['conteudo'])
                    if traduzido.strip() != dados['conteudo'].strip():
                        dados['conteudo'] = traduzido
                        dados['idioma'] = 'pt'
                        print('OK')
                    else:
                        print('falhou (mantendo EN)')
                except Exception as e:
                    print(f'ERRO: {e}')

            local[chave_artigo(titulo)] = dados
            sucessos += 1
            if i % 3 == 0:
                salvar_local(local)
        else:
            falhas += 1
            falhas_lista.append(titulo)

        time.sleep(0.4)

    salvar_local(local)

    if falhas_lista:
        with open(ARQUIVO_FALHAS, 'w', encoding='utf-8') as arq:
            arq.write('\n'.join(falhas_lista))

    duracao = time.time() - inicio
    print('\n' + '=' * 60)
    print('  DOWNLOAD CONCLUÍDO')
    print('=' * 60)
    print(f'  Sucessos: {sucessos}')
    print(f'  Pulados:  {pulados}')
    print(f'  Falhas:   {falhas}')
    print(f'  Total:    {len(local)} artigos em wiki_local.json')
    print(f'  Tempo:    {duracao:.1f} segundos')
    if os.path.exists(ARQUIVO_LOCAL):
        print(f'  Tamanho:  {os.path.getsize(ARQUIVO_LOCAL) / 1024 / 1024:.2f} MB')
    print('=' * 60)


if __name__ == '__main__':
    main()
