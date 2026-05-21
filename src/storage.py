import json
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.models import Aeroplane


class BaseStorage(ABC):
    """Абстрактный класс для управления хранилищем данных о самолетах (Принцип OCP)."""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавляет информацию о самолете в хранилище."""
        pass

    @abstractmethod
    def get_all_aeroplanes(self) -> List[Dict[str, Any]]:
        """Возвращает список всех самолетов из хранилища."""
        pass

    @abstractmethod
    def delete_aeroplane(self, icao24: str) -> bool:
        """Удаляет информацию о самолете из хранилища по его уникальному ID (icao24)."""
        pass


class JSONStorage(BaseStorage):
    """Коннектор для работы с данными в плоских JSON-файлах (Принцип SRP)."""

    def __init__(self, file_path: str = "data/aeroplanes.json") -> None:
        self.file_path: str = file_path
        # Автоматически создаем папку для данных, если её нет
        dir_name = os.path.dirname(self.file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

    def _read_file(self) -> List[Dict[str, Any]]:
        """Внутренний безопасный метод чтения файла с обработкой исключений."""
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return []

    def _write_file(self, data: List[Dict[str, Any]]) -> None:
        """Внутренний безопасный метод записи файла."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError:
            pass

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавляет самолет в JSON-файл. Если борт уже существует, обновляет его данные."""
        data = self._read_file()

        # Формируем сериализуемый словарь из объекта модели
        plane_dict = {
            "icao24": aeroplane.icao24,
            "callsign": aeroplane.callsign,
            "origin_country": aeroplane.origin_country,
            "velocity": aeroplane.velocity,
            "baro_altitude": aeroplane.baro_altitude,
        }

        # Проверяем, нет ли уже самолета с таким же icao24 в файле
        for i, item in enumerate(data):
            if item.get("icao24") == aeroplane.icao24:
                data[i] = plane_dict  # Обновляем данные существующего борта
                break
        else:
            data.append(plane_dict)  # Если борт новый, добавляем в список

        self._write_file(data)

    def get_all_aeroplanes(self) -> List[Dict[str, Any]]:
        """Возвращает список всех сохраненных самолетов."""
        return self._read_file()

    def delete_aeroplane(self, icao24: str) -> bool:
        """Удаляет самолет из JSON-файла по идентификатору icao24."""
        data = self._read_file()
        initial_count = len(data)

        # Фильтруем данные, исключая удаляемый борт
        data = [item for item in data if item.get("icao24") != icao24]

        if len(data) < initial_count:
            self._write_file(data)
            return True  # Успешно удалено
        return False  # Борт с таким ID не найден
