"""
Calculator Router
FastAPI endpoints for glass price calculator
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from models.user import TokenData
from middleware.auth import get_current_user
from database import Database

router = APIRouter(tags=["calculator"])


# Request models for admin updates
class GlassConfigUpdate(BaseModel):
    thickness: str
    type: str
    base_price: float
    polish_price: float
    only_tempered: bool = False
    no_polish: bool = False
    never_tempered: bool = False


class MarkupUpdate(BaseModel):
    name: str
    percentage: float


class BeveledPricingUpdate(BaseModel):
    glass_thickness: str
    price_per_inch: float


class ClippedCornersPricingUpdate(BaseModel):
    num_corners: int
    price: float


class CalculatorSettingsUpdate(BaseModel):
    minimum_sq_ft: Optional[float] = None
    markup_divisor: Optional[float] = None
    contractor_discount_rate: Optional[float] = None
    flat_polish_rate: Optional[float] = None


class FormulaConfigUpdate(BaseModel):
    formula_mode: str  # 'divisor', 'multiplier', or 'custom'
    divisor_value: Optional[float] = None
    multiplier_value: Optional[float] = None
    custom_expression: Optional[str] = None
    enable_base_price: bool = True
    enable_polish: bool = True
    enable_beveled: bool = True
    enable_clipped_corners: bool = True
    enable_tempered_markup: bool = True
    enable_shape_markup: bool = True
    enable_contractor_discount: bool = True


@router.get("/config")
async def get_calculator_config(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get calculator configuration including:
    - Glass pricing (base + polish rates)
    - Beveled pricing
    - Clipped corners pricing
    - System settings (minimum sq ft, markup divisor, etc.)
    - Formula configuration
    """
    db = Database()
    config = db.get_calculator_config()
    return config


# ========== ADMIN UPDATE ENDPOINTS ==========

@router.put("/admin/glass-config/{glass_id}")
async def update_glass_config(
    glass_id: int,
    update: GlassConfigUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update glass configuration (admin only)"""
    db = Database()
    try:
        response = db.client.table("glass_config").update({
            "thickness": update.thickness,
            "type": update.type,
            "base_price": update.base_price,
            "polish_price": update.polish_price,
            "only_tempered": update.only_tempered,
            "no_polish": update.no_polish,
            "never_tempered": update.never_tempered
        }).eq("id", glass_id).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/glass-config")
async def create_glass_config(
    config: GlassConfigUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Create new glass configuration (admin only)"""
    db = Database()
    try:
        response = db.client.table("glass_config").insert({
            "thickness": config.thickness,
            "type": config.type,
            "base_price": config.base_price,
            "polish_price": config.polish_price,
            "only_tempered": config.only_tempered,
            "no_polish": config.no_polish,
            "never_tempered": config.never_tempered
        }).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/glass-config/{glass_id}")
async def delete_glass_config(
    glass_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """Soft delete glass configuration (admin only)"""
    db = Database()
    try:
        from datetime import datetime
        response = db.client.table("glass_config").update({
            "deleted_at": datetime.now().isoformat()
        }).eq("id", glass_id).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/markups")
async def update_markups(
    updates: List[MarkupUpdate],
    current_user: TokenData = Depends(get_current_user)
):
    """Update markup percentages (admin only)"""
    db = Database()
    try:
        for markup in updates:
            db.client.table("markups").update({
                "percentage": markup.percentage
            }).eq("name", markup.name).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/beveled-pricing")
async def update_beveled_pricing(
    updates: List[BeveledPricingUpdate],
    current_user: TokenData = Depends(get_current_user)
):
    """Update beveled pricing (admin only)"""
    db = Database()
    try:
        for pricing in updates:
            db.client.table("beveled_pricing").update({
                "price_per_inch": pricing.price_per_inch
            }).eq("glass_thickness", pricing.glass_thickness).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/clipped-corners-pricing")
async def update_clipped_corners_pricing(
    updates: List[ClippedCornersPricingUpdate],
    current_user: TokenData = Depends(get_current_user)
):
    """Update clipped corners pricing (admin only)"""
    db = Database()
    try:
        for pricing in updates:
            db.client.table("clipped_corners_pricing").update({
                "price": pricing.price
            }).eq("num_corners", pricing.num_corners).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/settings")
async def update_calculator_settings(
    update: CalculatorSettingsUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update calculator system settings (admin only)"""
    db = Database()
    try:
        # Update each setting that was provided
        updates_map = {
            "minimum_sq_ft": update.minimum_sq_ft,
            "markup_divisor": update.markup_divisor,
            "contractor_discount_rate": update.contractor_discount_rate,
            "flat_polish_rate": update.flat_polish_rate
        }

        for key, value in updates_map.items():
            if value is not None:
                db.client.table("calculator_settings").update({
                    "setting_value": value
                }).eq("setting_key", key).execute()

        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/formula-config")
async def update_formula_config(
    update: FormulaConfigUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update pricing formula configuration (admin only)"""
    db = Database()
    try:
        from datetime import datetime

        # First, deactivate current active formula
        db.client.table("pricing_formula_config").update({
            "is_active": False
        }).eq("is_active", True).execute()

        # Create new formula config
        response = db.client.table("pricing_formula_config").insert({
            "formula_mode": update.formula_mode,
            "divisor_value": update.divisor_value or 0.28,
            "multiplier_value": update.multiplier_value or 3.5714,
            "custom_expression": update.custom_expression,
            "enable_base_price": update.enable_base_price,
            "enable_polish": update.enable_polish,
            "enable_beveled": update.enable_beveled,
            "enable_clipped_corners": update.enable_clipped_corners,
            "enable_tempered_markup": update.enable_tempered_markup,
            "enable_shape_markup": update.enable_shape_markup,
            "enable_contractor_discount": update.enable_contractor_discount,
            "is_active": True,
            "created_by": current_user.user_id,
            "created_at": datetime.now().isoformat()
        }).execute()

        return {"success": True, "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
