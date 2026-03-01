FROM python:3.12-slim

WORKDIR /app

# instalar uv
RUN pip install --no-cache-dir uv

# copiar arquivos de dependência
COPY pyproject.toml uv.lock /app/

# instalar dependências
RUN uv sync 

# copiar projeto
COPY . /app

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]