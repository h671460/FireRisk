#!/bin/bash

export PYTHONPATH=$(pwd)
set -a
source .env.vm
set +a
echo "✅ env variables loaded from .env.vm"