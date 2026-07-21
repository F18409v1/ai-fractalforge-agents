from pro_experience_agent.agent import ExperienceAgent


def test_handle_event_basic():
    a = ExperienceAgent()
    res = a.handle_event({"type": "ping"})
    assert res["status"] == "ok"
    assert res["type"] == "ping"
