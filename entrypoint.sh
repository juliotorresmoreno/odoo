#!/bin/bash

set -e

#!/bin/bash

required_vars=(
  PGUSER
  PGPASSWORD
  PGHOST
  PGPORT
  ODOO_BACKUP_FORMAT
  ODOO_BACKUP_PATH
  ADMIN_PASSWORD
  ADMIN_URL
  WORKERS
  HTTP_PORT
  GEVENT_PORT
  MAX_REQUESTS
  LIMIT_TIME_CPU
  LIMIT_TIME_REAL
  LIMIT_MEMORY_HARD
  LIMIT_MEMORY_SOFT
  LONGPOLLING_INTERVAL
  LOG_LEVEL
  LIST_DB
)

missing=()

for var in "${required_vars[@]}"; do
  val="${!var}"
  if [[ -z "$val" ]]; then
    missing+=("$var")
  fi
done

if [ ${#missing[@]} -ne 0 ]; then
  echo "Faltan variables de entorno obligatorias o están vacías:"
  for v in "${missing[@]}"; do
    echo " - $v"
  done
  exit 1
fi

echo "Todas las variables obligatorias están definidas."


envsubst </odoo/odoo.conf.template >/odoo/odoo.conf

# Ejecutar como usuario odoo y activar entorno virtual
source /venv/bin/activate
./odoo-bin --config=/odoo/odoo.conf
