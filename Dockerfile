FROM python:3.12-slim

WORKDIR /app

COPY --chown=node:node . .

RUN pip install --no-cache-dir streamlit

EXPOSE 7860

CMD ["streamlit", "run", "streamlit_app/app.py"]
