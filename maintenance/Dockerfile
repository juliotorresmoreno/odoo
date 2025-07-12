FROM ubuntu:24.04

LABEL maintainer="juliotorres"

RUN apt-get update && \
    apt-get install -y \
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

RUN chmod +x /app/main

EXPOSE 8080

ENTRYPOINT [ "/app/main" ]