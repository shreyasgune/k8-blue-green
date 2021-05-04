FROM python:3.8.1-slim-buster

# install system dependencies
RUN apt-get update 

RUN pip install --upgrade pip

COPY app /usr/src/app

WORKDIR /usr/src/app

# Install dependencies:
RUN pip install -r requirements.txt

ARG BLIZZ_VERSION
ENV BLIZZ_VERSION=$BLIZZ_VERSION

EXPOSE 8080

CMD ["python3", "th3-server.py"]
