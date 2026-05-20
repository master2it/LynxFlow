"""Import side-effect: register SQLModel tables."""

from app.storage.db.models import AppSetting, PromptHistory

__all__ = ["AppSetting", "PromptHistory"]
