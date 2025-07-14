FROM ubuntu:24.04

LABEL maintainer="juliotorres"

RUN apt-get update && \
    apt-get install -y \
    adduser \
    ca-certificates \
    golang-go \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app
COPY go.mod /app
COPY go.sum /app
WORKDIR /app
RUN go mod download

COPY *.go /app

RUN go build -o /app/main
RUN rm -rf /app/*.go
RUN chown -R ubuntu:ubuntu /app && chmod -R 755 /app

RUN chmod +x /app/main

USER ubuntu

EXPOSE 8080

ENTRYPOINT [ "/app/main" ]
