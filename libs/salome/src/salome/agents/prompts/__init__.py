from pathlib import Path

PROMPTS_PATH = Path(__file__).parent

SALOME_ROLE_PROMPT = (PROMPTS_PATH / "salome-role.md").read_text()
