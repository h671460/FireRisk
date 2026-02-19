#!/bin/bash

export PYTHONPATH=$(pwd)
set -a
source .env.postgres
set +a

echo "✅ env variables loaded from .env.postgres"


set -a
source .env.timescale
set +a
echo "✅ env variables loaded from .env.timescale"


set -a
source .env.keycloak
set +a
echo "✅ env variables loaded from .env.keycloak"

set -a
source .env.dynamic-frcm
set +a
echo "✅ env variables loaded from .env.dynamic-frcm"