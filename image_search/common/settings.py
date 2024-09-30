from functools import cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    rabbitmq_default_user: str = ""
    rabbitmq_default_pass: str = ""
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    redis_host: str = "localhost"
    redis_port: int = 6379
    mysql_root_password: str = "rootpassword"
    mysql_database: str = "mydatabase"
    mysql_user: str = "myuser"
    mysql_password: str = "mypassword"
    mysql_host: str = "localhost"
    mysql_port: int = 3306

    @property
    def redis_str(self):
        return f"redis://{self.redis_host}:{self.redis_port}"

    @property
    def mq_str(self):
        return (
            f"amqp://{self.rabbitmq_default_user}:{self.rabbitmq_default_pass}@"
            f"{self.rabbitmq_host}:{self.rabbitmq_port}"
        )

    @property
    def db_str(self):
        return (
            f"mysql+asyncmy://{self.mysql_user}:{self.mysql_password}@"
            f"{self.mysql_host}:{self.mysql_port!s}/{self.mysql_database}?charset=utf8mb4"
        )

    @property
    def db_str_alembic(self):
        return (
            f"mysql+mysqlconnector://{self.mysql_user}:{self.mysql_password}@"
            f"{self.mysql_host}:{self.mysql_port!s}/{self.mysql_database}"
        )


@cache
def get_envs():
    return Settings()


ENVS = get_envs()
