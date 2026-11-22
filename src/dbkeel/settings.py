"""Shared settings for asynchronous database backends."""

from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseDBSettings(BaseSettings):
    """Common pool settings; values are loaded only when instantiated.

    Subclasses define backend connection fields and an environment prefix.
    Dotenv files must be selected explicitly with ``_env_file``.
    """

    model_config = SettingsConfigDict(
        env_file=None,
        extra="ignore",
        frozen=True,
        hide_input_in_errors=True,
        allow_inf_nan=False,
    )

    min_size: int = Field(default=1, ge=1)
    max_size: int = Field(default=10, ge=1)
    connect_timeout: int = Field(default=10, gt=0)
    acquire_timeout: float = Field(default=30.0, gt=0)
    startup_timeout: float = Field(default=30.0, gt=0)

    @model_validator(mode="after")
    def validate_pool_size(self) -> Self:
        """Reject a pool that cannot accommodate its minimum size."""
        if self.max_size < self.min_size:
            raise ValueError("max_size must be greater than or equal to min_size")
        return self
