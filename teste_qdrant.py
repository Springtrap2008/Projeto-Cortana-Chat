import toml
from qdrant_client import QdrantClient

secrets = toml.load(".streamlit/secrets.toml")
url = secrets.get("qdrant_url")
key = secrets.get("qdrant_api_key")

print(f"Conectando a: {url}...")
try:
    client = QdrantClient(url=url, api_key=key, timeout=5)
    # Tenta listar as coleções (se conectar, vai retornar vazio ou com a 'cortana_memoria')
    collections = client.get_collections()
    print("✅ CONEXÃO BEM SUCEDIDA COM O QDRANT!")
    print(collections)
except Exception as e:
    print(f"❌ ERRO AO CONECTAR: {e}")