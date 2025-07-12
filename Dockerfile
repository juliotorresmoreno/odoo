FROM ubuntu:24.04

RUN apt-get update && apt dist-upgrade -y && apt-get install -y \
    build-essential \
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

RUN mkdir -p /odoo
WORKDIR /odoo

RUN addgroup --system odoo
RUN adduser --system --ingroup odoo --home /var/lib/odoo --shell /bin/false odoo

COPY requirements.txt /odoo/requirements.txt

RUN python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip3 install --upgrade pip setuptools wheel && \
    pip3 install -r requirements.txt

RUN chown -R odoo:odoo /odoo && chmod -R 755 /odoo
USER odoo

COPY . /odoo

USER root
RUN chmod +x /odoo/entrypoint.sh

USER odoo
ENTRYPOINT ["/odoo/entrypoint.sh"]

EXPOSE 8069
EXPOSE 8072
