#!/bin/bash

export PYTHONPATH=$(pwd)
set -a
source .env
set +a
echo "✅ env variables loaded from .env"