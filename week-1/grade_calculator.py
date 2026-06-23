def validate_scores(scores: list[float]) -> None:
  """Validate that scores is non-empty and all values are between 0 and 100.

  Raises:
    ValueError: If scores is empty or contains a value outside 0-100.
  """
  if not scores:
    raise ValueError("scores must not be empty")

  for score in scores:
    if score < 0:
      raise ValueError(f"score {score} is below the minimum of 0")
    if score > 100:
      raise ValueError(f"score {score} is above the maximum of 100")


def calculate_grade(name: str, scores: list[float]) -> dict:
  """Calculate a student's average score and letter grade from a list of scores.

  Args:
    name: The student's name.
    scores: Numeric scores between 0 and 100 (inclusive).

  Returns:
    A dict with the student's name, average score, and letter grade.

  Raises:
    ValueError: If scores is empty or any score is outside 0-100.
  """
  validate_scores(scores)

  average = sum(scores) / len(scores)

  if average >= 90:
    letter = "A"
  elif average >= 80:
    letter = "B"
  elif average >= 70:
    letter = "C"
  elif average >= 60:
    letter = "D"
  else:
    letter = "F"

  return {"name": name, "average": average, "letter": letter}
