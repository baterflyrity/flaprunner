FROM python:3.11

LABEL author="baterflyrity"
LABEL mail="baterflyrity@yandex.ru"
LABEL home="https://github.com/baterflyrity/flaprunner"
LABEL version="1.2.0"
LABEL description="Flap Runner - is job runner service with simple REST web API."

COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir --quiet -r requirements.txt  && mkdir /projects
EXPOSE 39393
ENTRYPOINT ["python", "flaprunner.py"]
CMD ["--projects", "/projects"]
