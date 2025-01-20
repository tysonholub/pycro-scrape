#!/bin/bash
set -euo pipefail

curl -sf http://$HOSTNAME:$PORT/health
