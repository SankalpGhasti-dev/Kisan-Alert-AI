"""
Auth Router — Placeholder for future Firebase Authentication.

Currently: No authentication logic. Login/Register simply return success
so the frontend can redirect to Location Setup.

Firebase Auth will be integrated in a future phase.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class LoginRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class RegisterRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None


@router.post("/login")
async def login(request: LoginRequest):
    """
    Placeholder login endpoint.
    Returns success so the frontend redirects to /location-setup.
    Firebase Authentication will replace this in a future phase.
    """
    return {
        "success": True,
        "message": "Login successful (auth not yet implemented)",
        "redirect": "/location-setup",
    }


@router.post("/register")
async def register(request: RegisterRequest):
    """
    Placeholder register endpoint.
    Returns success so the frontend redirects to /location-setup.
    Firebase Authentication will replace this in a future phase.
    """
    return {
        "success": True,
        "message": "Registration successful (auth not yet implemented)",
        "redirect": "/location-setup",
    }
