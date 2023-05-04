docker build -t baterflyrity/flaprunner:3.11 -f dockerfiles/3.11.dockerfile sources
docker build -t baterflyrity/flaprunner:latest -f dockerfiles/latest.dockerfile sources
docker build -t baterflyrity/flaprunner:3.11-docker -f dockerfiles/3.11-docker.dockerfile sources
docker build -t baterflyrity/flaprunner:latest-docker -f dockerfiles/latest-docker.dockerfile sources

docker push baterflyrity/flaprunner:3.11
docker push baterflyrity/flaprunner:latest
docker push baterflyrity/flaprunner:3.11-docker
docker push baterflyrity/flaprunner:latest-docker
