from flask import Flask, request, Response, jsonify
from redis import Redis
from elections.models import database
from elections.configuration import Configuration

while True:
    with Redis(host = Configuration.REDIS_HOST) as redis:
        while True:
            bytes = redis.lpop(Configuration.REDIS_LIST)
            vote = bytes.decode("utf-8")
            print(vote)