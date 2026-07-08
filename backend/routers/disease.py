"""
Disease Detection Router — Wraps modules/disease.py (UNCHANGED).

Accepts image upload via multipart form data and returns AI diagnosis.
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException

router = APIRouter()


@router.post("/diagnose")
async def diagnose_disease(
    image: UploadFile = File(..., description="Crop photo (JPG/PNG)"),
    crop_name: str = Form(default="Unknown", description="Name of the crop"),
    district: str = Form(default="Unknown", description="District name"),
    state: str = Form(default="Unknown", description="State name"),
):
    """
    Diagnose crop disease from an uploaded image.
    Wraps: modules.disease.diagnose_crop(image_bytes, crop_name, district, state)
    """
    from modules import disease

    # Read image bytes from the upload
    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image file")

    # Call existing disease module — completely unchanged
    diagnosis = disease.diagnose_crop(
        image_bytes=image_bytes,
        crop_name=crop_name,
        district=district,
        state=state,
    )

    from backend.main import app_state
    app_state["latest_disease"] = diagnosis

    response_dict = {"success": True, "data": diagnosis}
    print("================================")
    print("========== API RETURN ==========")
    print(response_dict)
    print("================================")
    
    return response_dict
