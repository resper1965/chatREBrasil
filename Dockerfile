# Dockerfile
FROM python:3.11-slim

# Instalar ODBC Driver e PostgreSQL client
# Atualizado para Debian 12+ (apt-key deprecated)
RUN apt-get update && apt-get install -y \
    curl apt-transport-https gnupg2 unixodbc-dev \
    libpq-dev \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && sed -i "s|deb https://packages.microsoft.com|deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com|" /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Criar diretório .chainlit se não existir e copiar config
RUN mkdir -p .chainlit && mkdir -p .chainlit/translations && \
    if [ -f .chainlit/config.toml ]; then \
        echo "Config.toml encontrado, usando arquivo fornecido"; \
    else \
        echo "Config.toml não encontrado, Chainlit criará automaticamente"; \
    fi && \
    if [ -f /app/.chainlit_translations_pt-BR.json ]; then \
        cp /app/.chainlit_translations_pt-BR.json /app/.chainlit/translations/pt-BR.json && \
        echo "pt-BR.json copiado"; \
    else \
        echo "pt-BR.json não encontrado"; \
    fi

EXPOSE 8000

CMD ["chainlit", "run", "app/app.py", "--host", "0.0.0.0", "--port", "8000"]

