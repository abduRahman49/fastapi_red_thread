import pytest
from app.core.security import hash_password, verify_password, create_access_token

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        # AAA (Arrange, Act, Assert)
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"
        assert len(hashed) > 20

    def test_correct_password_verifies(self):
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True
    
    def test_wrong_password_fails(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False
    
    def test_different_hashes_for_same_password(self):
        """bcrypt genere un salt aleatoire."""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2 # Meme mot de passe, hashes differents


class TestJWT:
    def test_token_contains_subject(self):
        from app.core.security import decode_token
        token = create_access_token(subject=42)
        payload = decode_token(token)
        assert payload["sub"] == "42"
    
    def test_expired_token_raises(self):
        from datetime import timedelta
        from fastapi import HTTPException
        token = create_access_token(subject=1, expires_delta=timedelta(seconds=-1))
        with pytest.raises(HTTPException) as exc:
            from app.core.security import decode_token
            decode_token(token)
        assert exc.value.status_code == 401
