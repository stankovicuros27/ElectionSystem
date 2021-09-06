from datetime import timedelta
import os

#databaseUrl = os.environ["DATABASE_URL"]

class Configuration():
    #SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/authentication"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost/authentication"
    JWT_SECRET_KEY = "#v3ry@s3cr3T@k3y@#"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours = 1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days = 30)