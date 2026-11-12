"""Command-line entry point for the Tem Shop application."""

from main import create_app


def main():
    app = create_app()
    app.run(host="127.0.0.1", port=8080, debug=False)


if __name__ == "__main__":
    main()
