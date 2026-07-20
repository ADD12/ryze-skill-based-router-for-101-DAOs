from src.rye_router.router import SkillRouter
from src.rye_router.models import JobError, TeamMember
from unittest.mock import MagicMock


def test_router_matches_best_candidate():
    # Setup mock triage to return python and cuda skills
    mock_triage = MagicMock()
    mock_triage.analyze_error.return_value = ["python", "cuda"]

    # Setup mock roster to return three candidates with different skills
    mock_roster = MagicMock()
    mock_roster.get_available_members.return_value = [
        TeamMember(
            user_id="u1",
            slack_id="S1",
            name="Alice",
            skills=["python"],
            is_available=True,
            current_workload=1,
        ),
        TeamMember(
            user_id="u2",
            slack_id="S2",
            name="Bob",
            skills=["python", "cuda"],
            is_available=True,
            current_workload=2,
        ),
        TeamMember(
            user_id="u3",
            slack_id="S3",
            name="Charlie",
            skills=["java"],
            is_available=True,
            current_workload=0,
        ),
    ]

    router = SkillRouter(triage=mock_triage, roster=mock_roster)

    # Simulate a job error
    error = JobError(
        job_id="job123", owner_id="u4", system="GH", error_message="cuda out of memory"
    )
    decision = router.route_error(error)

    # Asserts
    assert decision is not None
    # Bob has the highest overlap (python, cuda)
    assert decision.assigned_user_id == "u2"
    assert "Matched on skills: 2" in decision.reasoning


def test_router_handles_tie_by_workload():
    mock_triage = MagicMock()
    mock_triage.analyze_error.return_value = ["python"]

    mock_roster = MagicMock()
    mock_roster.get_available_members.return_value = [
        # Alice and Bob both have the required skill, but Bob has lower workload
        TeamMember(
            user_id="u1",
            slack_id="S1",
            name="Alice",
            skills=["python"],
            is_available=True,
            current_workload=5,
        ),
        TeamMember(
            user_id="u2",
            slack_id="S2",
            name="Bob",
            skills=["python"],
            is_available=True,
            current_workload=1,
        ),
    ]

    router = SkillRouter(triage=mock_triage, roster=mock_roster)

    error = JobError(
        job_id="job124", owner_id="u4", system="GH", error_message="python error"
    )
    decision = router.route_error(error)

    assert decision is not None
    assert decision.assigned_user_id == "u2"


def test_router_returns_none_if_no_candidates():
    mock_triage = MagicMock()
    mock_triage.analyze_error.return_value = ["python"]

    mock_roster = MagicMock()
    mock_roster.get_available_members.return_value = []

    router = SkillRouter(triage=mock_triage, roster=mock_roster)
    error = JobError(job_id="job125", owner_id="u4", system="GH", error_message="err")
    decision = router.route_error(error)

    assert decision is None
