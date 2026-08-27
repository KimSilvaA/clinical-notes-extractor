from pathlib import Path

COMPLAINT_SUBSTR = "# Chief Complaint"
HISTORY_SUBSTR = "# History of Present Illness"
SOCIAL_HISTORY_SUBSTR = "# Social History"
ALLERGIES_SUBSTR = "# Allergies"
MEDICATIONS_SUBSTR = "# Medications"
ASSESSMENT_SUBSTR = "# Assessment and Plan"
PLAN_SUBSTR = "## Plan"

# File path
RAW_INPUT_DIR = Path(__file__).parent.parent  / "src" / "data" / "raw" / "fhir" 
