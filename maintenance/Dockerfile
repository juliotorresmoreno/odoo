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
RUN addgroup --system odoo
RUN adduser --system --ingroup odoo --home /var/lib/odoo --shell /bin/false odoo

COPY *.go /app

RUN go build -o /app/main
RUN rm -rf /app/*.go
RUN chown -R odoo:odoo /app && chmod -R 755 /app

RUN chmod +x /app/main

USER odoo

EXPOSE 8080

ENTRYPOINT [ "/app/main" ]