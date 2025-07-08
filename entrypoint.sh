#!/bin/bash

set -e

chown -R odoo:odoo /var/lib/odoo

# Ejecutar como usuario odoo y activar entorno virtual
exec gosu odoo bash -c "source /venv/bin/activate && ./odoo-bin --config=/odoo/odoo.conf"
