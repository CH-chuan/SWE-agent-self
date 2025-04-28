#!/usr/bin/env python

from pathlib import Path
import sys

from sweagent.run.run_batch_team import run_team_from_cli


def main():
    """Command entry point."""
    run_team_from_cli(sys.argv[1:])


if __name__ == "__main__":
    main()
