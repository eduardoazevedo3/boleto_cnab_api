#!/bin/bassh
docker build -t akretion/boleto_api .
docker run --name boleto-api --restart always -d akretion/boleto_api
