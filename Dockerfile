FROM python:3.9-slim
EXPOSE 8080
ENV PYTHONUNBUFFERED 1
ENV APP_DIR /src
ENV SECRETS_DIR /secrets
WORKDIR $APP_DIR

COPY requirements.txt /src/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY src $APP_DIR
COPY secrets $SECRETS_DIR


CMD streamlit run main.py --server.port 8080
