import sys
from typing import List
from src.api import FlightAPIAdapter
from src.models import Aeroplane
from src.storage import JSONStorage


def display_menu() -> None:
    """Выводит интерактивное меню пользователя в консоль."""
    print("\n" + "=" * 50)
    print("✈️  СИСТЕМА МОНИТОРИНГА ВОЗДУШНОГО ПРОСТРАНСТВА  ✈️")
    print("=" * 50)
    print("1. Запросить данные по стране и обновить базу данных")
    print("2. Показать ТОП-N самолетов по высоте полета (DESC)")
    print("3. Найти самолеты по стране их регистрации")
    print("4. Найти самый быстрый самолет в воздушном пространстве")
    print("5. Показать все сохраненные самолеты")
    print("0. Выход из программы")
    print("=" * 50)


def load_planes_from_storage(storage: JSONStorage) -> List[Aeroplane]:
    """Вспомогательная функция для загрузки и восстановления объектов из файла."""
    raw_data = storage.get_all_aeroplanes()
    planes = []
    for item in raw_data:
        planes.append(
            Aeroplane(
                icao24=item.get("icao24", ""),
                callsign=item.get("callsign", ""),
                origin_country=item.get("origin_country", ""),
                velocity=item.get("velocity"),
                baro_altitude=item.get("baro_altitude"),
            )
        )
    return planes


def user_interactive_loop() -> None:
    """Основной цикл взаимодействия с пользователем через консоль."""
    api_client = FlightAPIAdapter()
    storage = JSONStorage("data/aeroplanes.json")

    while True:
        display_menu()
        choice = input("Выберите действие (0-5): ").strip()

        if choice == "1":
            country = input("🌍 Введите название страны на английском (например, Canada): ").strip()
            if not country:
                print("❌ Название страны не может быть пустым.")
                continue

            print(f"🛰️  Запрос географических границ и поиск самолетов для: {country}...")
            raw_response = api_client.get_aeroplanes(country)

            if not raw_response or "states" not in raw_response or raw_response["states"] is None:
                print(f"⚠️  В воздушном пространстве {country} сейчас нет самолетов или страна указана неверно.")
                continue

            states_list = raw_response["states"]
            print(f"📊 Найдено бортов в небе: {len(states_list)}. Сохранение в базу данных...")

            # Парсим сырые данные в объекты и сохраняем на диск
            saved_count = 0
            for state in states_list:
                # Согласно индексам OpenSky API: 0 - icao24, 1 - callsign, 2 - origin_country, 7 - baro_altitude, 9 - velocity
                if len(state) >= 10:
                    plane_obj = Aeroplane(
                        icao24=state[0],
                        callsign=state[1],
                        origin_country=state[2],
                        velocity=state[9],
                        baro_altitude=state[7],
                    )
                    storage.add_aeroplane(plane_obj)
                    saved_count += 1
            print(f"✅ Успешно сохранено и обновлено бортов: {saved_count}")

        elif choice == "2":
            planes = load_planes_from_storage(storage)
            if not planes:
                print("📂 База данных пуста. Сначала выполните запрос (Пункт 1).")
                continue

            try:
                n_input = input(f"🔢 Введите количество самолетов для вывода (всего доступно {len(planes)}): ").strip()
                n = int(n_input)
                if n <= 0:
                    print("❌ Число N должно быть больше нуля.")
                    continue
            except ValueError:
                print("❌ Пожалуйста, введите корректное целое число.")
                continue

            # Сортировка по высоте по убыванию (DESC) с использованием встроенной логики сравнения
            sorted_by_altitude = sorted(planes, key=lambda p: p.baro_altitude, reverse=True)
            top_n = sorted_by_altitude[:n]

            print(f"\n🔝 ТОП-{len(top_n)} САМОЛЕТОВ ПО ВЫСОТЕ ПОЛЕТА (DESC):")
            for i, p in enumerate(top_n, 1):
                print(
                    f"{i}. Рейс {p.callsign} ({p.origin_country}) ➡️  Высота: {p.baro_altitude} м | Скорость: {p.velocity} м/с [ID: {p.icao24}]"
                )

        elif choice == "3":
            planes = load_planes_from_storage(storage)
            if not planes:
                print("📂 База данных пуста. Сначала выполните запрос.")
                continue

            search_country = input(
                "🔍 Введите страну регистрации самолета для фильтрации (например, Switzerland): "
            ).strip()
            # Фильтрация нечувствительна к регистру
            filtered_planes = [p for p in planes if p.origin_country.lower() == search_country.lower()]

            if not filtered_planes:
                print(f"❌ Самолетов, зарегистрированных в '{search_country}', в текущей базе данных не найдено.")
            else:
                print(f"\n📋 НАЙДЕННЫЕ САМОЛЕТЫ С РЕГИСТРАЦИЕЙ В '{search_country}' (Всего: {len(filtered_planes)}):")
                for i, p in enumerate(filtered_planes, 1):
                    print(
                        f"{i}. [Борт {p.icao24}] Рейс: {p.callsign} | Скорость: {p.velocity} м/с | Высота: {p.baro_altitude} м"
                    )

        elif choice == "4":
            # Дополнительный полезный функционал
            planes = load_planes_from_storage(storage)
            if not planes:
                print("📂 База данных пуста.")
                continue

            # Находим самый быстрый самолет, используя метод модели .is_faster_than()
            fastest_plane = planes[0]
            for p in planes[1:]:
                if p.is_faster_than(fastest_plane):
                    fastest_plane = p

            print(f"\n⚡ САМЫЙ БЫСТРЫЙ САМОЛЕТ В ВОЗДУШНОМ ПРОСТРАНСТВЕ:")
            print(f"✈️  Рейс: {fastest_plane.callsign} из страны {fastest_plane.origin_country}")
            print(f"🚀 Скорость: {fastest_plane.velocity} м/с (около {round(fastest_plane.velocity * 3.6)} км/ч)")
            print(f"🏔️  Высота полета: {fastest_plane.baro_altitude} м")

        elif choice == "5":
            planes = load_planes_from_storage(storage)
            if not planes:
                print("📂 База данных пуста.")
                continue
            print(f"\n📋 ВСЕ САМОЛЕТЫ В ХРАНИЛИЩЕ (Всего: {len(planes)}):")
            for i, p in enumerate(planes, 1):
                print(f"{i}. {p}")

        elif choice == "0":
            print("👋 До свидания! Завершение работы программы.")
            sys.exit(0)
        else:
            print("❌ Неверный ввод. Выберите пункт от 0 до 5.")


if __name__ == "__main__":
    user_interactive_loop()
