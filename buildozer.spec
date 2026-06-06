[app]

# Название приложения на телефоне
title = Клик Маркет

# Имя пакета: только латиница, цифры и нижнее подчеркивание
package.name = clickmarket
package.domain = org.nick

# Версия приложения
version = 0.1.0

# Исходники проекта
source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,json,kv,atlas,ttf

# Главный файл приложения должен называться main.py

# Зависимости Python для Android-сборки
requirements = python3,kivy,pillow

# Вертикальный режим телефона
orientation = portrait

# 0 — оставить системную верхнюю строку Android, 1 — полноэкранный режим
fullscreen = 1

# Разрешения. INTERNET оставлен на будущее, если добавишь API/ссылки продавцов.
android.permissions = INTERNET

# Минимальная версия Android. API 23 = Android 6.0.
android.minapi = 24

# Архитектуры. arm64-v8a достаточно для современных телефонов.
android.archs = arm64-v8a

# Иконка приложения. Можно заменить на отдельную app_icon.png.
icon.filename = logo.png

# Логи Kivy при запуске
log_level = 2

# Не обязательно, но удобно для debug-сборки
warn_on_root = 1
