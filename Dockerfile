FROM ubuntu:24.04

RUN apt-get update && apt dist-upgrade -y && apt-get install -y \
    build-essential \
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

COPY . /odoo
WORKDIR /odoo

RUN python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip3 install --upgrade pip setuptools wheel && \
    pip3 install -r requirements.txt

RUN chmod +x /odoo/entrypoint.sh

RUN addgroup --system odoo
RUN adduser --system --ingroup odoo --home /var/lib/odoo --shell /bin/false odoo
RUN chown -R odoo:odoo /odoo && \
    chown -R odoo:odoo /var/lib/odoo && \
    chmod 755 /odoo/entrypoint.sh

ENTRYPOINT ["/odoo/entrypoint.sh"]

EXPOSE 8069
