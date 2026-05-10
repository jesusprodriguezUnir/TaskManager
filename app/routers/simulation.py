from fastapi import APIRouter, Depends
from ..auth import require_auth
from ..services import simulation as simulation_svc

router = APIRouter(prefix="/simulation", tags=["simulation"])

@router.post("/seed")
async def seed_data(_: bool = Depends(require_auth)):
    return await simulation_svc.seed_mock_data()

@router.post("/clear")
async def clear_data(_: bool = Depends(require_auth)):
    await simulation_svc.clear_all_data()
    return {"status": "success", "message": "All data cleared"}
