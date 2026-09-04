from __future__ import annotations

import json
from typing import Any


def build_system_prompt() -> str:
    output_schema = {
        "patient_id": "string",
        "demographics": {
            "name": "string or null",
            "sex": "string or null",
            "race_ethnicity": "string or null",
            "age_at_first_note": "string or null",
        },
        "complaints": [
            {
                "text": "string",
                "first_date": "YYYY-MM-DD or null",
                "last_date": "YYYY-MM-DD or null",
                "source_note_ids": ["string"],
            }
        ],
        "conditions": [
            {
                "text": "string",
                "source": "assessment, history, or other",
                "date": "YYYY-MM-DD or null",
                "source_note_id": "string",
            }
        ],
        "allergies": {
            "status": "none_known, documented, or not_documented",
            "items": [
                {
                    "allergen": "string",
                    "reaction": "string or null",
                    "source_note_ids": ["string"],
                }
            ],
        },
        "medication_events": [
            {
                "name": "string",
                "dose": "string or null",
                "unit": "string or null",
                "route": "string or null",
                "frequency": "string or null",
                "event_type": "current_medication or prescribed_in_plan",
                "date": "YYYY-MM-DD or null",
                "source_note_id": "string",
                "evidence": "short supporting text",
            }
        ],
        "plan_actions": [
            {
                "type": "careplan, procedure, immunization, report, or other",
                "description": "string",
                "date": "YYYY-MM-DD or null",
                "source_note_id": "string",
            }
        ],
        "data_quality_flags": ["string"],
    }

    return f"""
You are a clinical information extraction assistant.

You will receive one synthetic Synthea patient record as JSON. Extract only
information explicitly documented in the input. Do not diagnose, speculate,
or invent missing facts.

Rules:

1. Process one patient only.
2. Use each note's date to determine chronology. Do not rely on array order.
3. Preserve every clinical_note_id as the source identifier.
4. Extract medications from both current_medications and plan.
5. Label medications from current_medications as current_medication.
6. Label medications prescribed in plan as prescribed_in_plan.
7. Do not infer that a medication continued or was discontinued.
8. Preserve different medication doses as separate events.
9. Extract dose, unit, route, and frequency only when explicitly documented.
10. Do not treat "No Active Medications" as a medication.
11. Keep explicit negatives distinguishable from undocumented information.
12. For allergies:
    - Use none_known when the record explicitly says no known allergies.
    - Use documented when allergies are listed.
    - Use not_documented when allergy information is absent or unclear.
13. Do not include DICOM, DNA, or filesystem paths in the result.
14. Do not treat administrative text as a clinical condition.
15. Consolidate repeated identical complaints where appropriate.
16. Preserve source-note references for every extracted item.
17. Use null for unavailable scalar values and [] for unavailable lists.
18. Return exactly one valid JSON object with no Markdown or explanation.

The output must follow this structure:

{json.dumps(output_schema, indent=2)}
""".strip()


def _as_list(value: Any) -> list[Any]:
    """
    Convert a string-or-list field into a list without silently discarding data.
    """
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        value = value.strip()
        return [value] if value else []

    return [value]


def _prepare_patient_record(patient_record: dict[str, Any]) -> dict[str, Any]:
    """
    Validate and normalize one processed patient record before prompting.
    """
    if not isinstance(patient_record, dict):
        raise TypeError("patient_record must be a dictionary")

    patient_id = patient_record.get("patient_id")
    notes = patient_record.get("notes")

    if not isinstance(patient_id, str) or not patient_id.strip():
        raise ValueError("patient_record must contain a non-empty patient_id")

    if not isinstance(notes, list):
        raise TypeError("patient_record['notes'] must be a list")

    prepared_notes: list[dict[str, Any]] = []

    for input_note_number, note in enumerate(notes, start=1):
        if not isinstance(note, dict):
            raise TypeError(
                f"Note {input_note_number} must be a dictionary"
            )

        prepared_note = dict(note)

        # Some processed files contain a string for complaints while others
        # contain a list. Present a consistent input shape to the LLM.
        prepared_note["complaints"] = _as_list(
            prepared_note.get("complaints")
        )
        prepared_note["allergies"] = _as_list(
            prepared_note.get("allergies")
        )
        prepared_note["current_medications"] = _as_list(
            prepared_note.get("current_medications")
        )

        # Preserve original order for traceability, even though the notes are
        # sorted chronologically below.
        prepared_note["input_note_number"] = input_note_number
        prepared_notes.append(prepared_note)

    prepared_notes.sort(
        key=lambda note: (
            note.get("date") or "9999-12-31",
            note["input_note_number"],
        )
    )

    return {
        "patient_id": patient_id,
        "notes": prepared_notes,
    }


def format_patient_record(patient_record: dict[str, Any]) -> str:
    """
    Return the normalized patient record as readable JSON.
    """
    prepared_record = _prepare_patient_record(patient_record)

    return json.dumps(
        prepared_record,
        ensure_ascii=False,
        indent=2,
    )


def build_user_prompt(patient_record: dict[str, Any]) -> str:
    """
    Build the user message sent to the LLM.
    """
    formatted_record = format_patient_record(patient_record)

    return (
        "Extract the clinical information from the following patient record.\n\n"
        "PATIENT_RECORD_JSON:\n"
        f"{formatted_record}\n"
        "\nEND_PATIENT_RECORD_JSON"
    )


def build_messages(
    patient_record: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Build messages compatible with the OpenAI chat-completions API.
    """
    return [
        {
            "role": "system",
            "content": build_system_prompt(),
        },
        {
            "role": "user",
            "content": build_user_prompt(patient_record),
        },
    ]

