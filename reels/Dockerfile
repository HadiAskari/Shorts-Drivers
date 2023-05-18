# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.7-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set current directory as ENV
ENV PATH=/app:$PATH

# Needed for tzdata
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Los_Angeles

# set working directory
WORKDIR /app

# Install pre-dependencies
RUN apt update
RUN apt install -y wget g++ unzip xvfb

# Install chrome
RUN wget http://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_112.0.5615.49-1_amd64.deb
RUN apt install -y ./google-chrome-stable_112.0.5615.49-1_amd64.deb

# Download chromedriver
RUN wget https://chromedriver.storage.googleapis.com/112.0.5615.49/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip

# copy items
COPY accounts.json ./
COPY credentials.json ./
COPY css-classes.json ./
COPY helpers.py ./
COPY keywords.json ./
COPY main.py ./
COPY requirements.txt ./
COPY util.py ./
COPY ReelsDriver.py ./

# install python dependencies
RUN pip install -r requirements.txt
