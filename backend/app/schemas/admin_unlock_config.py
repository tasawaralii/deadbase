from sqlmodel import SQLModel


class UnlockConfigUpdate(SQLModel):
    required_solves: int | None = None
    report_threshold: int | None = None


class UnlockConfigPublic(SQLModel):
    required_solves: int
    report_threshold: int
