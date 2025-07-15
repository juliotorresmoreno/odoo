#!/bin/bash

set -e

envsubst </odoo/odoo.conf.template >/odoo/odoo.conf

# Ejecutar como usuario odoo y activar entorno virtual
source /venv/bin/activate
./odoo-bin --config=/odoo/odoo.conf
