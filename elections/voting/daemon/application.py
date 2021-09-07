from flask import Flask, request, Response, jsonify
from redis import Redis
from elections.models import database
from elections.configuration import Configuration

with Redis(host = Configuration.REDIS_HOST) as redis:
    while True:
        vote = redis.lpop(Configuration.REDIS_LIST).decode("utf-8")
        print(vote)