import os

databaseUrl = os.environ["DATABASE_URL"]
#redisHost = os.environ["REDIS_HOST"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/elections"
    #SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost:3307/elections"
    JWT_SECRET_KEY = "verisikretkij"
    #REDIS_HOST = redisHost
    REDIS_LIST = "redis_voting_list"