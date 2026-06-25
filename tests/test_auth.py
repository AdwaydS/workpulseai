"""Basic tests for WORKPULSE AI."""

import pytest
from authentication.security import hash_password, verify_password, create_access_token, decode_token


def test_password_hashing():
    hashed = hash_password("Workpulse@123")
    assert verify_password("Workpulse@123", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_token():
    token = create_access_token({"sub": "1", "email": "test@test.com", "role": "admin", "session_id": "abc"})
    data = decode_token(token)
    assert data is not None
    assert data.user_id == 1
    assert data.email == "test@test.com"
