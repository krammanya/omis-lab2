"""Entry point for the customer experience review platform."""

from app.ui import ReviewPlatformApp


def main() -> None:
    ReviewPlatformApp().run()


if __name__ == "__main__":
    main()
