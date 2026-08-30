import time

import pytest

PROJECTS_URL = '/charity_project/'
PROJECT_DETAILS_URL = PROJECTS_URL + '{project_id}'


@pytest.mark.parametrize(
    'invalid_name',
    [
        '',
        'lovechimichangasbutnunchakuisbetternunchakis4life' * 3,
        None,
    ],
    ids=['empty', 'too_long', 'None'],
)
def test_create_invalid_project_name(
        superuser_client, invalid_name, project_json
):
    project_json['name'] = invalid_name
    response = superuser_client.post(
        PROJECTS_URL,
        json=project_json,
    )
    assert response.status_code == 422, (
        'Убедитесь, что POST-запрос суперпользователя к эндпоинту '
        f'`{PROJECTS_URL}` с пустым полем `name` или со значением для этого '
        'поля длиннее 100 символов не проходит валидацию (возвращает ответ со '
        'статус-кодом 422).'
    )


@pytest.mark.parametrize(
    'description', [
        '',
        None,
    ]
)
def test_create_project_no_desc(superuser_client, description, project_json):
    project_json['description'] = description
    response = superuser_client.post(
        PROJECTS_URL,
        json=project_json
    )
    assert (
        response.status_code == 422
    ), (
        'Убедитесь, что POST-запрос суперпользователя к эндпоинту '
        f'`{PROJECTS_URL}` с пустым полем `description` не проходит валидацию '
        '(возвращает ответ со статус-кодом 422).'
    )


@pytest.mark.parametrize('forbidden_key', [
    {'invested_amount': 100},
    {'fully_invested': True},
    {'id': 5000},
])
def test_create_project_with_autofilling_fields(
        superuser_client, forbidden_key, project_json
):
    project_json.update(forbidden_key)
    response = superuser_client.post(
        PROJECTS_URL,
        json=project_json
    )
    assert response.status_code == 422, (
        'Если в POST-запросе суперпользователя на создание целевого проекта '
        'есть поля, не указанные в спецификации - должен вернуться ответ со '
        'статус-кодом 422.\n'
        'При тестировании кода был отправлен запрос с полем '
        f'`{list(forbidden_key.keys())[0]}`. '
        f'Получен код ответа {response.status_code}.'
    )


@pytest.mark.parametrize(
    'invalid_full_amount',
    [
        -100,
        0.5,
        'test',
        0.0,
        '',
        None,
    ],
)
def test_create_invalid_full_amount_value(
        superuser_client, invalid_full_amount, project_json
):
    project_json['full_amount'] = invalid_full_amount
    response = superuser_client.post(PROJECTS_URL, json=project_json)
    assert response.status_code == 422, (
        f'Убедитесь, что в POST-запросе к эндпоинту `{PROJECTS_URL}` поле '
        '`full_amount` (требуемая сумма проекта) принимает только '
        'целочисленные положительные значения.\n'
        'При запросе суперпользователя, где значением поля `full_amount` было '
        f'`{invalid_full_amount}`, вернулся ответ со статус-кодом '
        f'{response.status_code}. Ожидаемый код ответа - 422.'
    )


@pytest.mark.usefixtures('charity_project')
def test_get_charity_project(user_client):
    response = user_client.get(PROJECTS_URL)
    assert response.status_code == 200, (
        f'GET-запрос обычного пользователя к эндпоинту `{PROJECTS_URL}` '
        'должен возвращать статус-код 200.'
    )
    response_data = response.json()
    assert isinstance(response_data, list), (
        f'В ответе на GET-запрос к эндпоинту `{PROJECTS_URL}` должен '
        'возвращаться список.'
    )
    assert len(response_data) == 1, (
        f'Убедитесь, что GET-запрос к эндпоинту `{PROJECTS_URL}` возвращает '
        'список всех существующих проектов.'
    )
    first_elem = response_data[0]
    expected_keys = {
        'name',
        'description',
        'full_amount',
        'id',
        'invested_amount',
        'fully_invested',
        'create_date',
    }
    missing_keys = expected_keys - first_elem.keys()
    assert not missing_keys, (
        f'В ответе на GET-запрос к эндпоинту `{PROJECTS_URL}` '
        'в описании объектов не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    response_data[0].pop('close_date', None)
    assert response_data == [
        {
            'create_date': '2010-10-10T00:00:00',
            'description': 'Huge fan of chimichangas. Wanna buy a lot',
            'full_amount': 1000000,
            'fully_invested': False,
            'id': 1,
            'invested_amount': 0,
            'name': 'chimichangas4life',
        }
    ], (
        f'При GET-запросе к эндпоинту `{PROJECTS_URL}` тело ответа API '
        'отличается от ожидаемого.'
    )


@pytest.mark.usefixtures('charity_project', 'charity_project_nunchaku')
def test_get_all_charity_project(user_client):
    response = user_client.get(PROJECTS_URL)
    assert response.status_code == 200, (
        'При запросе перечня проектов должен возвращаться статус-код 200.'
    )
    response_data = response.json()
    assert isinstance(response_data, list), (
        'При запросе перечня проектов должен возвращаться объект типа `list`.'
    )
    assert len(response_data) == 2, (
        f'Убедитесь, что ответ на GET-запрос к эндпоинту `{PROJECTS_URL}` '
        'содержит данные всех существующих проектов.'
    )
    first_elem = response_data[0]
    expected_keys = {
        'name',
        'description',
        'full_amount',
        'id',
        'invested_amount',
        'fully_invested',
        'create_date',
    }
    missing_keys = expected_keys - first_elem.keys()
    assert not missing_keys, (
        f'В ответе на GET-запрос к эндпоинту `{PROJECTS_URL}` не хватает '
        f'следующих ключей: `{"`, `".join(missing_keys)}`'
    )
    [project.pop('close_date', None) for project in response_data]
    assert sorted(response_data, key=lambda x: x['id']) == [
        {
            'create_date': '2010-10-10T00:00:00',
            'description': 'Huge fan of chimichangas. Wanna buy a lot',
            'full_amount': 1000000,
            'fully_invested': False,
            'id': 1,
            'invested_amount': 0,
            'name': 'chimichangas4life',
        },
        {
            'create_date': '2010-10-10T00:00:00',
            'description': 'Nunchaku is better',
            'full_amount': 5000000,
            'fully_invested': False,
            'id': 2,
            'invested_amount': 0,
            'name': 'nunchaku',
        },
    ], (
        f'При GET-запросе к эндпоинту `{PROJECTS_URL}` тело ответа API '
        'отличается от ожидаемого.'
    )


def test_create_charity_project(superuser_client, project_json):
    response = superuser_client.post(PROJECTS_URL, json=project_json)
    assert response.status_code == 200, (
        'Убедитесь, что POST-запрос с корректными данными, отправленный '
        f'суперпользователем к эндпоинту `{PROJECTS_URL}`, возвращает ответ '
        'со статус-кодом 200.'
    )
    data = response.json()
    expected_keys = {
        'name',
        'description',
        'full_amount',
        'id',
        'invested_amount',
        'fully_invested',
        'create_date',
    }
    missing_keys = expected_keys - data.keys()
    assert not missing_keys, (
        'В ответе на корректный POST-запрос суперпользователя к эндпоинту '
        f'`{PROJECTS_URL}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    data.pop('create_date')
    data.pop('close_date', None)
    project_json.update(
        {
            'fully_invested': False,
            'id': 1,
            'invested_amount': 0,
        }
    )
    assert data == project_json, (
        f'При POST-запросе суперпользователя к эндпоинту `{PROJECTS_URL}` '
        'тело ответа API отличается от ожидаемого. Проверьте структуру ответа '
        'и убедитесь, что пустые поля не выводятся в ответе.'
    )


@pytest.mark.parametrize(
    'missing_key',
    [
        'name',
        'description',
        'full_amount',
    ],
)
def test_create_charity_project_with_missing_key(
        missing_key, superuser_client, project_json
):
    project_json.pop(missing_key)
    response = superuser_client.post(PROJECTS_URL, json=project_json)
    assert response.status_code == 422, (
        'Убедитесь, что если в POST-запросе суперпользователя к эндпоинту '
        f'`{PROJECTS_URL}` отсутствует обязательное поле `{missing_key}`, то '
        'возвращается ответ со статус-кодом 422.'
    )
    data = response.json()
    assert 'detail' in data, (
        'В ответе на некорректный POST-запрос суперпользователя к эндпоинту '
        f'`{PROJECTS_URL}` должно содержаться поле `detail`.'
    )


def test_delete_project_usual_user(user_client, charity_project):
    response = user_client.delete(
        PROJECT_DETAILS_URL.format(project_id=charity_project.id))
    assert response.status_code == 403, (
        f'DELETE-запрос к эндпоинту `{PROJECT_DETAILS_URL}` от пользователя, '
        'не являющегося суперюзером, должен вернуть ответ со статус-кодом 403.'
    )


def test_delete_charity_project(superuser_client, charity_project):
    response = superuser_client.delete(
        PROJECT_DETAILS_URL.format(project_id=charity_project.id))
    assert response.status_code == 200, (
        'Корректный DELETE-запрос суперпользователя к эндпоинту '
        f'`{PROJECT_DETAILS_URL}` должен вернуть ответ со статус-кодом 200.'
    )
    data = response.json()
    expected_keys = {
        'name',
        'description',
        'full_amount',
        'id',
        'invested_amount',
        'fully_invested',
        'create_date',
    }
    missing_keys = expected_keys - data.keys()
    assert not missing_keys, (
        'В ответе на DELETE-запрос суперпользователя к эндпоинту '
        f'`{PROJECT_DETAILS_URL}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )


def test_delete_charity_project_invalid_id(superuser_client):
    response = superuser_client.delete(
        PROJECT_DETAILS_URL.format(project_id=99983))
    assert response.status_code == 404, (
        'Если в DELETE-запросе суперпользователя к эндпоинту '
        f'`{PROJECT_DETAILS_URL}` передан id несуществующего проекта - должен '
        'вернуться ответ со статус-кодом 404.'
    )
    data = response.json()
    assert 'detail' in data, (
        'Ответ на некорректный DELETE-запрос суперпользователя к эндпоинту '
        f'`{PROJECT_DETAILS_URL}` должен содержать поле `detail`'
    )


@pytest.mark.parametrize(
    'json_data, expected_data',
    [
        (
            {'full_amount': 10},
            {
                'name': 'chimichangas4life',
                'description': 'Huge fan of chimichangas. Wanna buy a lot',
                'full_amount': 10,
                'id': 1,
                'invested_amount': 0,
                'fully_invested': False,
                'create_date': '2010-10-10T00:00:00',
            },
        ),
        (
            {'name': 'chimi'},
            {
                'name': 'chimi',
                'description': 'Huge fan of chimichangas. Wanna buy a lot',
                'full_amount': 1000000,
                'id': 1,
                'invested_amount': 0,
                'fully_invested': False,
                'create_date': '2010-10-10T00:00:00',
            },
        ),
        (
            {'description': 'Give me the money!'},
            {
                'name': 'chimichangas4life',
                'description': 'Give me the money!',
                'full_amount': 1000000,
                'id': 1,
                'invested_amount': 0,
                'fully_invested': False,
                'create_date': '2010-10-10T00:00:00',
            },
        ),
    ],
)
def test_update_charity_project(
        superuser_client, charity_project, json_data, expected_data
):
    response = superuser_client.patch(
        PROJECT_DETAILS_URL.format(project_id=charity_project.id),
        json=json_data
    )
    assert response.status_code == 200, (
        f'Корректный PATCH-запрос к эндпоинту `{PROJECT_DETAILS_URL}` должен '
        'вернуть ответ со статус-кодом 200.'
    )
    response_data = response.json()
    expected_keys = {
        'name',
        'description',
        'full_amount',
        'id',
        'invested_amount',
        'fully_invested',
        'create_date',
    }
    missing_keys = expected_keys - response_data.keys()
    assert not missing_keys, (
        f'В ответе на GET-запрос к эндпоинту `{PROJECT_DETAILS_URL}` не '
        f'хватает следующих ключей: `{"`, `".join(missing_keys)}`'
    )
    response_data.pop('close_date', None)
    assert response_data == expected_data, (
        f'Тело ответа на PATCH-запрос к эндпоинту `{PROJECT_DETAILS_URL}` '
        'отличается от ожидаемого. Проверьте структуру ответа и убедитесь, '
        'что пустые поля не выводятся в ответе.'
    )


@pytest.mark.parametrize('shift', [0, 1])
def test_update_charity_project_full_amount_ge_invested_amount(
        superuser_client, charity_project_little_invested, shift
):
    json_data = {
        'full_amount': (
            charity_project_little_invested.invested_amount + shift
        )
    }
    response = superuser_client.patch(
        PROJECT_DETAILS_URL.format(
            project_id=charity_project_little_invested.id),
        json=json_data,
    )
    assert response.status_code == 200, (
        'Убедитесь, что при редактировании проекта разрешено устанавливать '
        'требуемую сумму больше или равную внесённой. Соответствующий '
        f'PATCH-запрос суперпользователя к эндпоинту `{PROJECT_DETAILS_URL}` '
        'должен вернуть ответ со статус-кодом 200.'
    )
    response_data = response.json()
    assert response_data.get('full_amount') == json_data['full_amount'], (
        'Убедитесь, что при редактировании проекта разрешено устанавливать '
        'требуемую сумму больше или равную внесённой. '
        'Убедитесь, что корректный PATCH-запрос суперпользователя к эндпоинту '
        f'`{PROJECT_DETAILS_URL}` изменяет значение поля `full_amount`.'
    )
    if not shift:
        assert response_data.get('fully_invested'), (
            'Если при PACH-запросе суперпользователя на редактирование '
            'целевого проекта значение поля `full_amount` будет установлено '
            'равным внесённой сумме, то в ответе на запрос должно быть '
            'передано поле `fully_invested` со значением True.'
        )
        project_closed_date = response_data.get('close_date')
        assert project_closed_date, (
            'Если при PACH-запросе суперпользователя на редактирование '
            'целевого проекта значение поля `full_amount` будет установлено '
            'равным внесённой сумме, то в ответе на запрос должно быть '
            'передано поле `close_date` с датой закрытия проекта.'
        )


@pytest.mark.parametrize(
    'json_data',
    [
        {'description': ''},
        {'name': ''},
        {'full_amount': ''},
    ],
)
def test_update_charity_project_invalid(
        superuser_client, charity_project, json_data
):
    response = superuser_client.patch(
        PROJECT_DETAILS_URL.format(project_id=charity_project.id),
        json=json_data
    )
    assert response.status_code == 422, (
        'Убедитесь, что при редактировании проекта запрещено назначать пустое '
        'имя, описание или требуемую сумму. Подобный PATCH-запрос '
        f'суперпользователя к эндпоинту `{PROJECT_DETAILS_URL}` должен '
        'вернуть статус-код 422.'
    )


@pytest.mark.parametrize(
    'json_data',
    [
        {'invested_amount': 100},
        {'create_date': '2010-10-10'},
        {'close_date': '2010-10-10'},
        {'fully_invested': True},
    ],
)
def test_update_charity_with_unexpected_fields(
        superuser_client, charity_project, json_data
):
    response = superuser_client.patch(
        PROJECT_DETAILS_URL.format(project_id=charity_project.id),
        json=json_data
    )
    assert response.status_code == 422, (
        'Убедитесь, что при редактировании проекта невозможно изменить '
        'значения полей, редактирование которых не предусмотрено '
        'спецификацией к API. '
        'Если в PATCH-запросе суперпользователя к эндпоинту '
        f'`{PROJECT_DETAILS_URL}` переданы значения для таких полей - должен '
        'вернуться ответ со статус-кодом 422.'
    )


def test_update_charity_project_same_name(
        superuser_client, charity_project, charity_project_nunchaku
):
    response = superuser_client.patch(
        PROJECT_DETAILS_URL.format(project_id=charity_project.id),
        json={
            'name': charity_project_nunchaku.name,
        }
    )
    assert response.status_code == 400, (
        'Если PATCH-запрос суперпользователя к эндпоинту '
        f'`{PROJECT_DETAILS_URL}` присваивает проекту название другого '
        'существующего проекта - должен вернуться ответ со статус-кодом 400.'
    )
    assert 'detail' in response.json(), (
        'Если PATCH-запрос суперпользователя к эндпоинту '
        f'`{PROJECT_DETAILS_URL}` присваивает проекту название другого '
        'существующего проекта - в ответе должен быть ключ `detail` с '
        'описанием ошибки.'
    )


@pytest.mark.parametrize('full_amount', [0, 5])
def test_update_charity_project_full_amount_smaller_already_invested(
        superuser_client, charity_project_little_invested, full_amount
):
    full_amount = (
        full_amount if not full_amount
        else charity_project_little_invested.invested_amount - full_amount
    )
    response = superuser_client.patch(
        PROJECT_DETAILS_URL.format(
            project_id=charity_project_little_invested.id),
        json={'full_amount': full_amount}
    )
    assert response.status_code in (400, 422), (
        'Убедитесь, что при редактировании проекта запрещено устанавливать '
        'требуемую сумму меньше внесённой.'
    )


def test_create_charity_project_usual_user(user_client, project_json):
    response = user_client.post(PROJECTS_URL, json=project_json)
    assert response.status_code == 403, (
        f'Если POST-запрос к эндпоинту `{PROJECTS_URL}` отправлен не '
        'суперпользователем - должен вернутся ответ со статус-кодом 403.'
    )
    assert 'detail' in response.json(), (
        f'Если POST-запрос к эндпоинту `{PROJECTS_URL}` отправлен не '
        'суперпользователем - в ответе на запрос должен быть ключ `detail`.'
    )


def test_patch_charity_project_usual_user(user_client, charity_project):
    response = user_client.patch(
        PROJECT_DETAILS_URL.format(project_id=charity_project.id),
        json={'full_amount': 1000}
    )
    assert response.status_code == 403, (
        'PATCH-запрос пользователя, не являющегося суперюзером, к эндпоинту '
        f'`{PROJECT_DETAILS_URL}` должен вернуть статус-код 403.'
    )
    data = response.json()
    assert 'detail' in data, (
        'Ответ на PATCH-запрос пользователя, не являющегося суперюзером, к '
        f'эндпоинту `{PROJECT_DETAILS_URL}` должен содержать ключ `detail`.'
    )


def test_patch_charity_project_fully_invested(
        superuser_client, small_fully_invested_charity_project,
):
    response = superuser_client.patch(
        PROJECT_DETAILS_URL.format(
            project_id=small_fully_invested_charity_project.id),
        json={'full_amount': 10}
    )
    common_message_part = (
        f'Если PATCH-запрос к эндпоинту `{PROJECT_DETAILS_URL}` '
        'пытается изменить проект, который был полностью проинвестирован -'
    )
    assert response.status_code == 400, (
        f'{common_message_part} должен вернуться статус-код 400.'
    )
    assert 'detail' in response.json(), (
        f'{common_message_part} ответ должен содержать ключ `detail` с '
        'описанием ошибки.'
    )


def test_patch_charity_project_invalid_id(superuser_client):
    response = superuser_client.patch(
        PROJECT_DETAILS_URL.format(project_id=99987),
        json={'full_amount': 10}
    )
    assert response.status_code == 404, (
        'Если в PATCH-запросе суперпользователя к эндпоинту '
        f'`{PROJECT_DETAILS_URL}` передан id несуществующего проекта - должен '
        'вернуться ответ со статус-кодом 404.'
    )
    data = response.json()
    assert 'detail' in data, (
        'Ответ на некорректный PATCH-запрос суперпользователя к эндпоинту '
        f'`{PROJECT_DETAILS_URL}` должен содержать поле `detail`'
    )


def test_create_charity_project_same_name(
        superuser_client, charity_project, project_json
):
    project_json['name'] = charity_project.name
    response = superuser_client.post(PROJECTS_URL, json=project_json)
    common_messege_part = (
        f'POST-запрос суперпользователя к эндпоинту `{PROJECTS_URL}`, '
        'содержащий неуникальное значение для поля `name`,'
    )
    assert response.status_code == 400, (
        f'{common_messege_part} должен вернуть статус-код 400.'
    )
    assert 'detail' in response.json(), (
        f'В ответе на {common_messege_part} должен быть ключ `detail` с '
        'описанием ошибки.'
    )


def test_create_charity_project_diff_time(superuser_client, project_json):
    response_chimichangs = (
        superuser_client.post(PROJECTS_URL, json=project_json)
    )
    time.sleep(0.01)
    response_nunchaku = superuser_client.post(
        PROJECTS_URL,
        json={
            'name': 'nunchaku',
            'description': 'Nunchaku is better',
            'full_amount': 5000000,
        },
    )
    chimichangas_create_date = response_chimichangs.json()['create_date']
    nunchakus_create_date = response_nunchaku.json()['create_date']
    assert chimichangas_create_date != nunchakus_create_date, (
        'Убедитесь, что при создании двух проектов подряд '
        'время создания этих проектов (значение поля `create_date`) '
        'отличается. Проверьте значение по умолчанию у атрибута `create_date`.'
    )


def test_donation_exist_project_create(
        superuser_client, donation, project_json
):
    not_invested_ammount = donation.full_amount - donation.invested_amount
    project_json['full_amount'] = not_invested_ammount
    response = superuser_client.post(PROJECTS_URL, json=project_json)
    data = response.json()
    common_assert_message_part = (
        'Если при создании проекта существуют нераспределённые пожертвования '
        'в сумме, равной или большей значения поля `full_amount` нового '
        'проекта, то проект должен быть закрыт в момент его создания.'
    )
    assert data['fully_invested'], (
        f'{common_assert_message_part} Убедитесь, что значением поля '
        '`fully_invested` в ответе на POST-запрос суперпользователя к '
        f'эндпоинту `{PROJECTS_URL}` будет `True`.'
    )
    assert 'close_date' in data, (
        f'{common_assert_message_part} Убедитесь, что в ответе на '
        f'POST-запрос суперпользователя к эндпоинту `{PROJECTS_URL}` есть '
        'поле `close_date`.'
    )
    assert data['close_date'] is not None, (
        f'{common_assert_message_part} Убедитесь, что в ответе на '
        f'POST-запрос суперпользователя к эндпоинту `{PROJECTS_URL}` есть '
        'поле `close_date`, содержащее время закрытия проекта.'
    )


def test_delete_charity_project_already_invested(
        superuser_client, charity_project_little_invested
):
    response = superuser_client.delete(
        PROJECT_DETAILS_URL.format(
            project_id=charity_project_little_invested.id)
    )
    assert response.status_code == 400, (
        'Убедитесь, что запрещено удаление проектов, в которые уже '
        'внесены средства. DELETE-запрос суперпользователя к эндпоинту '
        f'`{PROJECT_DETAILS_URL}` на удаление такого проекта '
        'должен вернуть ответ со статус-кодом 400.'
    )
    assert 'detail' in response.json(), (
        'Убедитесь, что запрещено удаление проектов, в которые уже '
        'внесены средства. В ответе на DELETE-запрос суперпользователя к '
        f'эндпоинту `{PROJECT_DETAILS_URL}` на удаление такого проекта '
        'должен быть ключ `detail` с описанием ошибки.'
    )


def test_delete_charity_project_already_closed(
        superuser_client, closed_charity_project
):
    response = superuser_client.delete(
        PROJECT_DETAILS_URL.format(project_id=closed_charity_project.id)
    )
    assert response.status_code == 400, (
        'Убедитесь, что удаление закрытых проектов запрещено. DELETE-запрос '
        f'суперпользователя к эндпоинту `{PROJECT_DETAILS_URL}` на удаление '
        'закрытого проекта должен вернуть ответ со статус-кодом 400.'
    )
    assert 'detail' in response.json(), (
        'Убедитесь, что удаление закрытых проектов запрещено. Ответ на '
        f'DELETE-запрос суперпользователя к эндпоинту `{PROJECT_DETAILS_URL}` '
        'должен содержать ключ `detail` с описанием ошибки.'
    )


@pytest.mark.usefixtures('charity_project', 'charity_project_nunchaku')
def test_get_all_charity_project_not_auth_user(test_client):
    response = test_client.get(PROJECTS_URL)
    assert response.status_code == 200, (
        'GET-запрос незарегистрированного пользователя к эндпоинту '
        f'`{PROJECTS_URL}` должен вернуть ответ со статус-кодом 200.'
    )
    data = response.json()
    [project.pop('close_date', None) for project in data]
    assert sorted(data, key=lambda x: x['id']) == [
        {
            'create_date': '2010-10-10T00:00:00',
            'description': 'Huge fan of chimichangas. Wanna buy a lot',
            'full_amount': 1000000,
            'fully_invested': False,
            'id': 1,
            'invested_amount': 0,
            'name': 'chimichangas4life'
        },
        {
            'create_date': '2010-10-10T00:00:00',
            'description': 'Nunchaku is better',
            'full_amount': 5000000,
            'fully_invested': False,
            'id': 2,
            'invested_amount': 0,
            'name': 'nunchaku'
        }
    ], (
        'Убедитесь, что в ответ на GET-запрос незарегистрированного '
        f'пользователя к эндпоинту `{PROJECTS_URL}` возвращается список '
        'существующих проектов.'
    )
