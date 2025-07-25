FROM ubuntu:24.04

LABEL maintainer="juliotorres"

RUN apt-get update && apt dist-upgrade -y && apt-get install -y \
    build-essential \
    curl \
    gettext \
    gnupg2 \
    gosu \
    libffi-dev \
    libjpeg-dev \
    libldap2-dev \
    libpq-dev \
    libsasl2-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    lsb-release \
    python3-full \
    python3-pip \
    software-properties-common \
    wget && \
    rm -rf /var/lib/apt/lists/*

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt-get update && apt-get install -y postgresql-client-17 wkhtmltopdf && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /odoo
WORKDIR /odoo

COPY requirements.txt /odoo/requirements.txt

RUN python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip3 install --upgrade pip setuptools wheel && \
    pip3 install -r requirements.txt

RUN chown -R ubuntu:ubuntu /odoo && chmod -R 755 /odoo
USER ubuntu

COPY . /odoo

USER root
RUN chmod +x /odoo/entrypoint.sh

USER ubuntu
ENTRYPOINT ["/odoo/entrypoint.sh"]

EXPOSE 8069
EXPOSE 8072
