# -*- coding: utf-8 -*-
# wiki_buscar.py - Consulta local primeiro, depois internet

import requests
import re
import os
import json
import time
import html as html_module
from personalidade import montar_resposta
from dicionario_pt import aplicar_dicionario
import wiki_local

HEADERS = {
    'User-Agent': 'CortanaChatbot/1.0 (projeto pessoal de fã)'
}

WIKIS = [
    {'nome': 'fandom_pt',    'api': 'https://pt-br.halo.fandom.com/api.php', 'idioma': 'pt'},
    {'nome': 'fandom_en',    'api': 'https://halo.fandom.com/api.php',       'idioma': 'en'},
    {'nome': 'halopedia',    'api': 'https://www.halopedia.org/api.php',     'idioma': 'en'},
    {'nome': 'wikipedia_pt', 'api': 'https://pt.wikipedia.org/w/api.php',    'idioma': 'pt'},
    {'nome': 'wikipedia_en', 'api': 'https://en.wikipedia.org/w/api.php',    'idioma': 'en'},
]

CACHE_FILE = 'cache_wiki.json'
CACHE_TTL = 86400
LIMITE_CHARS = 2600

SECOES_IGNORAR = [
    'design do personagem', 'design', 'produção', 'desenvolvimento',
    'recepção', 'críticas', 'curiosidades', 'trivia', 'galeria',
    'referências', 'notas', 'ver também', 'links externos', 'fontes',
    'jogabilidade', 'dublagem', 'vozes', 'merchandise', 'prêmios',
    'development', 'production', 'reception', 'gallery', 'references',
    'notes', 'see also', 'external links', 'behind the scenes'
]


def carregar_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def salvar_cache(cache):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[cache] Erro: {e}")


def traduzir_en_pt(texto):
    if not texto:
        return texto
    try:
        pedaco = texto[:4500]
        url = 'https://translate.googleapis.com/translate_a/single'
        params = {'client': 'gtx', 'sl': 'en', 'tl': 'pt', 'dt': 't', 'q': pedaco}
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        dados = r.json()
        return ''.join(parte[0] for parte in dados[0] if parte[0])
    except Exception as e:
        print(f"[traduzir EN->PT] Erro: {e}")
        return texto


def buscar_artigos_online(termo, limite=3):
    cache = carregar_cache()
    agora = time.time()
    resultados = []

    for wiki in WIKIS:
        chave = f"busca::{wiki['nome']}::{termo.lower()}"

        if chave in cache:
            entrada = cache[chave]
            if agora - entrada.get('timestamp', 0) < CACHE_TTL:
                resultados.extend(entrada.get('resultados', []))
                continue

        params = {
            'action': 'query', 'list': 'search', 'srsearch': termo,
            'srlimit': limite, 'format': 'json', 'origin': '*'
        }

        try:
            r = requests.get(wiki['api'], params=params, headers=HEADERS, timeout=8)
            if r.status_code != 200:
                continue

            dados = r.json()
            encontrados = []
            for item in dados.get('query', {}).get('search', []):
                encontrados.append({
                    'wiki': wiki['nome'],
                    'idioma': wiki['idioma'],
                    'titulo': item['title'],
                    'pageid': item.get('pageid')
                })

            print(f"[buscar {wiki['nome']}] '{termo}' -> {len(encontrados)}")
            cache[chave] = {'timestamp': agora, 'resultados': encontrados}
            resultados.extend(encontrados)

        except Exception as e:
            print(f"[buscar {wiki['nome']}] Erro: {e}")

    salvar_cache(cache)
    return resultados


def tentar_extracts(wiki, titulo):
    params = {
        'action': 'query', 'prop': 'extracts', 'titles': titulo,
        'format': 'json', 'explaintext': 1, 'redirects': 1, 'origin': '*'
    }
    try:
        r = requests.get(wiki['api'], params=params, headers=HEADERS, timeout=10)
        dados = r.json()
        for pid, pagina in dados.get('query', {}).get('pages', {}).items():
            if 'extract' in pagina and pagina['extract'].strip():
                txt = limpar_texto_wiki(pagina['extract'])
                if txt and len(txt) > 50:
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
        r = requests.get(wiki['api'], params=params, headers=HEADERS, timeout=10)
        dados = r.json()
        if 'error' in dados:
            return None
        html = dados.get('parse', {}).get('text', {}).get('*', '')
        if html:
            txt = limpar_html_para_texto(html)
            if txt and len(txt) > 50:
                return txt
    except Exception:
        pass
    return None


def tentar_revisions(wiki, titulo):
    params = {
        'action': 'query', 'prop': 'revisions', 'titles': titulo,
        'rvprop': 'content', 'rvslots': 'main', 'format': 'json',
        'redirects': 1, 'origin': '*'
    }
    try:
        r = requests.get(wiki['api'], params=params, headers=HEADERS, timeout=10)
        dados = r.json()
        for pid, pagina in dados.get('query', {}).get('pages', {}).items():
            revs = pagina.get('revisions', [])
            if revs:
                wikitext = revs[0].get('slots', {}).get('main', {}).get('*', '')
                if wikitext:
                    txt = limpar_wikitext(wikitext)
                    if txt and len(txt) > 50:
                        return txt
    except Exception:
        pass
    return None


def obter_conteudo_online(titulo, wiki_nome):
    wiki = next((w for w in WIKIS if w['nome'] == wiki_nome), None)
    if not wiki:
        return None, None

    conteudo = tentar_extracts(wiki, titulo)
    if not conteudo:
        conteudo = tentar_parse(wiki, titulo)
    if not conteudo:
        conteudo = tentar_revisions(wiki, titulo)

    if not conteudo:
        return None, None

    return conteudo, wiki['idioma']


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


def cortar_em_frase(texto, limite):
    if len(texto) <= limite:
        return texto

    trecho = texto[:limite]
    for i in range(len(trecho) - 1, max(0, len(trecho) - 400), -1):
        if trecho[i] in '.!?':
            if i + 1 >= len(trecho) or trecho[i + 1] in ' \n':
                return trecho[:i + 1].strip()

    espaco = trecho.rfind(' ')
    if espaco > 0:
        return trecho[:espaco].strip() + '...'
    return trecho.strip() + '...'


def tem_internet():
    try:
        requests.get('https://www.google.com', timeout=3)
        return True
    except Exception:
        return False


def buscar_e_responder(pergunta, rampancy_pct=0):
    print(f"\n{'='*50}")
    print(f"[buscar_e_responder] Pergunta: {pergunta}")
    print(f"{'='*50}")

    # 1. LOCAL primeiro
    local = wiki_local.buscar_local(pergunta)
    if local:
        print(f"[LOCAL] '{local.get('titulo')}' ({local.get('fonte')})")
        conteudo = local.get('conteudo', '')
        conteudo = aplicar_dicionario(conteudo)
        conteudo = cortar_em_frase(conteudo, LIMITE_CHARS)
        return montar_resposta(local.get('titulo', '?'), conteudo, pergunta, rampancy_pct)

    # 2. ONLINE
    if not tem_internet():
        print("[OFFLINE] Sem internet e nada no wiki_local.json")
        return ("Não tenho esse registro nos arquivos locais, e não há conexão "
                "com a rede da ONI no momento. Tente outra pergunta, Spartan.")

    print("[ONLINE] Buscando nas wikis...")
    resultados = buscar_artigos_online(pergunta, limite=3)

    if not resultados:
        return ("Não encontrei nada sobre isso nos arquivos da ONI. "
                "Reformule a pergunta ou tente termos mais específicos.")

    resultados.sort(key=lambda r: 0 if r['idioma'] == 'pt' else 1)

    for r in resultados:
        print(f"[tentando] '{r['titulo']}' em {r['wiki']} ({r['idioma']})")
        conteudo, idioma = obter_conteudo_online(r['titulo'], r['wiki'])

        if not conteudo:
            continue

        if idioma == 'en':
            print("[traduzindo] EN -> PT")
            conteudo = traduzir_en_pt(conteudo)

        conteudo = aplicar_dicionario(conteudo)
        conteudo = cortar_em_frase(conteudo, LIMITE_CHARS)

        return montar_resposta(r['titulo'], conteudo, pergunta, rampancy_pct)

    return ("Encontrei registros, mas os arquivos estão corrompidos. "
            "Tente reformular a pergunta, Spartan.")
