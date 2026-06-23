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
  if not scores:
    raise ValueError("scores must not be empty")

  for score in scores:
    if score < 0 or score > 100:
      raise ValueError("scores must be between 0 and 100")

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
