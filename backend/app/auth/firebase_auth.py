import json
import logging
import os
from typing import Dict, Any, List, Optional
import firebase_admin
from firebase_admin import auth as firebase_auth_admin, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

logger = logging.getLogger(__name__)

# Security scheme
bearer_scheme = HTTPBearer(auto_error=False)

# Initialize Firebase Admin SDK
_firebase_initialized = False

def init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return

    try:
        if settings.FIREBASE_SERVICE_ACCOUNT_JSON:
            try:
                cred_dict = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                _firebase_initialized = True
                logger.info("Firebase Admin SDK initialized from JSON string.")
            except Exception as e:
                logger.error(f"Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
        elif settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            logger.info(f"Firebase Admin SDK initialized from file: {settings.FIREBASE_CREDENTIALS_PATH}")
        else:
            # Check default credentials or initialize default for dev
            if settings.ENVIRONMENT == "development":
                logger.warning("No Firebase credentials provided. Running in dev mock-auth mode.")
            else:
                try:
                    firebase_admin.initialize_app()
                    _firebase_initialized = True
                    logger.info("Firebase Admin SDK initialized with default credentials.")
                except Exception as e:
                    logger.warning(f"Could not initialize Firebase default credentials: {e}")
    except Exception as e:
        logger.error(f"Firebase init error: {e}")

# Call at module import
init_firebase()

async def verify_firebase_token(token: str) -> Dict[str, Any]:
    """Verify Firebase ID token and return decoded claims."""
    if not _firebase_initialized:
        # Development fallback mode
        if settings.ENVIRONMENT == "development":
            return {
                "uid": "dev-user-123",
                "email": "admin@redhack.mine",
                "name": "Dev Admin",
                "role": "ADMIN",
                "roles": ["ADMIN", "OPERATOR", "VIEWER"]
            }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase Authentication not initialized on server."
        )

    try:
        decoded_token = firebase_auth_admin.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        # In development mode, accept any token as a valid admin/operator
        if settings.ENVIRONMENT == "development":
            return {
                "uid": "dev-user-123",
                "email": "adnan@mineguard.internal",
                "name": "SHAIK ADNAN HYDER",
                "displayName": "SHAIK ADNAN HYDER",
                "role": "ADMIN",
                "roles": ["ADMIN", "OPERATOR", "VIEWER"]
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Dict[str, Any]:
    """FastAPI dependency to extract and verify the bearer token."""
    if not auth_credentials or not auth_credentials.credentials:
        if settings.ENVIRONMENT == "development":
            # For development convenience when testing endpoints without headers
            return {
                "uid": "dev-user-123",
                "email": "admin@redhack.mine",
                "name": "Dev Admin",
                "role": "ADMIN",
                "roles": ["ADMIN", "OPERATOR", "VIEWER"]
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_credentials.credentials
    user = await verify_firebase_token(token)
    return user

def require_role(*required_roles: str):
    """Dependency factory to enforce role-based authorization."""
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = (current_user.get("role") or "VIEWER").upper()
        user_roles = [r.upper() for r in current_user.get("roles", [user_role])]
        
        # Admin has access to all roles
        if "ADMIN" in user_roles or user_role == "ADMIN":
            return current_user

        # Hierarchy / Check
        req_upper = [r.upper() for r in required_roles]
        if "OPERATOR" in req_upper and ("OPERATOR" in user_roles or user_role == "OPERATOR"):
            return current_user

        if any(role in user_roles for role in req_upper) or user_role in req_upper:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: requires one of roles {required_roles}"
        )
    return role_checker
