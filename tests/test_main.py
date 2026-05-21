import json
import os
from unittest.mock import patch, MagicMock
import pytest
from src.models import Aeroplane
from src.storage import JSONStorage
from main import load_planes_from_storage, user_interactive_loop


@pytest.fixture
def sample_storage_with_data(tmp_path):
    """Фикстура для создания хранилища с тремя тестовыми самолетами."""
    file_path = tmp_path / "test_main_menu.json"
    storage = JSONStorage(str(file_path))

    # Добавляем разнородные самолеты для тестов сортировки и фильтрации
    plane_1 = Aeroplane("111", "SU100", "Russia", 150.0, 9000.0)
    plane_2 = Aeroplane("222", "LX200", "Switzerland", 200.0, 11000.0)
    plane_3 = Aeroplane("333", "SU300", "Russia", 100.0, 4000.0)

    storage.add_aeroplane(plane_1)
    storage.add_aeroplane(plane_2)
    storage.add_aeroplane(plane_3)
    return storage


def test_load_planes_from_storage(tmp_path):
    """Проверяет восстановление списка объектов Aeroplane из хранилища."""
    file_path = tmp_path / "test_main_load.json"
    storage = JSONStorage(str(file_path))

    plane = Aeroplane("4b1812", "SWR438A", "Switzerland", 189.7, 4267.2)
    storage.add_aeroplane(plane)

    planes_list = load_planes_from_storage(storage)
    assert len(planes_list) == 1
    assert isinstance(planes_list[0], Aeroplane)
    assert planes_list[0].icao24 == "4b1812"


@patch("builtins.input")
@patch("src.storage.JSONStorage.get_all_aeroplanes")
def test_main_menu_view_all_and_exit(mock_get_all, mock_input):
    """Тестирует вывод всех самолетов (Пункт 5) и выход (Пункт 0)."""
    mock_get_all.return_value = [
        {"icao24": "111", "callsign": "SU100", "origin_country": "Russia", "velocity": 150.0, "baro_altitude": 9000.0}
    ]
    # Пользователь нажимает 5, затем 0
    mock_input.side_effect = ["5", "0"]

    with pytest.raises(SystemExit):
        user_interactive_loop()


@patch("builtins.input")
@patch("src.storage.JSONStorage.get_all_aeroplanes")
def test_main_menu_top_n_altitude(mock_get_all, mock_input):
    """Тестирует вывод Топ-N самолетов по высоте полета (Пункт 2)."""
    mock_get_all.return_value = [
        {"icao24": "111", "callsign": "SU100", "origin_country": "Russia", "velocity": 150.0, "baro_altitude": 9000.0},
        {
            "icao24": "222",
            "callsign": "LX200",
            "origin_country": "Switzerland",
            "velocity": 200.0,
            "baro_altitude": 11000.0,
        },
    ]
    # Выбираем пункт 2, запрашиваем ТОП-1 самолет, затем нажимаем 0 для выхода
    mock_input.side_effect = ["2", "1", "0"]

    with pytest.raises(SystemExit):
        user_interactive_loop()


@patch("builtins.input")
@patch("src.storage.JSONStorage.get_all_aeroplanes")
def test_main_menu_filter_by_country(mock_get_all, mock_input):
    """Тестирует поиск самолетов по стране их регистрации (Пункт 3)."""
    mock_get_all.return_value = [
        {"icao24": "111", "callsign": "SU100", "origin_country": "Russia", "velocity": 150.0, "baro_altitude": 9000.0},
        {
            "icao24": "222",
            "callsign": "LX200",
            "origin_country": "Switzerland",
            "velocity": 200.0,
            "baro_altitude": 11000.0,
        },
    ]
    # Выбираем пункт 3, ищем "Russia", затем нажимаем 0 для выхода
    mock_input.side_effect = ["3", "Russia", "0"]

    with pytest.raises(SystemExit):
        user_interactive_loop()


@patch("builtins.input")
@patch("src.storage.JSONStorage.get_all_aeroplanes")
def test_main_menu_fastest_plane(mock_get_all, mock_input):
    """Тестирует вывод самого быстрого самолета (Пункт 4)."""
    mock_get_all.return_value = [
        {"icao24": "111", "callsign": "SU100", "origin_country": "Russia", "velocity": 150.0, "baro_altitude": 9000.0},
        {
            "icao24": "222",
            "callsign": "LX200",
            "origin_country": "Switzerland",
            "velocity": 200.0,
            "baro_altitude": 11000.0,
        },
    ]
    # Выбираем пункт 4, затем нажимаем 0 для выхода
    mock_input.side_effect = ["4", "0"]

    with pytest.raises(SystemExit):
        user_interactive_loop()
