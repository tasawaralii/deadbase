from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, get_current_active_superuser
from app.schemas.admin_unlock_config import UnlockConfigPublic, UnlockConfigUpdate
from app.unlock import get_unlock_config

router = APIRouter(
    prefix="/unlock-config",
    tags=["admin"],
    dependencies=[Depends(get_current_active_superuser)],
)


@router.get("/")
def read_unlock_config(session: SessionDep) -> UnlockConfigPublic:
    config = get_unlock_config(session)
    return UnlockConfigPublic(
        required_solves=config.required_solves, report_threshold=config.report_threshold
    )


@router.patch("/")
def update_unlock_config(
    session: SessionDep, body: UnlockConfigUpdate
) -> UnlockConfigPublic:
    config = get_unlock_config(session)

    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(config, field, value)

    session.add(config)
    session.commit()
    session.refresh(config)
    return UnlockConfigPublic(
        required_solves=config.required_solves, report_threshold=config.report_threshold
    )
