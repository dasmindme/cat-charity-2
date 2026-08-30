import pytest
from sqlalchemy import select

DONATION_URL = '/donation/'
PROJECTS_URL = '/charity_project/'


@pytest.mark.usefixtures('donation')
def test_donation_without_projects(superuser_client):
    response_donation = superuser_client.get(DONATION_URL)
    data_donation = response_donation.json()
    assert len(data_donation) == 1, (
        'Убедитесь, что в ответ на GET-запрос суперпользователя к эндпоинту '
        f'`{DONATION_URL}` возвращается список всех существующих '
        'пожертвований.'
    )
    assert data_donation[0]['invested_amount'] == 0, (
        'Если получено пожертвование, но открытых проектов нет, '
        'сумма в поле `invested_amount` должна оставаться нулевой.'
    )


@pytest.mark.usefixtures('charity_project')
def test_project_without_donation(superuser_client):
    response = superuser_client.get(PROJECTS_URL)
    data = response.json()
    assert len(data) == 1, (
        'Убедитесь, что в ответ на GET-запрос суперпользователя к эндпоинту '
        f'`{PROJECTS_URL}` возвращается список всех существующих проектов.'
    )
    assert data[0]['invested_amount'] == 0, (
        'Если проект создан, но пожертвований пока нет, сумма в поле '
        '`invested_amount` должна оставаться нулевой.'
    )


async def test_fully_invested_amount_for_two_projects(
        user_client, charity_project, charity_project_nunchaku, session,
        charity_project_model
):
    common_asser_msg = (
        'При тестировании создано два пустых проекта. '
        'Затем тест создал два пожертвования (через POST-запросы '
        f'зарегистрированного пользователя к `{DONATION_URL}`). Эти '
        'пожертвования полностью и без остатка покрывают требуемую сумму '
        'первого проекта. В такой ситуации `invested_amount` второго проекта '
        'должна оставаться нулевой.'
    )
    [user_client.post(
        DONATION_URL,
        json={
            'full_amount': charity_project.full_amount // 2,
            'comment': 'test'
        }
    ) for _ in range(2)]
    charity_project = await session.execute(
        select(charity_project_model).where(
            charity_project_model.id == charity_project.id)
    )
    charity_project = charity_project.scalars().first()
    charity_project_nunchaku = await session.execute(
        select(charity_project_model).where(
            charity_project_model.id == charity_project_nunchaku.id)
    )
    charity_project_nunchaku = charity_project_nunchaku.scalars().first()
    assert charity_project.fully_invested, common_asser_msg
    assert not charity_project_nunchaku.fully_invested, common_asser_msg
    assert charity_project_nunchaku.invested_amount == 0, common_asser_msg


async def test_donation_to_little_invest_project(
        user_client, charity_project_little_invested, charity_project_nunchaku,
        session, charity_project_model
):
    common_asser_msg = (
        'При тестировании создано два проекта (через POST-запросы '
        f'зарегистрированного пользователя к `{DONATION_URL}`). '
        'Один из проектов частично инвестирован, а второй - без инвестиций. '
        'Затем тест создает пожертвование, недостаточное для закрытия '
        'первого проекта. Пожертвование должно добавиться '
        'в первый проект; второй проект должен остаться пустым.'
    )
    already_invested = charity_project_little_invested.invested_amount
    to_invest = (
        charity_project_little_invested.full_amount - already_invested - 1
    )
    user_client.post(
        DONATION_URL,
        json={'full_amount': to_invest, 'comment': 'test'}
    )
    charity_project_little_invested = await session.execute(
        select(charity_project_model).where(
            charity_project_model.id == charity_project_little_invested.id)
    )
    charity_project_little_invested = (
        charity_project_little_invested.scalars().first()
    )
    charity_project_nunchaku = await session.execute(
        select(charity_project_model).where(
            charity_project_model.id == charity_project_nunchaku.id)
    )
    charity_project_nunchaku = charity_project_nunchaku.scalars().first()
    assert not charity_project_little_invested.fully_invested, common_asser_msg
    assert (
        charity_project_little_invested.invested_amount == (
            already_invested + to_invest
        )
    ), common_asser_msg
    assert not charity_project_nunchaku.fully_invested, common_asser_msg
    assert charity_project_nunchaku.invested_amount == 0, common_asser_msg


async def test_project_invests_at_creation_if_donation_exists(
        superuser_client, donation, project_json
):
    common_asser_msg = (
        'При тестировании в базе данных создано нераспределённое '
        'пожертвование. Затем тест создал новый целевой проект (через '
        f'POST-запрос суперпользователя к `{PROJECTS_URL}`). Значение поля '
        '`full_amount` проекта равно сумме нераспределённого пожертвования. '
        'Нераспределённая сумма должна быть автоматически инвестирована в '
        'новый проект при его создании, а проект должен быть закрыт.'
    )
    project_json['full_amount'] = donation.full_amount
    response = superuser_client.post(PROJECTS_URL, json=project_json)
    project = response.json()
    assert project['invested_amount'] == donation.full_amount, common_asser_msg
    assert project['fully_invested'], common_asser_msg
