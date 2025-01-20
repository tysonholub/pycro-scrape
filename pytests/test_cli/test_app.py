from unittest.mock import Mock, call, patch

from typer import Context

from pycro_scrape.cli import app


def test_app_commands():
    assert [x.name for x in app.registered_commands] == []


@patch("pycro_scrape.cli.logger")
def test_app_callbacks(mock_log):
    ctx = Mock(spec=Context, invoked_subcommand="test-callback")
    app.registered_callback.callback(ctx)
    app.info.result_callback(ctx)
    assert mock_log.info.call_args_list == [
        call("Starting CLI command test-callback"),
        call("CLI command finished"),
    ]
