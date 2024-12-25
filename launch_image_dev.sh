#!/bin/sh
export PORT_DOCKER=8000

docker run -it --name api_market_research -v ${PWD}/src:/src -p $PORT_DOCKER:$PORT_DOCKER --entrypoint /bin/bash publicismarketresearch:V0
