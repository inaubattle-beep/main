from backend.auth import create_access_token, verify_password

def create_jwt_token(data: dict):
    return create_access_token(data)