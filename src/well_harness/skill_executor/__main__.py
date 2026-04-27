"""Make the package executable as `python -m well_harness.skill_executor`."""

from well_harness.skill_executor.cli import main


if __name__ == "__main__":
    import sys
    sys.exit(main())
