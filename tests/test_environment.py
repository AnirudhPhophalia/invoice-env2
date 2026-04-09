import pytest
from env.environment import InvoiceEnv
from env.models import InvoiceAction


class DummyGraders:
    """Monkeypatch graders to return fixed scores for testing."""
    @staticmethod
    def grade_extraction(fields, invoice):
        return 0.999 if fields.get("vendor_name") == invoice["vendor_name"] else 0.001

    @staticmethod
    def grade_category(category, invoice):
        return 0.999 if category == invoice["category"] else 0.001

    @staticmethod
    def grade_anomaly(flag, invoice):
        return 0.999 if flag == invoice["anomaly_flag"] else 0.001


@pytest.fixture(autouse=True)
def patch_graders(monkeypatch):
    monkeypatch.setattr("env.environment.grade_extraction", DummyGraders.grade_extraction)
    monkeypatch.setattr("env.environment.grade_category", DummyGraders.grade_category)
    monkeypatch.setattr("env.environment.grade_anomaly", DummyGraders.grade_anomaly)


def test_reset_returns_observation():
    env = InvoiceEnv(batch_size=2, seed=42)
    obs = env.reset()
    assert obs.vendor_name != ""  # should be a real vendor
    assert isinstance(obs.amount, float)


def test_step_progression_and_reward():
    env = InvoiceEnv(batch_size=2, seed=42)
    obs = env.reset()

    action = InvoiceAction(
        extracted_fields={"vendor_name": obs.vendor_name, "invoice_date": obs.invoice_date},
        category=env.current_invoice["category"],
        anomaly_flag=env.current_invoice["anomaly_flag"]
    )

    next_obs, reward, done, info = env.step(action)

    # Reward is clamped by env.MAX_REWARD_SCORE.
    assert reward.score == pytest.approx(0.99)
    assert reward.details["extraction"] == 0.999
    assert reward.details["category"] == 0.999
    assert reward.details["anomaly"] == 0.999

    # Info should contain ground truth
    assert "ground_truth_category" in info
    assert "cumulative_reward" in info

    # Next observation should be valid until episode ends
    assert isinstance(next_obs.vendor_name, str)


def test_state_tracking():
    env = InvoiceEnv(batch_size=1, seed=123)
    obs = env.reset()
    assert env.state()["pointer"] == 0

    action = InvoiceAction(
        extracted_fields={"vendor_name": obs.vendor_name, "invoice_date": obs.invoice_date},
        category=env.current_invoice["category"],
        anomaly_flag=env.current_invoice["anomaly_flag"]
    )
    next_obs, reward, done, info = env.step(action)

    # After one step, pointer should advance
    state = env.state()
    assert state["pointer"] == 1
    assert state["steps"] == 1
    assert state["total_reward"] > 0.0
    assert done is True
    # Terminal observation metadata
    assert next_obs.metadata.get("terminal") is True