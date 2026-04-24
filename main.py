import logging

from pipeline import run_research_pipeline

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def main():
    topic = input("Enter a topic to research on:\n")
    run_research_pipeline(topic)


if __name__ == "__main__":
    main()
