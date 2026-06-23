"""Grade calculator with weighted categories and letter-grade mapping."""

from dataclasses import dataclass


LETTER_GRADES = (
    (93.0, "A"),
    (90.0, "A-"),
    (87.0, "B+"),
    (83.0, "B"),
    (80.0, "B-"),
    (77.0, "C+"),
    (73.0, "C"),
    (70.0, "C-"),
    (67.0, "D+"),
    (63.0, "D"),
    (60.0, "D-"),
    (0.0, "F"),
)


@dataclass(frozen=True)
class Category:
  """A graded component with a weight and earned score."""

  name: str
  weight: float
  score: float
  max_score: float = 100.0

  def normalized_score(self) -> float:
    if self.max_score <= 0:
      raise ValueError(f"max_score must be positive for '{self.name}'")
    return (self.score / self.max_score) * 100.0


def letter_grade(percentage: float) -> str:
  """Convert a percentage to a letter grade."""
  for threshold, grade in LETTER_GRADES:
    if percentage >= threshold:
      return grade
  return "F"


def calculate_weighted_grade(categories: list[Category]) -> float:
  """Return the weighted average percentage across all categories."""
  if not categories:
    raise ValueError("At least one category is required")

  total_weight = sum(category.weight for category in categories)
  if total_weight <= 0:
    raise ValueError("Total weight must be positive")

  weighted_sum = sum(
      category.normalized_score() * category.weight for category in categories
  )
  return weighted_sum / total_weight


def score_needed(
    completed: list[Category],
    remaining_weight: float,
    target_percentage: float,
) -> float:
  """
  Return the percentage score needed on remaining work to reach a target grade.

  remaining_weight is the fraction of the course still ungraded (e.g. 0.30 for 30%).
  """
  if remaining_weight <= 0:
    raise ValueError("remaining_weight must be positive")
  if not 0 <= target_percentage <= 100:
    raise ValueError("target_percentage must be between 0 and 100")

  completed_weight = sum(category.weight for category in completed)
  total_weight = completed_weight + remaining_weight
  if total_weight <= 0:
    raise ValueError("Total weight must be positive")

  completed_points = sum(
      category.normalized_score() * category.weight for category in completed
  )
  needed_points = target_percentage * total_weight
  remaining_points = needed_points - completed_points
  return remaining_points / remaining_weight
