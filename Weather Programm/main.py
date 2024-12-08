import flet as ft
import requests
from time import sleep

# Основная функция приложения
def main(page: ft.Page):
    page.title = "Погодная программа"
    page.theme_mode = "light"
    page.theme = ft.Theme(color_scheme_seed=ft.colors.GREEN)

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def get_text_color():
        return ft.colors.BLACK if page.theme_mode == "light" else ft.colors.WHITE

    def toggle_theme(e):
        page.theme_mode = "dark" if page.theme_mode == "light" else "light"
        user_input.border_color = (
            ft.colors.YELLOW if page.theme_mode == "dark" else ft.colors.GREEN
        )
        page.update()

    def show_message(message, icon, color):
        snack_bar = ft.SnackBar(
            content=ft.Row([ft.Icon(icon), ft.Text(message, color=color)]),
            bgcolor=ft.colors.YELLOW_200,
        )
        page.overlay.append(snack_bar)  # Вместо page.snack_bar
        snack_bar.open = True
        page.update()

    def set_city_input(city):
        user_input.value = city
        suggestions_list.controls.clear()
        page.update()

    def show_city_suggestions(e):
        query = user_input.value.lower()
        suggestions_list.controls.clear()
        if len(query) >= 2:
            cities = [
                "Душанбе", "Худжанд", "Куляб", "Бохтар", "Хорог", "Турсунзаде", 
                "Пенджикент", "Гиссар", "Исфара", "Канибадам", "Вахдат",
                "Москва", "Минск", "Лондон", "Нью-Йорк", "Париж", "Берлин", "Милан",
                "Мадрид", "Токио", "Шанхай"
            ]
            matched_cities = [city for city in cities if query in city.lower()]
            for city in matched_cities:
                suggestions_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(city),
                        on_click=lambda e, city=city: set_city_input(city),
                    )
                )
        page.update()

    def clear_weather_data():
        today_weather.controls.clear()
        page.update()

    def get_weather(period):
        clear_weather_data()
        city = user_input.value.strip()
        if not city:
            show_message("Введите название города!", ft.icons.ERROR, ft.colors.RED)
            return

        api_key = "cb5321bde0225986dc5558b89f2b3069"

        if period == "today":
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
        elif period == "tomorrow":
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=ru"
        elif period == "10days":
            url = f"https://api.openweathermap.org/data/2.5/forecast/daily?q={city}&cnt=10&appid={api_key}&units=metric&lang=ru"

        for attempt in range(3):
            try:
                response = requests.get(url)
                response.raise_for_status()
                weather_data = response.json()
                print(weather_data)  # Логируем ответ
                display_weather_info(weather_data, period)
                break
            except requests.exceptions.RequestException as e:
                if attempt < 2:
                    show_message(
                        f"Ошибка загрузки данных. Повторная попытка... ({attempt + 1}/3)",
                        ft.icons.WARNING,
                        ft.colors.ORANGE,
                    )
                    sleep(2)
                else:
                    show_message(f"Ошибка: {str(e)}", ft.icons.ERROR, ft.colors.RED)
                    break
            except Exception as e:
                show_message(f"Ошибка: {str(e)}", ft.icons.ERROR, ft.colors.RED)
                break

    def display_weather_info(data, period):
        if "main" not in data and period == "today":
            show_message("Город не найден!", ft.icons.ERROR, ft.colors.RED)
            return

        if period == "today":
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            pressure = data["main"]["pressure"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            description = data["weather"][0]["description"]
            icon_code = data["weather"][0]["icon"]
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

            today_weather.controls.append(
                ft.Column(
                    [
                        ft.Image(src=icon_url, width=100, height=100),
                        ft.Row(
                            [
                                ft.Icon(ft.icons.THERMOSTAT_AUTO),
                                ft.Text(f"Температура: {temp}°C", size=20, weight="bold", color=get_text_color()),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Icon(ft.icons.WB_CLOUDY),
                                ft.Text(f"Ощущается как: {feels_like}°C", size=16, color=get_text_color()),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Icon(ft.icons.AIR),
                                ft.Text(f"Скорость ветра: {wind_speed} м/с", size=16, color=get_text_color()),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Icon(ft.icons.WATER_DROP),
                                ft.Text(f"Влажность: {humidity}%", size=16, color=get_text_color()),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Icon(ft.icons.LINE_WEIGHT),
                                ft.Text(f"Давление: {pressure} гПа", size=16, color=get_text_color()),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Icon(ft.icons.DESCRIPTION),
                                ft.Text(f"Описание: {description}", size=16, color=get_text_color()),
                            ]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )
        page.update()

    user_input = ft.TextField(
        label="Введите город",
        border_color=ft.colors.GREEN,
        focused_border_color=ft.colors.GREEN_600,
        prefix_icon=ft.icons.LOCATION_CITY,
        on_change=show_city_suggestions,
        width=400,
    )

    suggestions_list = ft.ListView(
        height=150,
        spacing=5,
        padding=5,
        auto_scroll=True,
    )

    today_weather = ft.ListView(height=400, spacing=10, padding=5, auto_scroll=True)

    top_bar = ft.Row(
        [
            ft.IconButton(
                icon=ft.icons.BRIGHTNESS_6,
                tooltip="Сменить тему",
                on_click=toggle_theme,
            )
        ],
        alignment=ft.MainAxisAlignment.END,
    )

    control_buttons = ft.Row(
        [
            ft.ElevatedButton(
                "Сегодня",
                icon=ft.icons.WB_SUNNY,
                on_click=lambda _: get_weather("today"),
            ),
            ft.ElevatedButton(
                "Завтра",
                icon=ft.icons.WB_CLOUDY,
                on_click=lambda _: get_weather("tomorrow"),
            ),
            ft.ElevatedButton(
                "10 дней",
                icon=ft.icons.DATE_RANGE,
                on_click=lambda _: get_weather("10days"),
            ),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(
        top_bar,
        ft.Column(
            [
                ft.Text(
                    "Погодная программа", size=30, weight="bold", color=ft.colors.GREEN
                ),
                user_input,
                suggestions_list,
                control_buttons,
                ft.Container(
                    content=ft.Column([today_weather], alignment=ft.MainAxisAlignment.CENTER),
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    height=500,
                    width=400,
                    padding=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

ft.app(target=main)
