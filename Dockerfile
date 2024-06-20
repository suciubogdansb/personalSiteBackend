FROM python:3.11.3-bullseye

WORKDIR /api

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip setuptools

COPY ./requirements.txt /api/requirements.txt

RUN pip install -r requirements.txt

COPY . /api
EXPOSE 8000
ENV LISTEN_PORT=8000
CMD ["uvicorn", "main:socketApp", "--host=0.0.0.0", "--port=8000", "--workers=4"]