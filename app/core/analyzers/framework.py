"""
AIRISS Framework definitions
"""

AIRISS_FRAMEWORK = {
    "name": "AIRISS",
    "version": "4.0",
    "description": "AI-driven Risk Intelligence Scoring System",
    "components": {
        "statistical": {
            "enabled": True,
            "weight": 0.6
        },
        "ai": {
            "enabled": True,
            "weight": 0.4
        }
    }
}