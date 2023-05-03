FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir --quiet -r requirements.txt  && mkdir /projects
EXPOSE 39393
ENTRYPOINT ["python", "flaprunner.py"]
CMD ["--projects", "/projects"]
