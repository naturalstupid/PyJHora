# JHoraWeb on Render (free web service). Put this file in the PySSHora repo root.
FROM python:3.13

ENV PYTHONUNBUFFERED=1 \
    CMAKE_POLICY_VERSION_MINIMUM=3.5 \
    JHORA_PUBLIC=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# 1. Dependencies (cached unless requirements-web.txt changes)
COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

# 2. Ephemeris files: not in the PySSHora repo, so take them from public PyJHora
RUN git clone --depth 1 https://github.com/naturalstupid/PyJHora.git /tmp/pyjhora \
 && mkdir -p /app/src/jhora/data \
 && cp -r /tmp/pyjhora/src/jhora/data/ephe /app/src/jhora/data/ \
 && rm -rf /tmp/pyjhora

# 3. Your code
COPY . .

WORKDIR /app/src/jhora/ui/nicegui
# main.py reads PORT (Render sets it) and STORAGE_SECRET (set in Render dashboard)
CMD ["python", "main.py"]
