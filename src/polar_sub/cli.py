import typer
from typing_extensions import Annotated

from .api import run_driller

app = typer.Typer()


@app.command()
def drill(
    source: Annotated[str | None, typer.Option("--source", help="source")] = None,
    table_name: Annotated[str, typer.Option("--table-name", help="Table name")] = "x",
):
    run_driller(source=source, table=table_name)


if __name__ == "__main__":
    app()
