"""Allow `python -m ai_sdlc` when the console script is not on PATH."""

from ai_sdlc.cli.main import app

if __name__ == "__main__":
    app()
