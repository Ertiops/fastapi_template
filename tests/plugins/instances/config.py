import pytest

from app.adapters.database.config import DatabaseConfig
from app.application.config import AppConfig, SecretConfig
from app.controllers.rest.config import RestConfig


@pytest.fixture
def rest_config(db_config: DatabaseConfig) -> RestConfig:
    return RestConfig(
        app=AppConfig(debug=True),
        database=db_config,
        secret=SecretConfig(),
    )
