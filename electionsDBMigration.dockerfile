FROM python:3

RUN mkdir -p /opt/src/elections
WORKDIR /opt/src/elections

COPY elections ./

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./migrate.py"]