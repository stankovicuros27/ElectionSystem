FROM python:3

RUN mkdir -p /opt/src/admin
WORKDIR /opt/src/admin

COPY elections ./elections

RUN pip install -r ./elections/requirements.txt
ENTRYPOINT ["python", "./elections/admin/application.py"]