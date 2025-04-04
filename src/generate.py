import argparse
import os
import sys
from config import parse_config
from worker.orchestrator import ContentCurator


def main():
    parser = argparse.ArgumentParser(description='Process content configuration.')
    parser.add_argument('--config_path', type=str, help='Path to the content config file')
    parser.add_argument('--background', action='store_true', help='Run process in background')

    args = parser.parse_args()
    config = parse_config(args.config_path)
    orchestrator = ContentCurator(config)

    if args.background:
        # also redirect logs to a log file
        sys.stdout = open('content_curator.log', 'w')
        # add error logs to the same file
        sys.stderr = sys.stdout
        pid = os.fork()
        if pid > 0:
            sys.exit()

    orchestrator.logger.info("Starting content curation...")
    orchestrator.curate()
    orchestrator.logger.info("Content curation completed.")


if __name__ == '__main__':
    main()
