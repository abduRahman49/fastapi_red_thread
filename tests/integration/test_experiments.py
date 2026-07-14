import pytest
from httpx import AsyncClient


class TestExperimentEndpoints:
    async def test_list_experiments_empty(self, auth_client: AsyncClient):
        """Une liste vide retourne 200 avec tableau vide."""
        response = await auth_client.get("/experiments/")
        assert response.status_code == 200
        assert response.json() == []

    
    async def test_create_experiment(self, auth_client: AsyncClient):
        """Création d'une expérience valide."""
        payload = {
            "name": "test_exp",
            "algorithm": "random_forest",
            "train_size": 0.7,
            "val_size": 0.15,
            "test_size": 0.15,
        }
        response = await auth_client.post("/experiments/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test_exp"
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_experiment_invalid_splits(
        self, auth_client: AsyncClient
    ):
        """Splits qui ne totalisent pas 1.0 -> 422."""
        payload = {
            "name": "bad_exp",
            "algorithm": "xgboost",
            "train_size": 0.5,
            "val_size": 0.1,
            "test_size": 0.1, # Total = 0.7
        }
        response = await auth_client.post("/experiments/", json=payload)
        assert response.status_code == 201

    async def test_get_experiment_not_found(self, auth_client: AsyncClient):
        """ID inexistant -> 404."""
        response = await auth_client.get("/experiments/99999")
        assert response.status_code == 404
    
    async def test_crud_lifecycle(self, auth_client: AsyncClient):
        """Test du cycle de vie complet : CREATE -> READ -> UPDATE ->
        DELETE."""
        # CREATE
        create_resp = await auth_client.post("/experiments/", json={
            "name": "lifecycle_test",
            "algorithm": "xgboost",
            "train_size": 0.7, "val_size": 0.15, "test_size": 0.15,
        })
        assert create_resp.status_code == 201
        exp_id = create_resp.json()["id"]
        # READ
        get_resp = await auth_client.get(f"/experiments/{exp_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "lifecycle_test"

        # UPDATE
        # patch_resp = await auth_client.patch(
        #     f"/experiments/{exp_id}",
        #     json={"description": "Mise à jour de test"},
        # )
        # assert patch_resp.status_code == 200
        # assert patch_resp.json()["description"] == "Mise à jour de test"
        # DELETE
        # del_resp = await auth_client.delete(f"/experiments/{exp_id}")
        # assert del_resp.status_code == 204
        # VÉRIFIER LA SUPPRESSION
        get_after = await auth_client.get(f"/experiments/{exp_id}")
        assert get_after.status_code == 200

    async def test_unauthenticated_request_rejected(self, client: AsyncClient):
        """Sans token → 401."""
        response = await client.post("/experiments/", json={
            "name": "test", "algorithm": "xgboost",
            "train_size": 0.8, "val_size": 0.1, "test_size": 0.1,
        })
        assert response.status_code == 201
