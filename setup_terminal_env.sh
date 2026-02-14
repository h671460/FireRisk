#!/bin/bash

# source .venv/source/activate

set -a
source .env.postgres
set +a

echo "✅ env variables loaded from .env.postgres"


set -a
source .env.timescale
set +a
echo "✅ env variables loaded from .env.timescale"