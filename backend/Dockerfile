# ==========================================
# Stage 1: Build & Dependencies
# ==========================================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /install

COPY requirements.txt .

# Install dependencies into /install/packages (pure Python / wheels, no heavy compilers needed)
RUN pip install --no-cache-dir --prefix=/install/packages -r requirements.txt

# ==========================================
# Stage 2: Production Minimal Runner
# ==========================================
FROM python:3.11-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    PORT=8000

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install/packages /usr/local

# Copy application source code
COPY . /app

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
