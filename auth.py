"""
Authentication, RBAC & API Security for TraffiQ
===============================================
Phase 7 Implementation:
- Role-based Access Control (Admin, Operator, Viewer)
- API Key authorization for external integrations
- Session validation and audit trail hooks
"""

import os
import hmac
from functools import wraps
from flask import request, jsonify, session
from database import log_audit

API_KEYS = {
    os.environ.get("TRAFFIQ_API_KEY", "traffiq_live_secret_key_2026"): "Admin",
    "operator_key_demo_2026": "Operator",
    "viewer_key_demo_2026": "Viewer"
}

ROLES_PERMISSIONS = {
    "Admin": ["read", "write_controls", "export", "manage_zones", "admin_users"],
    "Operator": ["read", "write_controls", "export", "manage_zones"],
    "Viewer": ["read", "export"]
}

def require_api_key(required_role: str = "Viewer"):
    """Decorator verifying API key or active authenticated browser session."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check Session First
            if session.get("authenticated"):
                user_role = session.get("role", "Admin")
                if _has_permission(user_role, required_role):
                    return f(*args, **kwargs)

            # Check Header / Param API Key
            key = request.headers.get("X-API-Key") or request.args.get("api_key")
            if key and key in API_KEYS:
                user_role = API_KEYS[key]
                if _has_permission(user_role, required_role):
                    return f(*args, **kwargs)

            return jsonify({"error": "Unauthorized: Insufficient role permissions or invalid API key"}), 401
        return decorated_function
    return decorator

def _has_permission(current_role: str, target_role: str) -> bool:
    hierarchy = {"Viewer": 1, "Operator": 2, "Admin": 3}
    return hierarchy.get(current_role, 0) >= hierarchy.get(target_role, 1)

def audit_action(username: str, action: str, details: str = ""):
    log_audit(username or "api_client", action, details)

