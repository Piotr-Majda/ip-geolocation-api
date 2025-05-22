import asyncio
import datetime
from typing import Optional, Tuple, cast

import pytest

from app.domain.models.ip_data import Geolocation
from app.domain.repositories import UpsertResult
from app.infrastructure.database import DatabaseClient
from app.infrastructure.ip_geolocation_repository import IpGeolocationRepositoryImpl

pytestmark = pytest.mark.asyncio


# Minimal helper, assuming Geolocation Pydantic model has Optional timestamps
# or the test provides them. For brevity, non-essential fields are hardcoded.
def create_geo(
    ip: str,
    city: str,
    url: str = "test.com",
    created_at: Optional[datetime.datetime] = None,
    updated_at: Optional[datetime.datetime] = None,
) -> Geolocation:
    # If your Pydantic model *requires* created_at/updated_at, provide defaults here.
    # e.g., created_at = created_at or datetime.datetime.now(datetime.timezone.utc)
    return Geolocation(
        ip=ip,
        url=url,
        city=city,
        latitude=0,
        longitude=0,
        region="R",
        country="C",
        continent="Co",
        postal_code="P",
        created_at=created_at,
        updated_at=updated_at,
    )


@pytest.fixture
def repo(database_client: DatabaseClient) -> IpGeolocationRepositoryImpl:
    return IpGeolocationRepositoryImpl(database_client)


async def test_upsert_new_ip_is_created(repo: IpGeolocationRepositoryImpl):
    """Given new IP data, When upsert is called, Then action is CREATED and timestamps are set."""
    new_ip_data = create_geo("1.1.1.1", "Newville")
    returned_data, action = await repo.upsert(new_ip_data)
    assert action == UpsertResult.CREATED
    assert returned_data.city == "Newville"
    assert isinstance(returned_data.created_at, datetime.datetime)
    assert isinstance(returned_data.updated_at, datetime.datetime)


async def test_upsert_existing_ip_is_updated(repo: IpGeolocationRepositoryImpl):
    """Given existing IP, When upsert is called with new data, Then action is UPDATED and data changes."""
    existing_ip = "2.2.2.2"
    initial_data = create_geo(existing_ip, "Oldtown")
    initial_persisted, _ = await repo.upsert(initial_data)
    assert initial_persisted.created_at is not None  # Should be set by DB
    await asyncio.sleep(0.01)
    # For update, we might not pass created_at/updated_at in input, relying on DB
    updated_data = create_geo(existing_ip, "Newcity", url="updated.org")
    returned_data, action = await repo.upsert(updated_data)
    assert action == UpsertResult.UPDATED
    assert returned_data.city == "Newcity"
    assert returned_data.url == "updated.org"
    assert returned_data.created_at is not None and initial_persisted.created_at is not None
    assert returned_data.created_at.replace(microsecond=0) == initial_persisted.created_at.replace(
        microsecond=0
    )
    assert returned_data.updated_at is not None and initial_persisted.created_at is not None
    assert returned_data.updated_at > initial_persisted.created_at


async def test_upsert_concurrent_new_ip_one_creates_one_updates(repo: IpGeolocationRepositoryImpl):
    """Given new IP, When upsert is called twice concurrently, Then one CREATES and one UPDATES."""
    concurrent_ip = "3.3.3.3"
    data1 = create_geo(concurrent_ip, "CityOne", url="url1.com")
    data2 = create_geo(concurrent_ip, "CityTwo", url="url2.com")
    results = await asyncio.gather(repo.upsert(data1), repo.upsert(data2), return_exceptions=True)

    actions_observed = []
    processed_results_tuples: list[Tuple[Geolocation, UpsertResult]] = []

    for res_item_from_gather in results:
        if isinstance(res_item_from_gather, Exception):
            pytest.fail(f"Unexpected exception during concurrent upsert: {res_item_from_gather}")
        else:
            # Use cast to inform the linter that res_item_from_gather is now the expected tuple type
            successful_result_tuple = cast(Tuple[Geolocation, UpsertResult], res_item_from_gather)
            processed_results_tuples.append(successful_result_tuple)
            actions_observed.append(successful_result_tuple[1])

    assert UpsertResult.CREATED in actions_observed
    assert UpsertResult.UPDATED in actions_observed
    assert len(processed_results_tuples) == 2

    updated_result_data = None
    for data, action in processed_results_tuples:
        if action == UpsertResult.UPDATED:
            updated_result_data = data
            break
    assert updated_result_data is not None, "Could not find result from UPDATED action"

    is_data1 = updated_result_data.city == "CityOne" and updated_result_data.url == "url1.com"
    is_data2 = updated_result_data.city == "CityTwo" and updated_result_data.url == "url2.com"
    assert is_data1 or is_data2, "Updated data does not match one of the inputs"
