FROM python:3.11-slim

# Create user with UID 1000 (Required for Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Install python dependencies as user
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application files
COPY --chown=user . $HOME/app

# Hugging Face Spaces requires port 7860
EXPOSE 7860
ENV PORT=7860
ENV HOST=0.0.0.0

# Run FastAPI with uvicorn (compatible with both HF Spaces 7860 and cloud dynamic $PORT)
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}"]
