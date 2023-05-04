# Flap Runner

Flap Runner - is job runner service with simple REST web API.

*Currently only linux is supported.*

## Docker image tags

Each tag is created from corresponding `python` image tag, e.g. `baterflyrity/flaprunner:3.11` is based
on `python:3.11`.

Additionally `*-docker` tags contain preinstalled docker client ready to mount to host's docker engine (see below).

All `latest` tags are equivalents of corresponding most recent version tags, e.g. `baterflyrity/flaprunner:latest` is
based on `baterflyrity/flaprunner:3.11` assuming versions *3.12*, *4.0*, e.t.c. do not exist. Latest images **do not**
base on `python:latest`.

## Installation

### With docker compose

1. Install docker.
2. Create projects *registry directory* and cd to it (e.g. `mkdir flaprunner && cd flaprunner`).
3. Create file `docker-compose.yaml` and insert content below:

```yaml
services:
  flaprunner:
    restart: always
    image: baterflyrity/flaprunner
    ports:
      - 39393:39393

    volumes:
      - .:/projects
```

**Alternatively** download default
one: `curl https://raw.githubusercontent.com/baterflyrity/flaprunner/main/tests/docker-compose.yaml > docker-compose.yaml`.

4. Start compose file with `docker compose up -d`.

### With docker container

1. Follow step 1-2 from above.
2. Run docker container: `docker run -d --name flaprunner -v .:/projects -p 39393:39393 baterflyrity/flaprunner`

### With python from sources

1. Install python 3.11: `sudo apt-get update && sudo apt-get install python3.11`. Alternatively install python from
   sources: `sudo apt-get update && sudo apt-get install wget && wget -qO - https://raw.githubusercontent.com/tvdsluijs/sh-python-installer/main/python.sh | sudo bash -s 3.11.3`.
2. Get Flap Runner sources: `git clone https://github.com/baterflyrity/flaprunner.git`.
3. Install required python packages: `python3.11 -m pip install -r flaprunner/sources/requirements.txt`.
4. Run and mount *registry
   directory*: `python3.11 flaprunner/sources/flaprunner.py --projetcs "/path/to/registry/directory"` (`--help` option
   is supported too).

## Usage

1. Create projects (subdirectories) in *registry directory*.
2. Create jobs in project. Each job is an *<project>/.flaprunner/*.sh* file.
3. Call API */run/<project>/<job>* endpoint like `curl http://localhost:39393/run/<project>/<job>`.

Each job is executed with `/bin/sh` from project's root directory.

## Examples

- Simple case is to create git repository with predefined jobs, then clone it to Flap Runner service. Additionally
  defining git pull job is a good idea.
- A logging job can be defined as `echo "cat log.txt" > ./.flaprunner/log.sh` and then executed
  via `curl http://localhost:39393/run/<project>/log`.
- GET query parameter *timeout* can be set as seconds in float. By default, timeout is set top 1 hour (3600).

### Print layout of project

In this simple example we crate one project called `my_project` inside projects *registry directory* called `registry`. Then we define a job called `layout` which prints project's structure.

```bash
mkdir registry
mkdir registry/my_project
mkdir registry/my_project/.flaprunner
echo "ls -a1R" > registry/my_project/.flaprunner/layout.sh
```

Now we start Flap Runner, mount *registry directory* and request job execution.

```bash
docker run -d --name flaprunner -v registry:/projects -p 39393:39393 baterflyrity/flaprunner
curl http://localhost:39393/run/my_project/layout
```
Print results:
> .:  
> .  
> ..  
> .flaprunner  
>   
> ./.flaprunner:  
> .  
> ..  
> layout.sh

### Access docker inside Flap Runner container

This example demonstrates dind (docker in docker) alternative assuming host docker daemon is used. We are going to build
docker image with a job.

Consider docker settings are inherited from host.

1. Mount host daemon volume.

Change startup command *(see Installation)*
to `docker run -d --name flaprunner -v .:/projects -v /var/run/docker.sock:/var/run/docker.sock -p 39393:39393 baterflyrity/flaprunner:latest-docker`
or `docker-compose.yaml` file to:

```yaml
services:
  flaprunner:
    restart: always
    image: baterflyrity/flaprunner:latest-docker
    ports:
      - 39393:39393

    volumes:
      - .:/projects
      - /var/run/docker.sock:/var/run/docker.sock 
```

**Alternatively** download default
one: `curl https://raw.githubusercontent.com/baterflyrity/flaprunner/main/tests/docker-compose-docker.yaml > docker-compose.yaml`.

2. Build (or use anyway) docker image with job `.flaprunner/docker-build.sh`:

```bash
docker version
docker info

echo "Building..."
docker pull ubuntu
docker image tag ubuntu myfirstimage

echo "Done. See image myfirstimage."

```

3. **Don not remember to actually run job.**

```bash
curl http://localhost:39393/run/<project>/docker-build
```
