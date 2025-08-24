import uvicorn
import typer
from typing import Optional
from src.api.server import app as fastapi_app
from .cli.main import app as cli_app

# Main entry point for both API and CLI
def main():
    """Main entry point"""
    cli_app()

if __name__ == "__main__":
    main()