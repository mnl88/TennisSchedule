# syntax=docker/dockerfile:1

FROM python:3.10-alpine
LABEL authors="manile"

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "script.py"]

#FROM ubuntu:latest
#ENTRYPOINT ["top", "-b"]