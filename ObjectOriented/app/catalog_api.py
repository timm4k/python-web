from fastapi import APIRouter

from app.catalog import PERFUMES, Perfume

router = APIRouter(prefix="/api/catalog", tags=["Perfume Catalog"])


@router.get("/perfumes")
def perfumes() -> tuple[Perfume, ...]:
    return PERFUMES
