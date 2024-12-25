#!/bin/sh

export PORT_DOCKER=8000

docker run --name api_market_research -d -p $PORT_DOCKER:$PORT_DOCKER publicismarketresearch:V0
