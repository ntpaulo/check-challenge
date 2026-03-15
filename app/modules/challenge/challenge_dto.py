from pydantic import BaseModel


class ChallengeRequestDTO(BaseModel):
    title: str
    duration: int
    start_date: str
