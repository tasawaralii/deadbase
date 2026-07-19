import datetime as dt
import decimal

from sqlmodel import SQLModel


class LinkAdminPublic(SQLModel):
    link_id: int
    content_id: int
    filename: str
    is_live: bool
    gdrive_email: str
    gdriveid: str
    type: str
    mimetype: str
    duration: int
    note: str
    only_hindi: bool
    size: decimal.Decimal | None
    quality_id: int | None
    added_date: dt.datetime
    updated_date: dt.datetime


class LinkAdminListPublic(SQLModel):
    data: list[LinkAdminPublic]


class LinkBatchCreate(SQLModel):
    gdrive_urls: list[str]
    note: str = ""
    only_hindi: bool = False


class LinkBatchResultItem(SQLModel):
    gdrive_url: str
    success: bool
    link: LinkAdminPublic | None = None
    error: str | None = None


class LinkBatchResult(SQLModel):
    results: list[LinkBatchResultItem]


class GdriveFolderFile(SQLModel):
    file_id: str
    name: str
    url: str


class GdriveFolderListing(SQLModel):
    files: list[GdriveFolderFile]


class LinkBulkDeleteResult(SQLModel):
    deleted_count: int


class LinkUpdate(SQLModel):
    # Deliberately excludes filename/gdriveid/type/mimetype/duration/size/
    # gdrive_email - those are all fetched from Google Drive at creation
    # time (see app.gdrive), never hand-typed. Only the fields an author
    # would realistically hand-tweak after the fact are editable here.
    is_live: bool | None = None
    note: str | None = None
    only_hindi: bool | None = None
    quality_id: int | None = None
