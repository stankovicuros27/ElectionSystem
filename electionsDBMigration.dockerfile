FROM python:3

RUN mkdir -p /opt/src/elections
WORKDIR /opt/src/elections

COPY elections/migrate.py ./migrate.py
COPY elections/configuration.py ./configuration.py
COPY elections/models.py ./models.py
COPY elections/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
RUN rm -rf ./migrations

ENTRYPOINT ["python", "./migrate.py"]