from typing import Any, Optional


class Aeroplane:
    """Класс, представляющий информацию о самолете (Принцип инкапсуляции)."""

    def __init__(
        self, icao24: str, callsign: str, origin_country: str, velocity: Optional[float], baro_altitude: Optional[float]
    ) -> None:
        self.icao24: str = str(icao24).strip()
        self.callsign: str = str(callsign).strip() if callsign else "UNKNOWN"
        self.origin_country: str = str(origin_country).strip()

        # Валидация числовых атрибутов для защиты от программных ошибок
        self.velocity: float = self._validate_float(velocity)
        self.baro_altitude: float = self._validate_float(baro_altitude)

    def _validate_float(self, value: Any) -> float:
        """Внутренний метод валидации типов для числовых данных."""
        if value is None:
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    # Метод сравнения по умолчанию: сначала сравниваем по скорости, а если она равна — по высоте
    def __lt__(self, other: "Aeroplane") -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        if self.velocity != other.velocity:
            return self.velocity < other.velocity
        return self.baro_altitude < other.baro_altitude

    def __le__(self, other: "Aeroplane") -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        if self.velocity != other.velocity:
            return self.velocity <= other.velocity
        return self.baro_altitude <= other.baro_altitude

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.velocity == other.velocity and self.baro_altitude == other.baro_altitude

    # Специальные методы для явного сравнения по отдельным критериям (потребуются для сортировок)
    def is_higher_than(self, other: "Aeroplane") -> bool:
        """Сравнивает самолеты строго по высоте полета."""
        return self.baro_altitude > other.baro_altitude

    def is_faster_than(self, other: "Aeroplane") -> bool:
        """Сравнивает самолеты строго по скорости полета."""
        return self.velocity > other.velocity

    def __repr__(self) -> str:
        return (
            f"Aeroplane(Борт: {self.icao24}, Рейс: {self.callsign}, "
            f"Страна: {self.origin_country}, Скорость: {self.velocity} м/с, Высота: {self.baro_altitude} м)"
        )
