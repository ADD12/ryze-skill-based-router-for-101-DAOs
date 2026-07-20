from typing import Optional
from .models import JobError, RoutingDecision
from .triage import AITriage
from .roster import RosterManager


class SkillRouter:
    def __init__(self, triage: AITriage, roster: RosterManager):
        self.triage = triage
        self.roster = roster

    def route_error(self, error: JobError) -> Optional[RoutingDecision]:
        """
        Main logic to find the best suited available team member.
        """
        # Step 1: AI Triage to determine required skills
        required_skills = self.triage.analyze_error(error)

        # Step 2: Get available members (exclude job owner)
        candidates = self.roster.get_available_members(exclude_user_id=error.owner_id)

        if not candidates:
            return None  # No one is available

        # Step 3: Match skills
        best_candidate = None
        max_overlap = -1

        for candidate in candidates:
            # Calculate skill overlap
            overlap = len(set(required_skills).intersection(set(candidate.skills)))
            if overlap > max_overlap:
                max_overlap = overlap
                best_candidate = candidate
            elif overlap == max_overlap:
                # Tie-breaker: lowest workload
                if (
                    best_candidate is None
                    or candidate.current_workload < best_candidate.current_workload
                ):
                    best_candidate = candidate

        if best_candidate:
            return RoutingDecision(
                job_id=error.job_id,
                assigned_user_id=best_candidate.user_id,
                required_skills=required_skills,
                reasoning=f"Matched on skills: {max_overlap} overlapping skills. Currently available.",
            )

        return None
