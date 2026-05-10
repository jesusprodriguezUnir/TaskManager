import pytest
from app.services import simulation as svc
from app import db

@pytest.mark.asyncio
async def test_simulation_clear_and_seed(client):
    # The 'client' fixture initializes the DB pool and monkeypatches it
    
    # 1. Clear data
    await svc.clear_all_data()
    
    # Verify tables are empty
    count = await db.fetchval("SELECT count(*) FROM courses")
    assert count == 0
    
    # 2. Seed data
    result = await svc.seed_mock_data()
    assert result["status"] == "success"
    
    # Verify tables are populated
    count = await db.fetchval("SELECT count(*) FROM courses")
    assert count == 3
    
    count = await db.fetchval("SELECT count(*) FROM tasks")
    assert count == 4
    
    # 3. Clear again
    await svc.clear_all_data()
    count = await db.fetchval("SELECT count(*) FROM courses")
    assert count == 0
