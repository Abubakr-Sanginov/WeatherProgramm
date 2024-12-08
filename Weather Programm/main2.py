import flet as ft
import requests
import datetime
import threading
import time

def main(page: ft.Page):
    page.title = "Погодная программа"

    # Настройка темы
    page.theme_mode = 'light'
    page.theme = ft.Theme(color_scheme_seed=ft.colors.GREEN)
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Функция для получения цвета текста на основе темы
    def get_text_color():
        return ft.colors.BLACK if page.theme_mode == 'light' else ft.colors.WHITE

    # Поле для ввода города
    user_data = ft.TextField(
        label='Введите город',
        width=400,
        border_color=ft.colors.GREEN_800,
        focused_border_color=ft.colors.GREEN_600,
        prefix_icon=ft.icons.LOCATION_CITY,
        color=get_text_color()  # Задаем цвет текста при создании
    )

    # Текст для отображения погоды
    weather_data = ft.Column([], spacing=5, alignment=ft.MainAxisAlignment.CENTER)

    # Список для отображения данных прогноза
    forecast_list = ft.ListView(
        expand=True,
        spacing=10,
        padding=10,
        auto_scroll=True,
    )

    # Функция для получения погоды
    def get_weather_data(period):
        if len(user_data.value) < 2:
            show_temporary_message(ft.icons.WARNING, "Пожалуйста, введите название города.")
            return

        city = user_data.value
        API = 'cb5321bde0225986dc5558b89f2b3069'
        
        if period == "today":
            URL = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric&lang=ru'
        else:
            URL = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API}&units=metric&lang=ru'

        try:
            res = requests.get(URL).json()
        except requests.exceptions.RequestException:
            show_temporary_message(ft.icons.ERROR, "Нет подключения к интернету.")
            return

        # Очищаем предыдущие данные о погоде и прогнозе
        weather_data.controls.clear()
        forecast_list.controls.clear()

        # Обработка погоды на сегодня
        if period == "today":
            if "main" in res:
                temp = res['main']['temp']
                feels_like = res['main']['feels_like']
                humidity = res['main']['humidity']
                pressure = res['main']['pressure']
                wind_speed = res['wind']['speed']
                visibility = res.get('visibility', 'N/A')
                country = res['sys']['country']
                city = res['name']
                description = res['weather'][0]['description']

                sunrise_timestamp = res['sys']['sunrise']
                sunset_timestamp = res['sys']['sunset']
                sunrise = datetime.datetime.fromtimestamp(sunrise_timestamp).strftime('%H:%M:%S')
                sunset = datetime.datetime.fromtimestamp(sunset_timestamp).strftime('%H:%M:%S')

                # Обновляем текст погоды с полной информацией
                weather_data.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(ft.Text(f"{city}, {country}", size=24, weight="bold", color=get_text_color()), alignment=ft.alignment.center),
                                ft.Container(
                                    ft.Row(
                                        [
                                            ft.Icon(ft.icons.THERMOSTAT, size=24),
                                            ft.Text(f"Температура: {temp}°C", size=18, color=get_text_color())
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    )
                                ),
                                ft.Container(
                                    ft.Row(
                                        [
                                            ft.Icon(ft.icons.EMOJI_EMOTIONS, size=24),
                                            ft.Text(f"Ощущается как: {feels_like}°C", size=18, color=get_text_color())
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    )
                                ),
                                ft.Container(
                                    ft.Row(
                                        [
                                            ft.Icon(ft.icons.WATER_DROP, size=24),
                                            ft.Text(f"Влажность: {humidity}%", size=18, color=get_text_color())
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    )
                                ),
                                ft.Container(
                                    ft.Row(
                                        [
                                            ft.Icon(ft.icons.SPEED, size=24),
                                            ft.Text(f"Давление: {pressure} hPa", size=18, color=get_text_color())
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    )
                                ),
                                ft.Container(
                                    ft.Row(
                                        [
                                            ft.Icon(ft.icons.AIR, size=24),
                                            ft.Text(f"Ветер: {wind_speed} м/с", size=18, color=get_text_color())
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    )
                                ),
                                ft.Container(
                                    ft.Row(
                                        [
                                            ft.Icon(ft.icons.VISIBILITY, size=24),
                                            ft.Text(f"Видимость: {visibility} м", size=18, color=get_text_color())
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    )
                                ),
                                ft.Container(
                                    ft.Row(
                                        [
                                            ft.Icon(ft.icons.WB_SUNNY, size=24),
                                            ft.Text(f"Восход: {sunrise}", size=18, color=get_text_color())
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    )
                                ),
                                ft.Container(
                                    ft.Row(
                                        [
                                            ft.Icon(ft.icons.NIGHT_SHELTER, size=24),
                                            ft.Text(f"Закат: {sunset}", size=18, color=get_text_color())
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    )
                                ),
                                ft.Container(
                                    ft.Row(
                                        [
                                            ft.Icon(ft.icons.DESCRIPTION, size=24),
                                            ft.Text(f"Описание: {description}", size=18, color=get_text_color())
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    )
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        padding=ft.padding.all(10),
                    )
                )
            else:
                show_temporary_message(ft.icons.ERROR, "Введен неправильный город, пожалуйста, введите правильный.")
        
        # Обработка прогноза на несколько дней
        elif period in ["tomorrow", "10days"]:
            if "list" in res:
                forecast_days = 2 if period == "tomorrow" else 10
                for i in range(forecast_days):
                    dt_txt = res["list"][i]["dt_txt"]
                    temp = res["list"][i]["main"]["temp"]
                    description = res["list"][i]["weather"][0]["description"]
                    wind_speed = res["list"][i]["wind"]["speed"]
                    humidity = res["list"][i]["main"]["humidity"]
                    pressure = res["list"][i]["main"]["pressure"]

                    forecast_list.controls.append(
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.WB_SUNNY, size=40, color=ft.colors.ORANGE),
                                    ft.Column(
                                        [
                                            ft.Text(f"{dt_txt}", size=16, weight="bold", color=get_text_color()),
                                            ft.Text(f"Температура: {temp}°C, Описание: {description}", color=get_text_color()),
                                            ft.Text(f"Ветер: {wind_speed} м/с, Влажность: {humidity}%, Давление: {pressure} hPa", color=get_text_color()),
                                        ]
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            padding=ft.padding.all(10),
                            bgcolor=ft.colors.LIGHT_GREEN_100 if page.theme_mode == 'light' else ft.colors.LIGHT_GREEN_800,
                            border_radius=8,
                        )
                    )
                page.update()  # Обновляем страницу после добавления прогноза
            else:
                show_temporary_message(ft.icons.ERROR, "Не удалось получить данные о прогнозе погоды.")
        
        page.update()

    # Функция для временного отображения ошибок с анимацией
    def show_temporary_message(icon, message, timeout=5):
        message_container = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=ft.colors.RED, size=30),
                    ft.Text(message, size=18, color=ft.colors.RED, weight="bold"),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            padding=ft.padding.all(10),
            bgcolor=ft.colors.YELLOW_200,
            border_radius=8,
        )
        
        # Добавляем временное сообщение и запускаем таймер на удаление
        page.add(message_container)
        page.update()
        
        # Удаление сообщения через таймер
        def fade_out():
            page.remove(message_container)
            page.update()
        
        threading.Timer(timeout, fade_out).start()

    # Функция для смены темы и обновления всех текстов на странице
    def change_theme(e):
        page.theme_mode = 'light' if page.theme_mode == 'dark' else 'dark'
        
        # Обновляем цвет текста для поля ввода
        user_data.color = get_text_color()

        # Обновляем цвет текста в погодных данных
        if weather_data.controls:
            for control in weather_data.controls:
                if isinstance(control, ft.Container):
                    for sub_control in control.content.controls:
                        if isinstance(sub_control, ft.Text):
                            sub_control.color = get_text_color()

        # Обновляем цвет текста в прогнозе
        if forecast_list.controls:
            for item in forecast_list.controls:
                if isinstance(item, ft.Container) and isinstance(item.content, ft.Row):
                    for sub_item in item.content.controls:
                        if isinstance(sub_item, ft.Text):
                            sub_item.color = get_text_color()

        page.update()

    # Кнопки управления прогнозом
    def create_weather_buttons():
        buttons = ft.Row(
            [
                ft.ElevatedButton(
                    text="Сегодня",
                    icon=ft.icons.WB_SUNNY,
                    on_click=lambda e: get_weather_data("today"),
                ),
                ft.ElevatedButton(
                    text="Завтра",
                    icon=ft.icons.CLOUD_QUEUE,
                    on_click=lambda e: get_weather_data("tomorrow"),
                ),
                ft.ElevatedButton(
                    text="10 дней",
                    icon=ft.icons.DATE_RANGE,
                    on_click=lambda e: get_weather_data("10days"),
                )
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER
        )
        return buttons

    # Добавляем элементы на страницу
    page.add(
        ft.Row(
            [ft.IconButton(ft.icons.BRIGHTNESS_6, on_click=change_theme)],
            alignment=ft.MainAxisAlignment.END
        ),
        ft.Row(
            [ft.Text('Погодная программа', size=30, color=get_text_color())],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        ft.Row([user_data], alignment=ft.MainAxisAlignment.CENTER),
        create_weather_buttons(),  # Кнопки для выбора прогноза
        weather_data,  # Текущая погода
        forecast_list  # Список для отображения прогноза
    )

ft.app(target=main)