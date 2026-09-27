from dataclasses import dataclass


@dataclass
class AppError(Exception):
    status_code: int
    code: str
    message: str

    def __post_init__(self) -> None:
        super().__init__(self.message)


class AIUnavailableError(Exception):
    pass