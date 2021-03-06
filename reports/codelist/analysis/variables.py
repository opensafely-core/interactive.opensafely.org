import argparse
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--start-date")
parser.add_argument("--end-date")
parser.add_argument("--output-dir", type=Path)
parser.add_argument("--low-count-threshold", default=100, type=int)
parser.add_argument("--rounding-base", default=10, type=int)
parser.add_argument("--rounding-base-practice-count", default=5, type=int)

args = parser.parse_args()

args.release_dir = args.output_dir / "for_release"

# minimum viable conversion from cli args to module variables
locals().update(vars(args))


if __name__ == "__main__":
    print(args)
