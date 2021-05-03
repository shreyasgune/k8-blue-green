FROM python:3.8.1-slim-buster as builder

# set work directory
WORKDIR /usr/src/app

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

RUN pip install --upgrade pip
COPY . /usr/src/app/

# install python dependencies
COPY requirements.txt .

# Install dependencies:
RUN pip install -r requirements.txt

ARG BLIZZ_VERSION
ENV BLIZZ_VERSION=$BLIZZ_VERSION

EXPOSE 8080

CMD ["python3", "th3-server.py"]