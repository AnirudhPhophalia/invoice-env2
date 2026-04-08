from __future__ import annotations

from datetime import date, timedelta
from random import Random
from typing import Any, Dict, List


InvoiceRecord = Dict[str, Any]


def _category_from_vendor(vendor_name: str) -> str:
	travel = {"Uber", "Lyft", "Delta Airlines", "Marriott"}
	office = {"Amazon", "Staples", "IKEA Business"}
	utilities = {"Electricity Board", "Water Utility", "Internet Provider", "Gas Company"}

	if vendor_name in travel:
		return "Travel"
	if vendor_name in office:
		return "Office Supplies"
	if vendor_name in utilities:
		return "Utilities"
	return "Misc"


def generate_invoices(num_invoices: int = 72, seed: int = 7) -> List[InvoiceRecord]:
	"""Generate deterministic synthetic invoices with realistic anomalies."""
	if num_invoices < 50 or num_invoices > 100:
		raise ValueError("num_invoices must be between 50 and 100")

	rng = Random(seed)
	vendors = [
		"Amazon",
		"Uber",
		"Electricity Board",
		"Staples",
		"Water Utility",
		"Internet Provider",
		"Lyft",
		"Delta Airlines",
		"Marriott",
		"Gas Company",
		"IKEA Business",
		"Local Services LLC",
	]
	descriptions = [
		"Office chair and desk organizer",
		"Airport transfer ride",
		"Monthly electricity bill",
		"Printer paper and pens",
		"Water services for HQ",
		"Internet subscription renewal",
		"Client meeting transport",
		"Flight ticket for sales visit",
		"Hotel stay during conference",
		"Natural gas utility charge",
		"Workspace furniture purchase",
		"General maintenance service",
	]

	base_date = date(2026, 1, 2)
	invoices: List[InvoiceRecord] = []

	for index in range(num_invoices - 8):
		vendor = vendors[index % len(vendors)]
		invoice_ref = f"INV-{1000 + index}"

		amount = round(rng.uniform(18.0, 950.0), 2)
		invoice_date = (base_date + timedelta(days=index % 60)).isoformat()
		description = descriptions[index % len(descriptions)]
		line_items = [
			{"item": "Primary charge", "quantity": 1, "unit_price": amount},
		]

		invoices.append(
			{
				"id": f"invoice-{index:03d}",
				"invoice_ref": invoice_ref,
				"vendor_name": vendor,
				"invoice_date": invoice_date,
				"amount": amount,
				"description": description,
				"line_items": line_items,
				"category": _category_from_vendor(vendor),
				"anomaly_flag": False,
				"anomaly_type": "none",
			}
		)

	# Create exact duplicates (same key fields) for duplicate anomaly detection.
	duplicate_source_indices = [4, 13, 28, 37]
	for dup_num, source_idx in enumerate(duplicate_source_indices):
		original = invoices[source_idx]
		invoices.append(
			{
				**original,
				"id": f"invoice-dup-{dup_num:02d}",
				"anomaly_flag": True,
				"anomaly_type": "duplicate_invoice",
			}
		)

	# Create unusually high invoices across categories.
	high_vendors = ["Amazon", "Delta Airlines", "Electricity Board", "Local Services LLC"]
	for high_num, vendor in enumerate(high_vendors):
		invoices.append(
			{
				"id": f"invoice-high-{high_num:02d}",
				"invoice_ref": f"INV-HIGH-{high_num:02d}",
				"vendor_name": vendor,
				"invoice_date": (base_date + timedelta(days=70 + high_num)).isoformat(),
				"amount": round(4800 + 900 * high_num + rng.uniform(0, 150), 2),
				"description": "Unexpected one-time bulk charge",
				"line_items": [
					{"item": "Bulk adjustment", "quantity": 1, "unit_price": round(4800 + 900 * high_num, 2)}
				],
				"category": _category_from_vendor(vendor),
				"anomaly_flag": True,
				"anomaly_type": "unusually_high_amount",
			}
		)

	return invoices


def load_invoices() -> List[InvoiceRecord]:
	"""Load the default deterministic dataset used by the environment."""
	return generate_invoices(num_invoices=72, seed=7)
