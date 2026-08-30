from datetime import datetime

import pytest
import pytest_asyncio

from .user import superuser, user


@pytest_asyncio.fixture
async def charity_project(freezer, mixer):
    freezer.move_to('2010-10-10')
    project = mixer.blend(
        'app.models.charity_project.CharityProject',
        name='chimichangas4life',
        description='Huge fan of chimichangas. Wanna buy a lot',
        full_amount=1000000,
        create_date=datetime.now(),
    )
    await mixer.params['session'].commit()
    return project


@pytest_asyncio.fixture
async def charity_project_nunchaku(freezer, mixer):
    freezer.move_to('2010-10-10')
    project = mixer.blend(
        'app.models.charity_project.CharityProject',
        name='nunchaku',
        description='Nunchaku is better',
        full_amount=5000000,
        create_date=datetime.now(),
    )
    await mixer.params['session'].commit()
    return project


@pytest_asyncio.fixture
async def small_fully_invested_charity_project(freezer, mixer):
    freezer.move_to('2010-10-10')
    project = mixer.blend(
        'app.models.charity_project.CharityProject',
        name='1M$ for ur project',
        description='Wanna buy you project',
        full_amount=100,
        fully_invested=True,
        close_date=datetime.strptime('2010-10-11T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'),
        create_date=datetime.now(),
    )
    await mixer.params['session'].commit()
    return project


@pytest_asyncio.fixture
async def charity_project_little_invested(freezer, mixer):
    freezer.move_to('2010-10-10')
    project = mixer.blend(
        'app.models.charity_project.CharityProject',
        name='chimichangas4life',
        description='Huge fan of chimichangas. Wanna buy a lot',
        full_amount=1000000,
        invested_amount=100,
        create_date=datetime.now(),
    )
    await mixer.params['session'].commit()
    return project


@pytest_asyncio.fixture
async def closed_charity_project(freezer, mixer):
    freezer.move_to('2010-10-10')
    project = mixer.blend(
        'app.models.charity_project.CharityProject',
        name='chimichangas4life',
        description='Huge fan of chimichangas. Wanna buy a lot',
        full_amount=100,
        invested_amount=100,
        fully_invested=True,
        close_date=datetime.strptime('2010-10-11T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'),
        create_date=datetime.now(),
    )
    await mixer.params['session'].commit()
    return project


@pytest_asyncio.fixture
async def donation(freezer, mixer):
    freezer.move_to('2011-11-11')
    donation = mixer.blend(
        'app.models.donation.Donation',
        user_id=user.id,
        comment='To you for chimichangas',
        full_amount=100,
        create_date=datetime.now(),
    )
    await mixer.params['session'].commit()
    return donation


@pytest_asyncio.fixture
async def another_donation(freezer, mixer):
    freezer.move_to('2012-12-12')
    donation = mixer.blend(
        'app.models.donation.Donation',
        user_id=superuser.id,
        comment='From admin',
        full_amount=2000,
        create_date=datetime.now(),
    )
    await mixer.params['session'].commit()
    return donation


@pytest.fixture
def project_json():
    return {
        'name': 'Default project',
        'description': 'A regular project',
        'full_amount': 10000
    }
