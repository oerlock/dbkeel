"""Configuration loading and validation without a database driver."""

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from dbkeel.postgres import PostgresSettings
from dbkeel.settings import BaseDBSettings


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in os.environ:
        if name.upper().startswith("DBKEEL_PG_"):
            monkeypatch.delenv(name)


def test_environment_and_explicit_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DBKEEL_PG_CONNINFO", "host=localhost dbname=app")
    monkeypatch.setenv("DBKEEL_PG_MIN_SIZE", "2")
    monkeypatch.setenv("DBKEEL_PG_MAX_SIZE", "12")
    monkeypatch.setenv("DBKEEL_PG_ACQUIRE_TIMEOUT", "2.5")

    settings = PostgresSettings(max_size=20)

    assert isinstance(settings, BaseDBSettings)
    assert settings.conninfo.get_secret_value() == "host=localhost dbname=app"
    assert settings.min_size == 2
    assert settings.max_size == 20
    assert settings.acquire_timeout == 2.5
    assert settings.connect_timeout == 10
    assert settings.startup_timeout == 30.0


def test_dotenv_requires_explicit_selection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "DBKEEL_PG_CONNINFO=host=dotenv\nOTHER_APP_SETTING=ignored\n"
    )
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError):
        PostgresSettings()

    assert (
        PostgresSettings(_env_file=env_file).conninfo.get_secret_value()
        == "host=dotenv"
    )
    monkeypatch.setenv("DBKEEL_PG_CONNINFO", "host=environment")
    assert (
        PostgresSettings(_env_file=env_file).conninfo.get_secret_value()
        == "host=environment"
    )


@pytest.mark.parametrize("conninfo", ["", " \n\t"])
def test_blank_connection_string(conninfo: str) -> None:
    with pytest.raises(ValidationError, match="must not be blank"):
        PostgresSettings(conninfo=conninfo)


@pytest.mark.parametrize(
    "values",
    [
        {"min_size": 0},
        {"max_size": 0},
        {"min_size": 3, "max_size": 2},
        {"connect_timeout": 0},
        {"acquire_timeout": -1},
        {"startup_timeout": 0},
        {"acquire_timeout": float("inf")},
        {"startup_timeout": float("nan")},
    ],
)
def test_invalid_pool_configuration(values: dict[str, int | float]) -> None:
    with pytest.raises(ValidationError):
        PostgresSettings.model_validate({"conninfo": "host=localhost", **values})


def test_secret_is_hidden_and_settings_are_immutable() -> None:
    conninfo = "postgresql://user:private-password@localhost/app"
    settings = PostgresSettings(conninfo=conninfo)
    assert settings.conninfo.get_secret_value() == conninfo
    assert "private-password" not in repr(settings)
    assert "private-password" not in settings.model_dump_json()

    with pytest.raises(ValidationError):
        settings.min_size = 20  # type: ignore[misc]  # Verify runtime immutability.

    with pytest.raises(ValidationError) as exc:
        PostgresSettings(conninfo=conninfo, min_size=20, max_size=1)
    assert "private-password" not in str(exc.value)
