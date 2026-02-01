from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from salome.bot import SalomeBot


class ScheduleHandler(ABC):
    def __init__(self, bot: "SalomeBot"):
        self.bot = bot

    @abstractmethod
    def __call__(self) -> None:
        raise NotImplementedError
