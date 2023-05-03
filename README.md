# Flap Runner

Flap Runner - is job runner service with simple REST web API.

*Currently only linux is supported.*

## Installation

### With docker compose

1. Install docker.
2. Create projects *registry directory* and cd to it (e.g. `mkdir flaprunner && cd flaprunner`).
3. Create file `docker-compose.yaml` and insert content below:

```yaml
services:
    flaprunner:
        restart: always
        image:   baterflyrity/flaprunner
        ports:
            - 39393:39393

        volumes:
            - .:/projects
```

4. Start compose file with `docker compose up -d`.

### With docker container

1. Follow step 1-2 from above.
2. Run docker container: `docker run -d --name flaprunner -v .:/projects -p 39393:39393 baterflyrity/flaprunner`

## Usage

1. Create projects (subdirectories) in *registry directory*.
2. Create jobs in project. Each job is an *<project>/.flaprunner/*.sh* file.
3. Call API */run/<project>/<job>* endpoint like `curl http://localhost:39393/run/<project>/<job>`.

Each job is executed with `/bin/sh` from project's root directory.

## Examples

- Simple case is to create git repository with predefined jobs, then clone it to Flap Runner service. Additionally defining git pull job is a good idea.
- A logging job can be defined as `echo "cat log.txt" > ./.flaprunner/log.sh` and then executed via `curl http://localhost:39393/run/<project>/log`.
- GET query parameter *timeout* can be set as seconds in float. By default, timeout is set top 1 hour (3600).

### Build docker image inside Flap Runner container

This example demonstrates dind (docker in docker) alternative assuming host docker daemon is used. We are going to build docker image with a job.

Consider docker settings are inherited from host.

1. Mount host daemon volume. Change startup command *(see Installation)* to `docker run -d --name flaprunner -v .:/projects -v /var/run/docker.sock:/var/run/docker.sock -p 39393:39393 baterflyrity/flaprunner` or `docker-compose.yaml` file to:

```yaml
services:
    flaprunner:
        restart: always
        image:   baterflyrity/flaprunner
        ports:
            - 39393:39393

        volumes:
            - .:/projects
            - /var/run/docker.sock:/var/run/docker.sock 
```

2. Install docker client inside Flap Runner container with job `.flaprunner/docker-install.sh`:

```bash
apt-get update
apt-get install ca-certificates curl gnupg
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh
echo "Installed docker."
```

3. Build (or use anyway) docker image with job `.flaprunner/docker-build.sh`:

```bash
docker version
docker info

echo "Building..."
docker pull ubuntu
docker image tag ubuntu myfirstimage

echo "Done. See image myfirstimage."

```
4. **Don not remember to actually run jobs.**
```bash
curl http://localhost:39393/run/<project>/docker-install
curl http://localhost:39393/run/<project>/docker-build
```
