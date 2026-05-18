import pytest
from unittest.mock import patch, MagicMock
from src.api import FlightAPIAdapter


@pytest.fixture
def api_adapter():
    """Фикстура для初始化 класса адаптера API."""
    return FlightAPIAdapter()


@patch("requests.get")
def test_get_aeroplanes_success(mock_get, api_adapter):
    """Проверяет успешный сквозной сценарий работы обоих API."""
    # Настраиваем мок для первого запроса (Nominatim OpenStreetMap)
    mock_nominatim_response = MagicMock()
    mock_nominatim_response.status_code = 200
    mock_nominatim_response.json.return_value = [{"boundingbox": ["41.67", "83.33", "-141.00", "-52.32"]}]

    # Настраиваем мок для второго запроса (OpenSky Network)
    mock_opensky_response = MagicMock()
    mock_opensky_response.status_code = 200
    mock_opensky_response.json.return_value = {
        "time": 1766142246,
        "states": [
            [
                "4b1812",
                "SWR438A ",
                "Switzerland",
                1766166618,
                1766166618,
                -0.01,
                51.08,
                4267.2,
                False,
                189.7,
                129.39,
                14.63,
                None,
                4282.44,
                "2061",
                False,
                0,
            ]
        ],
    }

    # Имитируем последовательные ответы requests.get
    mock_get.side_effect = [mock_nominatim_response, mock_opensky_response]

    result = api_adapter.get_aeroplanes("Canada")

    assert result is not None
    assert "states" in result
    # Проверяем, что вернулись именно данные от мока (длина позывного оригинальная)
    assert result["states"][0][1] == "SWR438A "
    assert mock_get.call_count == 2


@patch("requests.get")
def test_get_aeroplanes_country_not_found(mock_get, api_adapter):
    """Проверяет переход на модельные данные, если страна не найдена в гео-базе."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []  # Страна не найдена

    mock_get.return_value = mock_response

    result = api_adapter.get_aeroplanes("NonExistentCountry")

    # Теперь мы ожидаем, что сработает честный демонстрационный режим
    assert result is not None
    assert "states" in result
    assert len(result["states"]) == 5
    assert result["states"][0][0] == "4b1812"  # Проверяем ID первого демонстрационного борта


@patch("requests.get")
def test_get_aeroplanes_opensky_failure(mock_get, api_adapter):
    """Проверяет переход на модельные данные при падении сервера OpenSky."""
    mock_nominatim_response = MagicMock()
    mock_nominatim_response.status_code = 200
    mock_nominatim_response.json.return_value = [{"boundingbox": ["41.67", "83.33", "-141.00", "-52.32"]}]

    mock_opensky_response = MagicMock()
    mock_opensky_response.status_code = 500  # Сервер упал

    mock_get.side_effect = [mock_nominatim_response, mock_opensky_response]

    result = api_adapter.get_aeroplanes("Canada")

    # Ожидаем включение демонстрационного режима вместо падения системы
    assert result is not None
    assert "states" in result
    assert len(result["states"]) == 5
