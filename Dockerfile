# Usa uma imagem oficial do Python, leve.
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container.
WORKDIR /app

# Instala as dependências do sistema.
# 'build-essential' pode ser necessário para compilar algumas bibliotecas Python.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências e instala.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do projeto para dentro do container.
COPY . .

# Cria o diretório /data que será usado para o armazenamento persistente.
RUN mkdir -p /data

# Expõe a porta que o Hugging Face Spaces espera (7860).
EXPOSE 7860

# Comando para iniciar a aplicação.
# Usamos Gunicorn, que é um servidor de produção, em vez do servidor de desenvolvimento do Flask.
# O 'app:app' refere-se ao objeto 'app' dentro do arquivo 'app.py'.
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
