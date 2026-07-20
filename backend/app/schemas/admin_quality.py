from sqlmodel import SQLModel


class QualityCreate(SQLModel):
    quality_resolution: int
    is_hevc: bool = False
    is_hq: bool = False
    quality_order: int
    quality_name: str


class QualityUpdate(SQLModel):
    quality_resolution: int | None = None
    is_hevc: bool | None = None
    is_hq: bool | None = None
    quality_order: int | None = None
    quality_name: str | None = None


class QualityAdminPublic(SQLModel):
    quality_id: int
    quality_resolution: int
    is_hevc: bool
    is_hq: bool
    quality_order: int
    quality_name: str


class QualityAdminListPublic(SQLModel):
    data: list[QualityAdminPublic]
