#!/bin/bash
set -e
echo "updating configuration"
sed -i "s|host = 127.0.0.1|host = 127.0.0.1|;" "/src/configurations/models/mongo-config-local.ini"
echo "updated config.. running app"
exec "$@"
