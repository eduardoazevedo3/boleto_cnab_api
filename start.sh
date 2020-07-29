#!/bin/bassh
docker build -t akretion/boleto_api .
docker run --name boleto_api --network docker_default --restart always -d akretion/boleto_api
