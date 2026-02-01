from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from salome.bot import SalomeBot


class CommandHandler(ABC):
    option: ClassVar[dict[str, Any]]

    def __init__(self, bot: "SalomeBot"):
        self.bot = bot

    @abstractmethod
    def __call__(self, message: dict[str, Any]) -> None:
        raise NotImplementedError

    def parse_options(self, message: dict[str, Any]) -> dict[str, Any]:
        return {opt["name"]: opt["value"] for opt in message["data"]["options"]}
