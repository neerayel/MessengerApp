FROM python:3.11-slim

WORKDIR /msg_app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["./SERVER_STARTER"]
