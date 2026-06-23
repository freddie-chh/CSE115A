import unittest

from grade_calculator import (
    Category,
    calculate_weighted_grade,
    letter_grade,
    score_needed,
)


class GradeCalculatorTests(unittest.TestCase):
  def test_weighted_grade(self):
    categories = [
        Category("Homework", 0.30, 90),
        Category("Midterm", 0.30, 80),
        Category("Final", 0.40, 95),
    ]
    self.assertAlmostEqual(calculate_weighted_grade(categories), 89.0)

  def test_normalized_max_score(self):
    categories = [Category("Quiz", 1.0, 18, max_score=20)]
    self.assertAlmostEqual(calculate_weighted_grade(categories), 90.0)

  def test_letter_grade_boundaries(self):
    self.assertEqual(letter_grade(93), "A")
    self.assertEqual(letter_grade(92.9), "A-")
    self.assertEqual(letter_grade(60), "D-")
    self.assertEqual(letter_grade(59.9), "F")

  def test_score_needed(self):
    completed = [
        Category("Homework", 0.50, 85),
        Category("Midterm", 0.20, 78),
    ]
    needed = score_needed(completed, remaining_weight=0.30, target_percentage=90)
    self.assertAlmostEqual(needed, 106.33333333333333)

  def test_score_needed_already_met(self):
    completed = [Category("Homework", 0.70, 95)]
    needed = score_needed(completed, remaining_weight=0.30, target_percentage=60)
    self.assertLess(needed, 0)


if __name__ == "__main__":
  unittest.main()
