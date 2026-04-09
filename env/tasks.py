from dataclasses import dataclass
from typing import Callable, Dict, List

from .graders import grade_anomaly, grade_category, grade_extraction, _clamp_open_unit


@dataclass(frozen=True)
class TaskDefinition:
	id: str
	name: str
	difficulty: str
	description: str
	grader: Callable[..., float]
	graders: List[Callable[..., float]]


TASKS: List[TaskDefinition] = [
	TaskDefinition(
		id="field_extraction",
		name="Field Extraction",
		difficulty="easy",
		description="Extract vendor_name and invoice_date from invoice text.",
		grader=grade_extraction,
		graders=[grade_extraction],
	),
	TaskDefinition(
		id="expense_categorization",
		name="Expense Categorization",
		difficulty="medium",
		description="Classify invoice into Travel, Office Supplies, Utilities, or Misc.",
		grader=grade_category,
		graders=[grade_category],
	),
	TaskDefinition(
		id="anomaly_detection",
		name="Anomaly Detection",
		difficulty="hard",
		description="Flag duplicates and unusually high amount invoices.",
		grader=grade_anomaly,
		graders=[grade_anomaly],
	),
]


def compute_weighted_reward(
    extraction_score: float,
    category_score: float,
    anomaly_score: float,
    *,
    missing_fields: int,
    false_anomaly: bool,
    missed_anomaly: bool,
) -> Dict[str, float]:
    """Combine task scores with penalties into a final bounded score."""
    # Clamp each task score individually
    extraction_score = _clamp_open_unit(extraction_score)
    category_score = _clamp_open_unit(category_score)
    anomaly_score = _clamp_open_unit(anomaly_score)

    base = 0.4 * extraction_score + 0.3 * category_score + 0.3 * anomaly_score

    penalty = 0.0
    penalty += 0.08 * missing_fields
    penalty += 0.12 if false_anomaly else 0.0
    penalty += 0.15 if missed_anomaly else 0.0

    final_score = _clamp_open_unit(base - penalty)
    return {
        "base_score": base,
        "penalty": penalty,
        "final_score": final_score,
    }