import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
AsyncSession, async_sessionmaker, create_async_engine
)
from app.main import app
from app.core.database import Base, get_db

# Base de données de test (SQLite en mémoire)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Crée le moteur de base de données de test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncSession:
    """Session de base de données pour chaque test."""
    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with TestSessionLocal() as session:
        yield session
        await session.rollback() # Annuler les changements après chaque test


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """Client HTTP de test avec override de la DB."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient, db_session: AsyncSession):
    """Client HTTP authentifié."""
    # Créer un utilisateur de test
    response = await client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    })
    assert response.status_code == 201
    # Se connecter
    response = await client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpass123"},
    )
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
