import os

#databaseUrl = os.environ["DATABASE_URL"]

class Configuration():
    #SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/authentication"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost:3307/elections"
    JWT_SECRET_KEY = "#v3ry@s3cr3T@k3y@#"
    REDIS_HOST = "localhost"
    REDIS_LIST = "redis_voting_list"