import logging

import typer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer(result_callback=lambda x: logger.info("CLI command finished"))


@app.callback()
def main(ctx: typer.Context):
    logger.info(f"Starting CLI command {ctx.invoked_subcommand}")
