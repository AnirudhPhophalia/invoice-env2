from env.graders import grade_category


def test_grade_category_close_guess_scores_half() -> None:
    invoice = {"category": "Travel"}
    score = grade_category("Misc", invoice)
    assert score == 0.5


def test_grade_category_top2_contains_truth_scores_half() -> None:
    invoice = {"category": "Utilities"}
    score = grade_category("Travel|Utilities", invoice)
    assert score == 0.5


def test_grade_category_top1_truth_scores_one() -> None:
    invoice = {"category": "Office Supplies"}
    score = grade_category("Office Supplies|Misc", invoice)
    assert score == 0.99


def test_grade_category_incorrect_scores_zero() -> None:
    invoice = {"category": "Utilities"}
    score = grade_category("Travel", invoice)
    assert score == 0.01
