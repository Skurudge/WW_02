import os
import pytest
from src.models import Aeroplane
from src.storage import JSONStorage


@pytest.fixture
def temp_storage(tmp_path):
    """Фикстура для создания изолированного временного JSON-файла хранилища."""
    file_path = tmp_path / "test_aeroplanes.json"
    return JSONStorage(str(file_path))


def test_add_and_get_aeroplanes(temp_storage):
    """Проверяет добавление объекта самолета в файл и его последующее чтение."""
    plane = Aeroplane("4b1812", "SWR438A", "Switzerland", 189.7, 4267.2)

    # Изначально хранилище пустое
    assert len(temp_storage.get_all_aeroplanes()) == 0

    # Добавляем самолет
    temp_storage.add_aeroplane(plane)
    all_planes = temp_storage.get_all_aeroplanes()

    assert len(all_planes) == 1
    assert all_planes[0]["icao24"] == "4b1812"
    assert all_planes[0]["callsign"] == "SWR438A"


def test_delete_aeroplane(temp_storage):
    """Проверяет корректность работы механизма удаления данных из файла."""
    plane_1 = Aeroplane("111", "AA", "Russia", 100.0, 3000.0)
    plane_2 = Aeroplane("222", "BB", "Russia", 200.0, 5000.0)

    temp_storage.add_aeroplane(plane_1)
    temp_storage.add_aeroplane(plane_2)
    assert len(temp_storage.get_all_aeroplanes()) == 2

    # Удаляем первый самолет
    delete_result = temp_storage.delete_aeroplane("111")
    assert delete_result is True

    all_planes = temp_storage.get_all_aeroplanes()
    assert len(all_planes) == 1
    assert all_planes[0]["icao24"] == "222"

    # Пытаемся удалить несуществующий самолет
    delete_false_result = temp_storage.delete_aeroplane("999")
    assert delete_false_result is False
