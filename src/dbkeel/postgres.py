"""PostgreSQL configuration, independent of the optional database driver."""

from pydantic import SecretStr, field_validator
from pydantic_settings import SettingsConfigDict

from dbkeel.settings import BaseDBSettings


class SettingsPG(BaseDBSettings):
    """Load PostgreSQL settings from ``DBKEEL_PG_`` variables.

    ``conninfo`` accepts a libpq URI or keyword/value connection string.
    It is passed unchanged to the driver when a connection is established.
    """

    model_config = SettingsConfigDict(env_prefix="DBKEEL_PG_")

    conninfo: SecretStr

    @field_validator("conninfo")
    @classmethod
    def validate_conninfo(cls, value: SecretStr) -> SecretStr:
        """Require explicit connection information without parsing libpq syntax."""
        if not value.get_secret_value().strip():
            raise ValueError("conninfo must not be blank")
        return value
