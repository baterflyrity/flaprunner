FROM baterflyrity/flaprunner:3.11

LABEL author="baterflyrity"
LABEL mail="baterflyrity@yandex.ru"
LABEL home="https://github.com/baterflyrity/flaprunner"
LABEL version="1.2.0"
LABEL description="Flap Runner - is job runner service with simple REST web API."

RUN apt-get update && \
    apt-get install ca-certificates curl gnupg && \
    curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh
