import pytest

 
@pytest.fixture(autouse=True)
async def clean_database(database_client):
    """
    Automatically clean all tables in the test database before each test.
    """
    await database_client.clean_tables()
