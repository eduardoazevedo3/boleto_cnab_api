#!/bin/bassh
docker build -t akretion/boleto_api .
docker run --name boleto-api --network docker_default --restart always -d akretion/boleto_api
