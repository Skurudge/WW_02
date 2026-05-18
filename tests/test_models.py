import pytest
from src.models import Aeroplane


def test_aeroplane_initialization_and_validation():
    """Проверяет корректность инициализации и валидации грязных типов данных."""
    # Успешный случай
    plane = Aeroplane("4b1812", "SWR438A", "Switzerland", 189.7, 4267.2)
    assert plane.icao24 == "4b1812"
    assert plane.velocity == 189.7
    assert isinstance(plane.velocity, float)

    # Случай с None и некорректными строками в числах
    dirty_plane = Aeroplane("4b1812", None, "Switzerland", "не число", None)
    assert dirty_plane.callsign == "UNKNOWN"
    assert dirty_plane.velocity == 0.0
    assert dirty_plane.baro_altitude == 0.0


def test_aeroplane_comparisons():
    """Проверяет корректность работы dunder-методов сравнения самолетов."""
    plane_slow = Aeroplane("111", "AA", "Russia", 100.0, 3000.0)
    plane_fast = Aeroplane("222", "BB", "Russia", 200.0, 5000.0)
    plane_same_speed_higher = Aeroplane("333", "CC", "Russia", 100.0, 4000.0)

    # Проверка базового сравнения по скорости
    assert plane_slow < plane_fast
    assert plane_fast > plane_slow
    assert plane_slow <= plane_fast

    # Проверка сравнения по высоте при равной скорости
    assert plane_slow < plane_same_speed_higher
    assert plane_same_speed_higher > plane_slow

    # Проверка методов явного сравнения по отдельным критериям
    assert plane_fast.is_faster_than(plane_slow)
    assert plane_same_speed_higher.is_higher_than(plane_slow)
