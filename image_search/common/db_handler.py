from enum import Enum
from functools import lru_cache
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from image_search.common.settings import ENVS


class EchoLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"


@lru_cache
def get_engine(
    pool_size: int = 10,
    autocommit: bool = True,
    echo_level: Optional[EchoLevel] = None,
) -> AsyncEngine:
    exec_options = {"isolation_level": "AUTOCOMMIT"} if autocommit else {"isolation_level": "READ UNCOMMITTED"}
    echo = {EchoLevel.DEBUG: "debug", EchoLevel.INFO: True, None: False}[echo_level]
    return create_async_engine(
        ENVS.db_str,
        pool_size=pool_size,
        echo=echo,
        execution_options=exec_options,
        connect_args={"init_command": "SET SESSION sql_mode=''"},
    )
