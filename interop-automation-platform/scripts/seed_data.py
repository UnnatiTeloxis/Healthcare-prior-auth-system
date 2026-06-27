#!/usr/bin/env python
"""Seed database with test data for the Interop Automation Platform."""

from pathlib import Path


def seed_database() -> None:
    print("Seeding database with test data...")

    profiles_path = Path("/app/data/profiles")
    questionnaires_path = Path("/app/data/questionnaires")
    patients_path = Path("/app/data/scenarios/patients")
    scenarios_path = Path("/app/data/scenarios/crd")

    print(f"Loading profiles from {profiles_path}")
    print(f"Loading questionnaires from {questionnaires_path}")
    print(f"Loading patients from {patients_path}")
    print(f"Loading scenarios from {scenarios_path}")

    profile_count = len(list(profiles_path.rglob("*.json"))) if profiles_path.exists() else 0
    questionnaire_count = len(list(questionnaires_path.glob("*.json"))) if questionnaires_path.exists() else 0
    patient_count = len(list(patients_path.glob("*.json"))) if patients_path.exists() else 0
    scenario_count = len(list(scenarios_path.glob("*.json"))) if scenarios_path.exists() else 0

    print(f"Found {profile_count} profiles")
    print(f"Found {questionnaire_count} questionnaires")
    print(f"Found {patient_count} patients")
    print(f"Found {scenario_count} CRD scenarios")
    print("Database seed placeholder completed successfully!")


if __name__ == "__main__":
    seed_database()
