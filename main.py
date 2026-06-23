#!/usr/bin/env python3
"""Interactive grade calculator CLI."""

import argparse
import sys

from grade_calculator import (
    Category,
    calculate_weighted_grade,
    letter_grade,
    score_needed,
)


def parse_category(value: str) -> Category:
  """
  Parse a category from NAME:WEIGHT:SCORE or NAME:WEIGHT:SCORE:MAX.

  Weight is a fraction (e.g. 0.25 for 25%). Score and max are raw points.
  """
  parts = value.split(":")
  if len(parts) not in (3, 4):
    raise argparse.ArgumentTypeError(
        "Expected NAME:WEIGHT:SCORE or NAME:WEIGHT:SCORE:MAX"
    )

  name, weight_text, score_text = parts[0], parts[1], parts[2]
  max_text = parts[3] if len(parts) == 4 else "100"

  try:
    weight = float(weight_text)
    score = float(score_text)
    max_score = float(max_text)
  except ValueError as exc:
    raise argparse.ArgumentTypeError("Weight, score, and max must be numbers") from exc

  return Category(name=name, weight=weight, score=score, max_score=max_score)


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
      description="Calculate weighted course grades and letter grades."
  )
  parser.add_argument(
      "-c",
      "--category",
      action="append",
      type=parse_category,
      metavar="NAME:WEIGHT:SCORE[:MAX]",
      help="Graded category (repeatable). Weight is a fraction, e.g. 0.30",
  )
  parser.add_argument(
      "--target",
      type=float,
      metavar="PERCENT",
      help="Target course percentage (e.g. 90 for an A-)",
  )
  parser.add_argument(
      "--remaining-weight",
      type=float,
      metavar="FRACTION",
      help="Fraction of course weight still ungraded (e.g. 0.25 for final exam)",
  )
  return parser


def main(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)

  if not args.category:
    parser.print_help()
    return 1

  categories = args.category
  percentage = calculate_weighted_grade(categories)
  grade = letter_grade(percentage)

  print(f"Current grade: {percentage:.2f}% ({grade})")
  print()
  print("Breakdown:")
  for category in categories:
    normalized = category.normalized_score()
    contribution = normalized * category.weight
    print(
        f"  {category.name}: "
        f"{category.score}/{category.max_score} "
        f"({normalized:.2f}%) "
        f"x {category.weight:.0%} "
        f"= {contribution:.2f} pts"
    )

  if args.target is not None:
    if args.remaining_weight is None:
      print(
          "\nProvide --remaining-weight to calculate the score needed "
          "on remaining work.",
          file=sys.stderr,
      )
      return 1

    needed = score_needed(categories, args.remaining_weight, args.target)
    target_letter = letter_grade(args.target)
    print()
    print(
        f"To reach {args.target:.2f}% ({target_letter}), "
        f"you need {needed:.2f}% on the remaining "
        f"{args.remaining_weight:.0%} of the course."
    )
    if needed > 100:
      print("That target is not achievable with the current grades.")
    elif needed < 0:
      print("You have already exceeded this target.")

  return 0


if __name__ == "__main__":
  raise SystemExit(main())
