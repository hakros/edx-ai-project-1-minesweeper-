FROM python:3.11-bookworm
WORKDIR /app
COPY . .
RUN apt-get update
RUN apt-get install python3-pygame -y
RUN python3 -m pip install pygame

ENV DISPLAY=host.docker.internal:0.0

CMD ["/usr/local/bin/python3", "runner.py"]
