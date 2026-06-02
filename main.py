from kivy.app import App
from datetime import datetime
import json
import os
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.graphics.texture import Texture
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import FadeTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

try:
    from PIL import Image as PILImage, ImageSequence
except Exception:
    PILImage = None
    ImageSequence = None


BLACK = (0, 0, 0, 1)
WHITE = (1, 1, 1, 1)
PAGE_BG = (0.965, 0.965, 0.965, 1)
CARD_BG = (1, 1, 1, 1)
BORDER = (0.86, 0.86, 0.86, 1)
TEXT_MUTED = (0.42, 0.42, 0.42, 1)
TEXT_DARK = (0.08, 0.08, 0.08, 1)
NAV_ACTIVE = (0.16, 0.16, 0.16, 1)
PINK = (1, 0.16, 0.38, 1)
PURPLE = (0.32, 0.12, 0.56, 1)


PRODUCTS = [
    {
        "id": 1,
        "name": "Смартфон X Pro",
        "category": "Электроника",
        "price": 13790,
        "source": "WB",
        "description": "Смартфон с ярким экраном, быстрой зарядкой и хорошей камерой.",
    },
    {
        "id": 2,
        "name": "Ноутбук LiteBook 15",
        "category": "Электроника",
        "price": 54990,
        "source": "Ozon",
        "description": "Легкий ноутбук для учебы, работы и ежедневных задач.",
    },
    {
        "id": 3,
        "name": "Беспроводные наушники",
        "category": "Электроника",
        "price": 2990,
        "source": "AliExpress",
        "description": "Компактные наушники с кейсом, микрофоном и быстрым подключением.",
    },
    {
        "id": 4,
        "name": "Футболка Basic",
        "category": "Одежда",
        "price": 990,
        "source": "WB",
        "description": "Базовая хлопковая футболка для повседневного образа.",
    },
    {
        "id": 5,
        "name": "Худи Oversize",
        "category": "Одежда",
        "price": 2490,
        "source": "Ozon",
        "description": "Свободное худи из плотного материала с мягкой внутренней частью.",
    },
    {
        "id": 6,
        "name": "Помада Velvet",
        "category": "Косметика",
        "price": 690,
        "source": "WB",
        "description": "Матовая помада с мягкой текстурой и стойким оттенком.",
    },
    {
        "id": 7,
        "name": "Набор кистей",
        "category": "Косметика",
        "price": 1190,
        "source": "AliExpress",
        "description": "Набор кистей для макияжа лица, глаз и растушевки.",
    },
    {
        "id": 8,
        "name": "Настольная лампа",
        "category": "Для дома",
        "price": 1590,
        "source": "Ozon",
        "description": "Минималистичная лампа для рабочего стола и учебной зоны.",
    },
    {
        "id": 9,
        "name": "Органайзер для стола",
        "category": "Для дома",
        "price": 890,
        "source": "WB",
        "description": "Компактный органайзер для канцелярии, кабелей и мелочей.",
    },
]


CATEGORIES = [
    ("Электроника", "Ноутбуки, смартфоны и гаджеты"),
    ("Одежда", "Базовые вещи и повседневные товары"),
    ("Косметика", "Средства ухода и декоративная косметика"),
    ("Для дома", "Товары для комнаты, стола и уюта"),
]


def asset_path(filename):
    """Возвращает путь к png-файлам, лежащим рядом с main.py."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def bind_adaptive_height(layout):
    layout.size_hint_y = None
    layout.bind(minimum_height=layout.setter("height"))
    return layout


class AppLabel(Label):
    def __init__(
        self,
        text="",
        font_size=14,
        color=TEXT_DARK,
        bold=False,
        halign="left",
        valign="top",
        fixed_height=None,
        **kwargs,
    ):
        self._fixed_height = fixed_height
        super().__init__(
            text=text,
            font_size=dp(font_size),
            color=color,
            bold=bold,
            halign=halign,
            valign=valign,
            size_hint_y=None,
            **kwargs,
        )

        if fixed_height is not None:
            self.height = dp(fixed_height)
        else:
            self.height = dp(1)
            self.bind(texture_size=self._update_height)

        self.bind(width=self._update_text_size)
        Clock.schedule_once(lambda dt: self._update_text_size(), 0)

    def _update_text_size(self, *args):
        max_width = max(self.width, dp(1))
        if self._fixed_height is None:
            self.text_size = (max_width, None)
        else:
            self.text_size = (max_width, self.height)

    def _update_height(self, *args):
        self.height = self.texture_size[1] + dp(3)


class RoundedBox(BoxLayout):
    bg_color = ListProperty(CARD_BG)
    border_color = ListProperty(BORDER)
    border_width = NumericProperty(1)
    radius = NumericProperty(dp(22))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            pos=self._redraw,
            size=self._redraw,
            bg_color=self._redraw,
            border_color=self._redraw,
            border_width=self._redraw,
            radius=self._redraw,
        )

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius],
            )
            if self.border_width > 0:
                Color(*self.border_color)
                Line(
                    rounded_rectangle=(
                        self.x,
                        self.y,
                        self.width,
                        self.height,
                        self.radius,
                    ),
                    width=self.border_width,
                )


class Surface(BoxLayout):
    bg_color = ListProperty(PAGE_BG)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, bg_color=self._redraw)

    def _redraw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            Rectangle(pos=self.pos, size=self.size)


class AppButton(ButtonBehavior, RoundedBox):
    text = StringProperty("")
    text_color = ListProperty(WHITE)
    font_size_value = NumericProperty(14)

    def __init__(self, fixed_width=None, fixed_height=44, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(12), 0, dp(12), 0]
        self.spacing = 0
        self.size_hint_y = None
        self.height = dp(fixed_height)

        if fixed_width is not None:
            self.size_hint_x = None
            self.width = dp(fixed_width)

        self.label = Label(
            text=self.text,
            color=self.text_color,
            font_size=dp(self.font_size_value),
            bold=True,
            halign="center",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        self.label.bind(size=lambda instance, size: setattr(instance, "text_size", size))
        self.add_widget(self.label)

        self.bind(
            text=self._sync_label,
            text_color=self._sync_label,
            font_size_value=self._sync_label,
        )

    def _sync_label(self, *args):
        self.label.text = self.text
        self.label.color = self.text_color
        self.label.font_size = dp(self.font_size_value)

    def on_press(self):
        Animation(opacity=0.62, duration=0.06).start(self)

    def on_release(self):
        Animation(opacity=1, duration=0.14, t="out_quad").start(self)


class LogoMark(RoundedBox):
    def __init__(self, dark=False, size_value=54, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(size_value), dp(size_value))
        self.radius = dp(18)
        self.border_width = 0
        self.bg_color = BLACK if dark else WHITE
        self.padding = [dp(9), dp(9), dp(9), dp(9)]

        logo_file = asset_path("logo.png")

        if os.path.exists(logo_file):
            logo = Image(
                source=logo_file,
                allow_stretch=True,
                keep_ratio=True,
            )
            self.add_widget(logo)
        else:
            # Резервный вариант, если logo.png не найден рядом с main.py.
            label = Label(
                text="КМ",
                color=WHITE if dark else BLACK,
                font_size=dp(18),
                bold=True,
                halign="center",
                valign="middle",
            )
            label.bind(size=lambda instance, size: setattr(instance, "text_size", size))
            self.add_widget(label)


class StatCard(RoundedBox):
    def __init__(self, number, caption, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(12), dp(10), dp(12), dp(10)]
        self.spacing = dp(2)
        self.bg_color = WHITE
        self.border_color = BORDER
        self.radius = dp(16)
        self.size_hint_y = None
        self.height = dp(76)
        self.add_widget(AppLabel(number, font_size=22, bold=True, fixed_height=30))
        self.add_widget(AppLabel(caption, font_size=11, color=TEXT_MUTED, fixed_height=28))


class ProfileSettingToggle(ButtonBehavior, RoundedBox):
    def __init__(self, app_ref, setting_key, title, subtitle, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.setting_key = setting_key
        self.title_text = title
        self.subtitle_text = subtitle
        self.orientation = "horizontal"
        self.padding = [dp(14), dp(12), dp(12), dp(12)]
        self.spacing = dp(12)
        self.bg_color = WHITE
        self.border_color = BORDER
        self.radius = dp(18)
        self.size_hint_y = None
        self.height = dp(82)

        text_box = BoxLayout(orientation="vertical", spacing=dp(2))
        text_box.add_widget(AppLabel(title, font_size=15, bold=True, fixed_height=25))
        text_box.add_widget(AppLabel(subtitle, font_size=12, color=TEXT_MUTED, fixed_height=36))

        icon_anchor = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint=(None, 1),
            width=dp(58),
        )
        self.icon = Image(
            source="",
            size_hint=(None, None),
            size=(dp(48), dp(28)),
            allow_stretch=True,
            keep_ratio=True,
        )
        icon_anchor.add_widget(self.icon)

        self.add_widget(text_box)
        self.add_widget(icon_anchor)
        self._update_icon()

    def _is_enabled(self):
        return bool(self.app_ref.profile_parameters.get(self.setting_key, False))

    def _update_icon(self):
        icon_file = "toggle_on.png" if self._is_enabled() else "toggle_off.png"
        self.icon.source = asset_path(icon_file)
        self.icon.reload()

    def on_press(self):
        Animation(opacity=0.68, duration=0.06).start(self)
        Animation(size=(dp(44), dp(25)), duration=0.06).start(self.icon)

    def on_release(self):
        self.app_ref.toggle_profile_parameter(self.setting_key)
        self._update_icon()
        Animation(opacity=1, duration=0.14, t="out_quad").start(self)
        Animation(size=(dp(48), dp(28)), duration=0.14, t="out_quad").start(self.icon)


class CategoryCard(ButtonBehavior, RoundedBox):
    def __init__(self, app_ref, title, subtitle, active=False, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.title = title
        self.orientation = "vertical"
        self.padding = [dp(14), dp(13), dp(14), dp(13)]
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(106)
        self.radius = dp(18)
        self.bg_color = BLACK if active else WHITE
        self.border_color = BLACK if active else BORDER
        text_color = WHITE if active else BLACK
        muted = (0.82, 0.82, 0.82, 1) if active else TEXT_MUTED
        self.add_widget(AppLabel(title, font_size=15, color=text_color, bold=True))
        self.add_widget(AppLabel(subtitle, font_size=11, color=muted))

    def on_press(self):
        Animation(opacity=0.64, duration=0.06).start(self)

    def on_release(self):
        Animation(opacity=1, duration=0.14).start(self)
        self.app_ref.set_selected_category(self.title)


class FavoriteIconButton(ButtonBehavior, RoundedBox):
    def __init__(self, icon_file, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(7), dp(7), dp(7), dp(7)]
        self.size_hint = (None, None)
        self.size = (dp(42), dp(38))
        self.radius = dp(13)
        self.bg_color = WHITE
        self.border_color = BLACK
        self.border_width = 1

        self.icon = Image(
            source=asset_path(icon_file),
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            allow_stretch=True,
            keep_ratio=True,
        )

        anchor = AnchorLayout(anchor_x="center", anchor_y="center")
        anchor.add_widget(self.icon)
        self.add_widget(anchor)

    def on_press(self):
        Animation(opacity=0.65, duration=0.06).start(self)
        Animation(size=(dp(21), dp(21)), duration=0.06).start(self.icon)

    def on_release(self):
        Animation(opacity=1, duration=0.14, t="out_quad").start(self)
        Animation(size=(dp(24), dp(24)), duration=0.14, t="out_quad").start(self.icon)


class ProductCard(RoundedBox):
    def __init__(self, app_ref, product, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.product = product
        self.orientation = "vertical"
        self.padding = [dp(16), dp(15), dp(16), dp(15)]
        self.spacing = dp(10)
        self.radius = dp(22)
        self.bg_color = WHITE
        self.border_color = BORDER
        bind_adaptive_height(self)

        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(38))
        top.add_widget(
            AppLabel(
                product["category"].upper(),
                font_size=11,
                color=TEXT_MUTED,
                bold=True,
                fixed_height=32,
            )
        )

        is_favorite = product["id"] in app_ref.favorite_ids
        fav_icon = "heart_on.png" if is_favorite else "heart_off.png"
        fav_button = FavoriteIconButton(fav_icon)
        fav_button.bind(on_release=lambda instance: app_ref.toggle_favorite(product["id"]))
        top.add_widget(fav_button)
        self.add_widget(top)

        self.add_widget(AppLabel(product["name"], font_size=20, bold=True))
        self.add_widget(AppLabel(product["description"], font_size=13, color=(0.28, 0.28, 0.28, 1)))

        price_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(34))
        price_row.add_widget(AppLabel(f'{product["price"]} ₽', font_size=23, bold=True, fixed_height=34))
        price_row.add_widget(
            AppLabel(
                product["source"],
                font_size=13,
                color=TEXT_MUTED,
                bold=True,
                halign="right",
                fixed_height=34,
            )
        )
        self.add_widget(price_row)

        actions = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(9))
        cart_button = AppButton(
            text="В корзину",
            bg_color=BLACK,
            text_color=WHITE,
            border_color=BLACK,
            radius=dp(14),
        )
        cart_button.bind(on_release=lambda instance: app_ref.add_to_cart(product["id"]))

        details_button = AppButton(
            text="Подробнее",
            bg_color=WHITE,
            text_color=BLACK,
            border_color=BLACK,
            radius=dp(14),
        )
        actions.add_widget(cart_button)
        actions.add_widget(details_button)
        self.add_widget(actions)


class NavItem(ButtonBehavior, RoundedBox):
    active = BooleanProperty(False)

    def __init__(self, shell, page_name, icon_file, active_icon_file, **kwargs):
        super().__init__(**kwargs)
        self.shell = shell
        self.page_name = page_name
        self.icon_file = icon_file
        self.active_icon_file = active_icon_file
        self.orientation = "vertical"
        self.padding = [dp(10), dp(8), dp(10), dp(8)]
        self.radius = dp(22)
        self.border_width = 0
        self.bg_color = BLACK
        self.size_hint_x = 1

        self.icon_anchor = AnchorLayout(anchor_x="center", anchor_y="center")
        self.icon = Image(
            source=asset_path(icon_file),
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            allow_stretch=True,
            keep_ratio=True,
        )
        self.icon_anchor.add_widget(self.icon)
        self.add_widget(self.icon_anchor)

        self.bind(active=self._update_state)
        self._update_state()

    def _update_state(self, *args):
        # Активная вкладка теперь определяется не обводкой, а отдельной PNG-иконкой *_on.png.
        self.bg_color = BLACK
        self.border_width = 0
        active_source = self.active_icon_file if self.active else self.icon_file
        new_source = asset_path(active_source)
        if self.icon.source != new_source:
            self.icon.source = new_source
            self.icon.reload()
        self.icon.opacity = 1 if self.active else 0.72
        self.icon.size = (dp(34), dp(34)) if self.active else (dp(30), dp(30))

    def on_press(self):
        Animation(opacity=0.68, duration=0.06).start(self)
        Animation(size=(dp(28), dp(28)), duration=0.06).start(self.icon)

    def on_release(self):
        Animation(opacity=1, duration=0.14).start(self)
        target_size = (dp(34), dp(34)) if self.active else (dp(30), dp(30))
        Animation(size=target_size, duration=0.14, t="out_quad").start(self.icon)
        self.shell.open_tab(self.page_name)


class InputBox(RoundedBox):
    def __init__(self, hint_text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(52)
        self.radius = dp(15)
        self.bg_color = WHITE
        self.border_color = BORDER
        self.padding = [dp(14), 0, dp(14), 0]

        self.input = TextInput(
            hint_text=hint_text,
            multiline=False,
            background_normal="",
            background_active="",
            background_color=(1, 1, 1, 0),
            foreground_color=BLACK,
            cursor_color=BLACK,
            font_size=dp(14),
            padding=[0, dp(15), 0, 0],
        )
        self.add_widget(self.input)


class Toast(RoundedBox):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(18), 0, dp(18), 0]
        self.radius = dp(18)
        self.bg_color = BLACK
        self.border_width = 0
        self.size_hint = (None, None)
        self.width = dp(300)
        self.height = dp(48)
        self.opacity = 0
        self.add_widget(
            Label(
                text=text,
                color=WHITE,
                font_size=dp(13),
                bold=True,
                halign="center",
                valign="middle",
                shorten=True,
                shorten_from="right",
            )
        )


class AuthModal(ModalView):
    TEST_CODE = "0000"

    def __init__(self, app_ref, mode="login", **kwargs):
        super().__init__(
            size_hint=(1, 1),
            auto_dismiss=False,
            background_color=(0, 0, 0, 0.55),
            **kwargs,
        )
        self.app_ref = app_ref
        self.mode = mode
        self.auth_payload = {}
        self.error_label = None

        if mode == "login":
            self._build_login_form()
        else:
            self._build_register_form()

    def _modal_card(self, height):
        self.clear_widgets()

        anchor = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            padding=[dp(18), dp(18), dp(18), dp(18)],
        )

        card = RoundedBox(
            orientation="vertical",
            size_hint=(None, None),
            width=dp(340),
            height=dp(height),
            padding=[dp(18), dp(18), dp(18), dp(18)],
            spacing=dp(12),
            radius=dp(26),
            bg_color=WHITE,
            border_color=BORDER,
        )

        anchor.add_widget(card)
        self.add_widget(anchor)
        return card

    def _title_row(self, title):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(42), spacing=dp(10))
        row.add_widget(AppLabel(title, font_size=24, bold=True, fixed_height=42))

        close_btn = AppButton(
            text="×",
            fixed_width=42,
            fixed_height=42,
            bg_color=WHITE,
            text_color=BLACK,
            border_color=BLACK,
            radius=dp(14),
            font_size_value=20,
        )
        close_btn.bind(on_release=lambda instance: self.dismiss())
        row.add_widget(close_btn)
        return row

    def _set_error(self, text):
        if self.error_label:
            self.error_label.text = text

    def _build_login_form(self):
        card = self._modal_card(292)
        card.add_widget(self._title_row("Вход"))
        card.add_widget(
            AppLabel(
                "Введите номер телефона. На него придет четырехзначный код подтверждения.",
                font_size=13,
                color=TEXT_MUTED,
                fixed_height=44,
            )
        )

        self.phone_box = InputBox("Номер телефона")
        card.add_widget(self.phone_box)

        self.error_label = AppLabel("", font_size=12, color=PINK, fixed_height=22)
        card.add_widget(self.error_label)

        buttons = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(46), spacing=dp(9))
        cancel = AppButton(
            text="Отмена",
            bg_color=WHITE,
            text_color=BLACK,
            border_color=BLACK,
            radius=dp(14),
        )
        cancel.bind(on_release=lambda instance: self.dismiss())

        next_btn = AppButton(
            text="Получить код",
            bg_color=BLACK,
            text_color=WHITE,
            border_color=BLACK,
            radius=dp(14),
        )
        next_btn.bind(on_release=lambda instance: self._request_login_code())

        buttons.add_widget(cancel)
        buttons.add_widget(next_btn)
        card.add_widget(buttons)

        card.add_widget(
            AppLabel(
                "Тестовый код для входа: 0000",
                font_size=11,
                color=TEXT_MUTED,
                halign="center",
                fixed_height=22,
            )
        )

    def _request_login_code(self):
        phone = self.phone_box.input.text.strip()
        if len(phone) < 4:
            self._set_error("Введите номер телефона")
            return

        self.auth_payload = {"phone": phone}
        self._build_code_form("login")

    def _build_register_form(self):
        card = self._modal_card(414)
        card.add_widget(self._title_row("Регистрация"))
        card.add_widget(
            AppLabel(
                "Заполните данные профиля. После этого подтвердите телефон тестовым кодом.",
                font_size=13,
                color=TEXT_MUTED,
                fixed_height=44,
            )
        )

        self.name_box = InputBox("Ваше имя")
        self.register_phone_box = InputBox("Номер телефона")
        self.email_box = InputBox("Почта")
        card.add_widget(self.name_box)
        card.add_widget(self.register_phone_box)
        card.add_widget(self.email_box)

        self.error_label = AppLabel("", font_size=12, color=PINK, fixed_height=22)
        card.add_widget(self.error_label)

        buttons = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(46), spacing=dp(9))
        cancel = AppButton(
            text="Отмена",
            bg_color=WHITE,
            text_color=BLACK,
            border_color=BLACK,
            radius=dp(14),
        )
        cancel.bind(on_release=lambda instance: self.dismiss())

        next_btn = AppButton(
            text="Далее",
            bg_color=BLACK,
            text_color=WHITE,
            border_color=BLACK,
            radius=dp(14),
        )
        next_btn.bind(on_release=lambda instance: self._request_register_code())

        buttons.add_widget(cancel)
        buttons.add_widget(next_btn)
        card.add_widget(buttons)

        card.add_widget(
            AppLabel(
                "Тестовый код подтверждения: 0000",
                font_size=11,
                color=TEXT_MUTED,
                halign="center",
                fixed_height=22,
            )
        )

    def _request_register_code(self):
        name = self.name_box.input.text.strip()
        phone = self.register_phone_box.input.text.strip()
        email = self.email_box.input.text.strip()

        if not name:
            self._set_error("Введите имя")
            return
        if len(phone) < 4:
            self._set_error("Введите номер телефона")
            return
        if "@" not in email or "." not in email:
            self._set_error("Введите корректную почту")
            return

        self.auth_payload = {
            "name": name,
            "phone": phone,
            "email": email,
        }
        self._build_code_form("register")

    def _build_code_form(self, auth_type):
        card = self._modal_card(288)
        card.add_widget(self._title_row("Введите код"))
        card.add_widget(
            AppLabel(
                "Мы отправили четырехзначный код на указанный номер. Для демо используйте код 0000.",
                font_size=13,
                color=TEXT_MUTED,
                fixed_height=48,
            )
        )

        self.code_box = InputBox("Код подтверждения")
        self.code_box.input.input_filter = "int"
        self.code_box.input.text = ""
        card.add_widget(self.code_box)

        self.error_label = AppLabel("", font_size=12, color=PINK, fixed_height=22)
        card.add_widget(self.error_label)

        buttons = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(46), spacing=dp(9))
        back = AppButton(
            text="Назад",
            bg_color=WHITE,
            text_color=BLACK,
            border_color=BLACK,
            radius=dp(14),
        )
        if auth_type == "login":
            back.bind(on_release=lambda instance: self._build_login_form())
            action_text = "Войти"
        else:
            back.bind(on_release=lambda instance: self._build_register_form())
            action_text = "Создать"

        confirm = AppButton(
            text=action_text,
            bg_color=BLACK,
            text_color=WHITE,
            border_color=BLACK,
            radius=dp(14),
        )
        confirm.bind(on_release=lambda instance: self._confirm_code(auth_type))

        buttons.add_widget(back)
        buttons.add_widget(confirm)
        card.add_widget(buttons)

    def _confirm_code(self, auth_type):
        code = self.code_box.input.text.strip()
        if code != self.TEST_CODE:
            self._set_error("Неверный код. Тестовый код: 0000")
            return

        self.dismiss()
        if auth_type == "login":
            self.app_ref.complete_login(self.auth_payload["phone"])
        else:
            self.app_ref.complete_registration(self.auth_payload)


class ProfileModal(ModalView):
    def __init__(self, app_ref, title, builder, **kwargs):
        super().__init__(
            size_hint=(1, 1),
            auto_dismiss=True,
            background_color=(0, 0, 0, 0.55),
            **kwargs,
        )
        self.app_ref = app_ref
        self.title = title
        self.builder = builder
        self._build()

    def _build(self):
        anchor = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            padding=[dp(16), dp(20), dp(16), dp(20)],
        )

        card = RoundedBox(
            orientation="vertical",
            size_hint=(None, None),
            width=dp(356),
            height=dp(610),
            padding=[dp(16), dp(16), dp(16), dp(16)],
            spacing=dp(12),
            radius=dp(26),
            bg_color=WHITE,
            border_color=BORDER,
        )

        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(10))
        top.add_widget(AppLabel(self.title, font_size=25, bold=True, fixed_height=44))
        close_btn = AppButton(
            text="×",
            fixed_width=44,
            fixed_height=44,
            bg_color=WHITE,
            text_color=BLACK,
            border_color=BLACK,
            radius=dp(15),
            font_size_value=20,
        )
        close_btn.bind(on_release=lambda instance: self.dismiss())
        top.add_widget(close_btn)
        card.add_widget(top)

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            padding=[0, 0, 0, dp(6)],
        )
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)
        card.add_widget(scroll)

        self.builder(content)
        anchor.add_widget(card)
        self.add_widget(anchor)


class AnimatedGif(Image):
    """Надежное воспроизведение GIF через ручную смену кадров.

    Стандартный Kivy Image иногда показывает GIF как белый квадрат на Windows.
    Этот виджет читает кадры через Pillow и сам обновляет texture.
    """

    def __init__(self, source, fallback_size=(132, 132), **kwargs):
        super().__init__(source="", **kwargs)
        self.gif_source = source
        self.frames = []
        self.frame_durations = []
        self.frame_index = 0
        self._event = None
        self._fallback_size = fallback_size
        self._load_gif_frames()

    def _load_gif_frames(self):
        if PILImage is None or ImageSequence is None:
            print("Pillow не установлен. Установи: pip install pillow")
            return

        if not os.path.exists(self.gif_source):
            print(f"GIF не найден: {self.gif_source}")
            return

        try:
            with PILImage.open(self.gif_source) as gif:
                for frame in ImageSequence.Iterator(gif):
                    duration = frame.info.get("duration", 60) / 1000
                    if duration <= 0:
                        duration = 0.06

                    rgba_frame = frame.convert("RGBA")
                    width, height = rgba_frame.size

                    texture = Texture.create(size=(width, height), colorfmt="rgba")
                    texture.blit_buffer(
                        rgba_frame.tobytes(),
                        colorfmt="rgba",
                        bufferfmt="ubyte",
                    )
                    texture.flip_vertical()

                    self.frames.append(texture)
                    self.frame_durations.append(duration)

            if self.frames:
                self.texture = self.frames[0]
                self.frame_index = 0
                print(f"GIF загружен: {self.gif_source}, кадров: {len(self.frames)}")
            else:
                print(f"В GIF нет кадров: {self.gif_source}")

        except Exception as error:
            print(f"Не удалось загрузить GIF {self.gif_source}: {error}")

    def play(self):
        self.stop()
        if len(self.frames) <= 1:
            if self.frames:
                self.texture = self.frames[0]
            return
        self.frame_index = 0
        self.texture = self.frames[0]
        self._schedule_next_frame()

    def stop(self):
        if self._event is not None:
            self._event.cancel()
            self._event = None

    def _schedule_next_frame(self):
        if not self.frames:
            return
        delay = self.frame_durations[self.frame_index]
        self._event = Clock.schedule_once(self._next_frame, delay)

    def _next_frame(self, *args):
        if not self.frames:
            return
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.texture = self.frames[self.frame_index]
        self._schedule_next_frame()


class SplashScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="splash", **kwargs)
        self.app_ref = app_ref
        self.splash_icon = None
        self.loading_icon = None

        root = Surface(orientation="vertical", bg_color=BLACK)
        center = AnchorLayout(anchor_x="center", anchor_y="center")

        box = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=dp(280),
            height=dp(280),
            spacing=dp(14),
        )

        icon_anchor = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint_y=None,
            height=dp(148),
        )

        # GIF в Kivy обычно стабильнее, чем MP4, особенно при запуске на Windows.
        # Положи файл phone.gif рядом с main.py.
        phone_gif = asset_path("phone.gif")
        logo_png = asset_path("logo.png")

        if os.path.exists(phone_gif):
            self.splash_icon = AnimatedGif(
                source=phone_gif,
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(None, None),
                size=(dp(132), dp(132)),
            )
            icon_anchor.add_widget(self.splash_icon)
        elif os.path.exists(logo_png):
            self.splash_icon = Image(
                source=logo_png,
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(None, None),
                size=(dp(132), dp(132)),
            )
            icon_anchor.add_widget(self.splash_icon)
        else:
            # Резервный вариант, если phone.gif и logo.png не найдены рядом с main.py.
            icon_anchor.add_widget(LogoMark(dark=False, size_value=96))

        box.add_widget(icon_anchor)

        title = Label(
            text="Клик Маркет",
            color=WHITE,
            font_size=dp(30),
            bold=True,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(46),
        )
        title.bind(size=lambda instance, size: setattr(instance, "text_size", size))
        box.add_widget(title)

        subtitle = Label(
            text="выгодные предложения — в один клик",
            color=(0.75, 0.75, 0.75, 1),
            font_size=dp(13),
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(30),
        )
        subtitle.bind(size=lambda instance, size: setattr(instance, "text_size", size))
        box.add_widget(subtitle)

        loader_anchor = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint_y=None,
            height=dp(42),
        )

        loading_gif = asset_path("loading.gif")
        if os.path.exists(loading_gif):
            self.loading_icon = AnimatedGif(
                source=loading_gif,
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(None, None),
                size=(dp(92), dp(34)),
            )
            loader_anchor.add_widget(self.loading_icon)
        else:
            # Резервный вариант, если loading.gif не найден рядом с main.py.
            loader_anchor.add_widget(
                Label(
                    text="Загрузка...",
                    color=(0.75, 0.75, 0.75, 1),
                    font_size=dp(12),
                    halign="center",
                    valign="middle",
                )
            )

        box.add_widget(loader_anchor)

        box.opacity = 0
        center.add_widget(box)
        root.add_widget(center)
        self.add_widget(root)
        self.box = box

    def on_enter(self, *args):
        # Перезапускаем GIF-иконки с первого кадра при каждом входе на splash.
        if hasattr(self.splash_icon, "play"):
            self.splash_icon.play()
        if hasattr(self.loading_icon, "play"):
            self.loading_icon.play()

        Animation(opacity=1, duration=0.55, t="out_quad").start(self.box)

    def on_leave(self, *args):
        if hasattr(self.splash_icon, "stop"):
            self.splash_icon.stop()
        if hasattr(self.loading_icon, "stop"):
            self.loading_icon.stop()


class PhoneShell(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="app", **kwargs)
        self.app_ref = app_ref
        self.current_tab = "home"
        self.home_scroll = None
        self.home_content = None
        self.home_steps_target = None
        self.home_catalog_target = None
        self.home_saved_scroll_y = 1
        self.catalog_scroll = None
        self.catalog_content = None
        self.nav_items = {}

        root = Surface(orientation="vertical", bg_color=PAGE_BG)
        self.content_holder = BoxLayout(orientation="vertical")
        root.add_widget(self.content_holder)
        root.add_widget(self._build_bottom_nav())
        self.add_widget(root)

    def _build_bottom_nav(self):
        nav = RoundedBox(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(78),
            padding=[dp(10), dp(8), dp(10), dp(8)],
            spacing=dp(7),
            radius=dp(0),
            bg_color=BLACK,
            border_width=0,
        )

        items = [
            ("home", "dom.png", "dom_on.png"),
            ("catalog", "katalog.png", "katalog_on.png"),
            ("cart", "korzina.png", "korzina_on.png"),
            ("profile", "profile.png", "profile_on.png"),
        ]

        for page_name, icon_file, active_icon_file in items:
            item = NavItem(self, page_name, icon_file, active_icon_file)
            self.nav_items[page_name] = item
            nav.add_widget(item)

        return nav

    def open_tab(self, tab_name, preserve_scroll=False):
        # Если на главной пользователь нажимает категорию, сердечко или корзину,
        # вкладка пересобирается. Перед пересборкой запоминаем текущую прокрутку,
        # чтобы экран не прыгал обратно наверх.
        saved_home_scroll_y = None
        saved_catalog_scroll_y = None
        if preserve_scroll and self.current_tab == "home" and self.home_scroll:
            saved_home_scroll_y = self.home_scroll.scroll_y
            self.home_saved_scroll_y = saved_home_scroll_y
        elif preserve_scroll and self.current_tab == "catalog" and self.catalog_scroll:
            saved_catalog_scroll_y = self.catalog_scroll.scroll_y

        self.current_tab = tab_name
        if self.app_ref:
            self.app_ref.save_state()
        self.content_holder.clear_widgets()

        for name, item in self.nav_items.items():
            item.active = name == tab_name

        if tab_name == "home":
            page = self._build_home_page()
        elif tab_name == "catalog":
            page = self._build_catalog_page()
        elif tab_name == "cart":
            page = self._build_cart_page()
        elif tab_name == "profile":
            page = self._build_profile_page()
        else:
            page = self._build_home_page()

        page.opacity = 0
        self.content_holder.add_widget(page)
        Animation(opacity=1, duration=0.18, t="out_quad").start(page)

        if tab_name == "home" and saved_home_scroll_y is not None:
            self._restore_home_scroll(saved_home_scroll_y)
        elif tab_name == "catalog" and saved_catalog_scroll_y is not None:
            self._restore_catalog_scroll(saved_catalog_scroll_y)

    def _restore_home_scroll(self, scroll_y):
        def do_restore(attempt=0):
            if not self.home_scroll or not self.home_content:
                if attempt < 8:
                    Clock.schedule_once(lambda dt: do_restore(attempt + 1), 0.05)
                return

            self.home_content.do_layout()
            self.home_scroll.update_from_scroll()
            self.home_scroll.scroll_y = max(0, min(1, scroll_y))

        Clock.schedule_once(lambda dt: do_restore(), 0.05)

    def _restore_catalog_scroll(self, scroll_y):
        def do_restore(attempt=0):
            if not self.catalog_scroll or not self.catalog_content:
                if attempt < 8:
                    Clock.schedule_once(lambda dt: do_restore(attempt + 1), 0.05)
                return

            self.catalog_content.do_layout()
            self.catalog_scroll.update_from_scroll()
            self.catalog_scroll.scroll_y = max(0, min(1, scroll_y))

        Clock.schedule_once(lambda dt: do_restore(), 0.05)

    def _scroll_page(self):
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        content = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(18), dp(18), dp(22)],
            spacing=dp(18),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)
        return scroll, content

    def _card(self, **kwargs):
        card = RoundedBox(
            orientation=kwargs.pop("orientation", "vertical"),
            padding=kwargs.pop("padding", [dp(18), dp(17), dp(18), dp(17)]),
            spacing=kwargs.pop("spacing", dp(12)),
            radius=kwargs.pop("radius", dp(24)),
            bg_color=kwargs.pop("bg_color", WHITE),
            border_color=kwargs.pop("border_color", BORDER),
            **kwargs,
        )
        bind_adaptive_height(card)
        return card

    def _section_title(self, small, title):
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        box.bind(minimum_height=box.setter("height"))
        box.add_widget(AppLabel(small, font_size=11, color=TEXT_MUTED, bold=True))
        box.add_widget(AppLabel(title, font_size=25, bold=True))
        return box

    def _build_home_page(self):
        scroll, content = self._scroll_page()
        self.home_scroll = scroll
        self.home_content = content
        self.home_steps_target = None
        self.home_catalog_target = None

        hero = self._card(bg_color=(0.985, 0.985, 0.985, 1), spacing=dp(13))
        hero.add_widget(AppLabel("КЛИК МАРКЕТ", font_size=11, color=TEXT_MUTED, bold=True))
        hero.add_widget(AppLabel("Находите выгодные товары быстрее", font_size=31, bold=True))
        hero.add_widget(
            AppLabel(
                "Приложение помогает сравнивать предложения с разных площадок, сохранять товары в избранное и собирать удобную корзину.",
                font_size=14,
                color=(0.28, 0.28, 0.28, 1),
            )
        )

        button_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(10))
        start_btn = AppButton(
            text="Начать поиск",
            fixed_width=145,
            bg_color=BLACK,
            text_color=WHITE,
            border_color=BLACK,
            radius=dp(14),
        )
        start_btn.bind(on_release=lambda instance: self.open_tab("catalog"))
        info_btn = AppButton(
            text="Как работает",
            bg_color=WHITE,
            text_color=BLACK,
            border_color=BLACK,
            radius=dp(14),
        )
        info_btn.bind(on_release=lambda instance: self.scroll_to_steps())
        button_row.add_widget(start_btn)
        button_row.add_widget(info_btn)
        hero.add_widget(button_row)

        stats = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(76))
        stats.add_widget(StatCard("4", "категории"))
        stats.add_widget(StatCard("24+", "товара"))
        stats.add_widget(StatCard("1", "интерфейс"))
        hero.add_widget(stats)
        content.add_widget(hero)

        content.add_widget(self._section_title("ПРЕИМУЩЕСТВА", "Что умеет Клик Маркет"))
        benefits = [
            ("Сравнение цен", "Предложения сортируются по цене, чтобы выгодный вариант был виден сразу."),
            ("Поиск и фильтры", "Можно выбрать категорию, ввести запрос и уточнить параметры товара."),
            ("Избранное", "Понравившиеся товары сохраняются отдельно, чтобы быстро вернуться к ним."),
            ("Корзина", "Корзина собирает выбранные предложения перед переходом к покупке."),
        ]
        for title, text in benefits:
            card = self._card(padding=[dp(16), dp(15), dp(16), dp(15)], spacing=dp(8))
            card.add_widget(AppLabel(title, font_size=18, bold=True))
            card.add_widget(AppLabel(text, font_size=13, color=(0.3, 0.3, 0.3, 1)))
            content.add_widget(card)

        steps_title = self._section_title("СЦЕНАРИЙ", "Как это работает")
        self.home_steps_target = steps_title
        content.add_widget(steps_title)
        steps = [
            ("01", "Выбор категории", "Пользователь открывает раздел \"Каталог\" и выбирает нужную категорию."),
            ("02", "Поиск товара", "Внутри категории можно найти товар и посмотреть подходящие предложения."),
            ("03", "Сравнение", "Карточки показывают цену, источник, краткое описание и доступные действия."),
            ("04", "Выбор", "Товар можно добавить в избранное или положить в корзину."),
        ]
        for number, title, text in steps:
            row = self._card(orientation="horizontal", spacing=dp(12))
            number_box = RoundedBox(
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                radius=dp(20),
                bg_color=BLACK,
                border_width=0,
            )
            number_label = Label(
                text=number,
                color=WHITE,
                bold=True,
                font_size=dp(12),
                halign="center",
                valign="middle",
            )
            number_label.bind(size=lambda instance, size: setattr(instance, "text_size", size))
            number_box.add_widget(number_label)

            text_box = BoxLayout(orientation="vertical", spacing=dp(4))
            bind_adaptive_height(text_box)
            text_box.add_widget(AppLabel(title, font_size=17, bold=True))
            text_box.add_widget(AppLabel(text, font_size=13, color=(0.3, 0.3, 0.3, 1)))
            row.add_widget(number_box)
            row.add_widget(text_box)
            content.add_widget(row)

        return scroll

    def _scroll_to_home_widget(self, target_attr):
        if self.current_tab != "home":
            self.open_tab("home")

        def clamp(value, min_value=0, max_value=1):
            return max(min_value, min(max_value, value))

        def do_scroll(attempt=0):
            scroll = getattr(self, "home_scroll", None)
            content = getattr(self, "home_content", None)
            target = getattr(self, target_attr, None)

            if not scroll or not content or not target:
                if attempt < 8:
                    Clock.schedule_once(lambda dt: do_scroll(attempt + 1), 0.08)
                return

            # Принудительно обновляем геометрию. Без этого ScrollView иногда
            # скроллит к старой позиции, особенно сразу после пересборки вкладки.
            content.do_layout()
            scroll.update_from_scroll()

            scrollable_height = max(content.height - scroll.height, 1)
            target_top = target.y + target.height

            # scroll_y: 1 — верх страницы, 0 — низ страницы.
            target_scroll_y = (target_top + dp(10) - scroll.height) / scrollable_height
            target_scroll_y = clamp(target_scroll_y)

            Animation.cancel_all(scroll, "scroll_y")
            Animation(scroll_y=target_scroll_y, duration=0.38, t="out_quad").start(scroll)

        Clock.schedule_once(lambda dt: do_scroll(), 0.18)

    def scroll_to_steps(self):
        self._scroll_to_home_widget("home_steps_target")

    def scroll_to_catalog(self):
        self.open_tab("catalog")

    def _build_catalog_page(self):
        scroll, content = self._scroll_page()
        self.catalog_scroll = scroll
        self.catalog_content = content

        hero = self._card(bg_color=(0.985, 0.985, 0.985, 1), spacing=dp(12))
        hero.add_widget(AppLabel("КАТАЛОГ", font_size=11, color=TEXT_MUTED, bold=True))
        hero.add_widget(AppLabel("Каталог товаров", font_size=31, bold=True))
        hero.add_widget(
            AppLabel(
                "Выбери категорию, найди товар и добавь выгодное предложение в корзину.",
                font_size=14,
                color=(0.3, 0.3, 0.3, 1),
            )
        )
        content.add_widget(hero)

        content.add_widget(AppLabel("Категории", font_size=26, bold=True))
        category_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        category_grid.bind(minimum_height=category_grid.setter("height"))
        for title, subtitle in CATEGORIES:
            category_grid.add_widget(
                CategoryCard(
                    self.app_ref,
                    title,
                    subtitle,
                    active=self.app_ref.selected_category == title,
                )
            )
        content.add_widget(category_grid)

        content.add_widget(self._section_title("ТОВАРЫ", self.app_ref.selected_category))
        content.add_widget(InputBox("Поиск в каталоге..."))

        products = [
            product for product in PRODUCTS
            if product["category"] == self.app_ref.selected_category
        ]

        for product in products:
            content.add_widget(ProductCard(self.app_ref, product))

        return scroll

    def _build_favorites_page(self):
        scroll, content = self._scroll_page()

        hero = self._card(bg_color=(0.99, 0.975, 0.982, 1))
        hero.add_widget(AppLabel("ИЗБРАННОЕ", font_size=11, color=TEXT_MUTED, bold=True))
        hero.add_widget(AppLabel("Товары, которые ты отметил", font_size=30, bold=True))
        hero.add_widget(
            AppLabel(
                "Здесь хранятся понравившиеся товары. Можно быстро вернуться к ним и добавить нужное предложение в корзину.",
                font_size=14,
                color=(0.3, 0.3, 0.3, 1),
            )
        )
        content.add_widget(hero)

        favorites = [product for product in PRODUCTS if product["id"] in self.app_ref.favorite_ids]
        if not favorites:
            empty = self._card(spacing=dp(10))
            empty.add_widget(AppLabel("♡", font_size=52, color=PINK, bold=True, halign="center"))
            empty.add_widget(AppLabel("Пока здесь пусто", font_size=24, bold=True, halign="center"))
            empty.add_widget(
                AppLabel(
                    "Открой главную страницу и нажми на сердечко в карточке товара.",
                    font_size=14,
                    color=TEXT_MUTED,
                    halign="center",
                )
            )
            go_btn = AppButton(
                text="Перейти к товарам",
                fixed_height=46,
                bg_color=BLACK,
                text_color=WHITE,
                border_color=BLACK,
                radius=dp(14),
            )
            go_btn.bind(on_release=lambda instance: self.open_tab("catalog"))
            empty.add_widget(go_btn)
            content.add_widget(empty)
        else:
            for product in favorites:
                content.add_widget(ProductCard(self.app_ref, product))

        return scroll

    def _build_cart_page(self):
        scroll, content = self._scroll_page()

        hero = self._card(bg_color=(0.985, 0.985, 0.985, 1))
        hero.add_widget(AppLabel("КОРЗИНА", font_size=11, color=TEXT_MUTED, bold=True))
        hero.add_widget(AppLabel("Товары для покупки", font_size=30, bold=True))
        hero.add_widget(
            AppLabel(
                "Здесь собраны предложения, которые ты выбрал. После демо-оформления заказ появится в профиле.",
                font_size=14,
                color=(0.3, 0.3, 0.3, 1),
            )
        )
        content.add_widget(hero)

        cart_products = [product for product in PRODUCTS if product["id"] in self.app_ref.cart_ids]
        total = sum(product["price"] for product in cart_products)

        if not cart_products:
            empty = self._card(spacing=dp(10))
            empty.add_widget(AppLabel("Корзина пока пустая", font_size=24, bold=True, halign="center"))
            empty.add_widget(
                AppLabel(
                    "Добавь товары из каталога, чтобы сравнить предложения и подготовить покупку.",
                    font_size=14,
                    color=TEXT_MUTED,
                    halign="center",
                )
            )
            go_btn = AppButton(
                text="Перейти к товарам",
                bg_color=BLACK,
                text_color=WHITE,
                border_color=BLACK,
                radius=dp(14),
            )
            go_btn.bind(on_release=lambda instance: self.open_tab("catalog"))
            empty.add_widget(go_btn)
            content.add_widget(empty)
        else:
            for product in cart_products:
                row = self._card(orientation="horizontal", padding=[dp(14), dp(12), dp(14), dp(12)], spacing=dp(8))
                info = BoxLayout(orientation="vertical", spacing=dp(2))
                bind_adaptive_height(info)
                info.add_widget(AppLabel(product["name"], font_size=16, bold=True))
                info.add_widget(AppLabel(f'{product["source"]} • {product["price"]} ₽', font_size=13, color=TEXT_MUTED))
                row.add_widget(info)
                remove_btn = AppButton(
                    text="×",
                    fixed_width=42,
                    fixed_height=42,
                    bg_color=WHITE,
                    text_color=BLACK,
                    border_color=BLACK,
                    radius=dp(14),
                    font_size_value=20,
                )
                remove_btn.bind(on_release=lambda instance, pid=product["id"]: self.app_ref.remove_from_cart(pid))
                row.add_widget(remove_btn)
                content.add_widget(row)

        summary = self._card(spacing=dp(8))
        summary.add_widget(AppLabel("ИТОГ ЗАКАЗА", font_size=11, color=TEXT_MUTED, bold=True))
        summary.add_widget(AppLabel(f"Товаров: {len(cart_products)}", font_size=15))
        summary.add_widget(AppLabel(f"Источников: {len(set(p['source'] for p in cart_products))}", font_size=15))
        summary.add_widget(AppLabel("Экономия: демо", font_size=15))
        summary.add_widget(AppLabel(f"Итого: {total} ₽", font_size=27, bold=True))
        pay_btn = AppButton(
            text="Оформить заказ",
            bg_color=BLACK,
            text_color=WHITE,
            border_color=BLACK,
            radius=dp(14),
        )
        pay_btn.bind(on_release=lambda instance: self.app_ref.checkout_order())
        summary.add_widget(pay_btn)
        content.add_widget(summary)

        return scroll

    def _build_profile_page(self):
        scroll, content = self._scroll_page()

        hero = self._card(bg_color=(0.985, 0.985, 0.985, 1), spacing=dp(13))
        hero.add_widget(AppLabel("ПРОФИЛЬ", font_size=11, color=TEXT_MUTED, bold=True))
        hero.add_widget(AppLabel("Личный кабинет", font_size=31, bold=True))

        if self.app_ref.is_logged_in:
            profile = self.app_ref.profile
            info = self._card(
                padding=[dp(14), dp(13), dp(14), dp(13)],
                spacing=dp(7),
                bg_color=WHITE,
                border_color=BORDER,
            )
            info.add_widget(AppLabel(f"Имя: {profile.get('name') or 'Пользователь'}", font_size=15, bold=True))
            info.add_widget(AppLabel(f"Телефон: {profile.get('phone') or 'не указан'}", font_size=14, color=TEXT_MUTED))
            info.add_widget(AppLabel(f"Почта: {profile.get('email') or 'не указана'}", font_size=14, color=TEXT_MUTED))
            hero.add_widget(info)

            logout = AppButton(
                text="Выйти из профиля",
                fixed_height=46,
                bg_color=BLACK,
                text_color=WHITE,
                border_color=BLACK,
                radius=dp(15),
            )
            logout.bind(on_release=lambda instance: self.app_ref.logout())
            hero.add_widget(logout)
        else:
            login = AppButton(
                text="Войти",
                fixed_height=48,
                bg_color=BLACK,
                text_color=WHITE,
                border_color=BLACK,
                radius=dp(15),
            )
            login.bind(on_release=lambda instance: self.app_ref.open_login_modal())
            hero.add_widget(login)

            register = AppButton(
                text="Зарегистрироваться",
                fixed_height=48,
                bg_color=WHITE,
                text_color=BLACK,
                border_color=BLACK,
                radius=dp(15),
            )
            register.bind(on_release=lambda instance: self.app_ref.open_register_modal())
            hero.add_widget(register)

        content.add_widget(hero)

        actions = self._card(spacing=dp(10))
        actions.add_widget(AppLabel("РАЗДЕЛЫ ПРОФИЛЯ", font_size=11, color=TEXT_MUTED, bold=True))

        orders_btn = AppButton(
            text="Мои заказы",
            fixed_height=48,
            bg_color=BLACK if self.app_ref.is_logged_in else (0.82, 0.82, 0.82, 1),
            text_color=WHITE,
            border_color=BLACK if self.app_ref.is_logged_in else (0.82, 0.82, 0.82, 1),
            radius=dp(15),
        )
        orders_btn.bind(on_release=lambda instance: self.open_profile_orders())
        actions.add_widget(orders_btn)

        fav_btn = AppButton(
            text="Избранное",
            fixed_height=48,
            bg_color=WHITE,
            text_color=BLACK if self.app_ref.is_logged_in else TEXT_MUTED,
            border_color=BLACK if self.app_ref.is_logged_in else BORDER,
            radius=dp(15),
        )
        fav_btn.bind(on_release=lambda instance: self.open_profile_favorites())
        actions.add_widget(fav_btn)

        stats_btn = AppButton(
            text="Статистика",
            fixed_height=48,
            bg_color=WHITE,
            text_color=BLACK if self.app_ref.is_logged_in else TEXT_MUTED,
            border_color=BLACK if self.app_ref.is_logged_in else BORDER,
            radius=dp(15),
        )
        stats_btn.bind(on_release=lambda instance: self.open_profile_stats())
        actions.add_widget(stats_btn)

        params_btn = AppButton(
            text="Параметры",
            fixed_height=48,
            bg_color=WHITE,
            text_color=BLACK if self.app_ref.is_logged_in else TEXT_MUTED,
            border_color=BLACK if self.app_ref.is_logged_in else BORDER,
            radius=dp(15),
        )
        params_btn.bind(on_release=lambda instance: self.open_profile_parameters())
        actions.add_widget(params_btn)

        content.add_widget(actions)

        return scroll

    def _require_login(self):
        if self.app_ref.is_logged_in:
            return True
        self.app_ref.toast("Сначала войдите в профиль")
        return False

    def open_profile_orders(self):
        if not self._require_login():
            return

        def build(content):
            orders = self.app_ref.orders
            if not orders:
                empty = self._card(spacing=dp(9))
                empty.add_widget(AppLabel("Заказов пока нет", font_size=22, bold=True, halign="center"))
                empty.add_widget(
                    AppLabel(
                        "Оформи демо-заказ из корзины — он появится здесь.",
                        font_size=14,
                        color=TEXT_MUTED,
                        halign="center",
                    )
                )
                go_btn = AppButton(
                    text="Открыть каталог",
                    fixed_height=46,
                    bg_color=BLACK,
                    text_color=WHITE,
                    border_color=BLACK,
                    radius=dp(14),
                )
                go_btn.bind(on_release=lambda instance: self.open_tab("catalog"))
                empty.add_widget(go_btn)
                content.add_widget(empty)
                return

            for order in reversed(orders):
                card = self._card(spacing=dp(8))
                card.add_widget(AppLabel(f"Заказ №{order.get('id')}", font_size=20, bold=True))
                card.add_widget(AppLabel(order.get("date", ""), font_size=13, color=TEXT_MUTED))
                for item in order.get("items", []):
                    card.add_widget(
                        AppLabel(
                            f"• {item.get('name')} — {item.get('price')} ₽",
                            font_size=14,
                            color=(0.22, 0.22, 0.22, 1),
                        )
                    )
                card.add_widget(AppLabel(f"Итого: {order.get('total', 0)} ₽", font_size=18, bold=True))
                content.add_widget(card)

        ProfileModal(self.app_ref, "Мои заказы", build).open()

    def open_profile_favorites(self):
        if not self._require_login():
            return

        def build(content):
            favorites = [product for product in PRODUCTS if product["id"] in self.app_ref.favorite_ids]
            if not favorites:
                empty = self._card(spacing=dp(9))
                empty.add_widget(AppLabel("Избранное пустое", font_size=22, bold=True, halign="center"))
                empty.add_widget(
                    AppLabel(
                        "Нажми сердечко у товара в каталоге, чтобы сохранить его здесь.",
                        font_size=14,
                        color=TEXT_MUTED,
                        halign="center",
                    )
                )
                content.add_widget(empty)
                return

            for product in favorites:
                card = self._card(spacing=dp(8))
                card.add_widget(AppLabel(product["name"], font_size=19, bold=True))
                card.add_widget(AppLabel(product["description"], font_size=13, color=TEXT_MUTED))
                card.add_widget(AppLabel(f'{product["source"]} • {product["price"]} ₽', font_size=17, bold=True))
                add_btn = AppButton(
                    text="В корзину",
                    fixed_height=44,
                    bg_color=BLACK,
                    text_color=WHITE,
                    border_color=BLACK,
                    radius=dp(14),
                )
                add_btn.bind(on_release=lambda instance, pid=product["id"]: self.app_ref.add_to_cart(pid))
                card.add_widget(add_btn)
                content.add_widget(card)

        ProfileModal(self.app_ref, "Избранное", build).open()

    def open_profile_stats(self):
        if not self._require_login():
            return

        def build(content):
            profile = self.app_ref.profile
            orders_total = sum(order.get("total", 0) for order in self.app_ref.orders)

            user_card = self._card(spacing=dp(8))
            user_card.add_widget(AppLabel("Пользователь", font_size=20, bold=True))
            user_card.add_widget(AppLabel(f"Имя: {profile.get('name') or 'Пользователь'}", font_size=14, color=TEXT_DARK))
            user_card.add_widget(AppLabel(f"Телефон: {profile.get('phone') or 'не указан'}", font_size=14, color=TEXT_MUTED))
            user_card.add_widget(AppLabel(f"Почта: {profile.get('email') or 'не указана'}", font_size=14, color=TEXT_MUTED))
            content.add_widget(user_card)

            stats_grid = GridLayout(cols=2, spacing=dp(9), size_hint_y=None, height=dp(166))
            stats_grid.add_widget(StatCard(str(len(self.app_ref.favorite_ids)), "в избранном"))
            stats_grid.add_widget(StatCard(str(len(self.app_ref.cart_ids)), "в корзине"))
            stats_grid.add_widget(StatCard(str(len(self.app_ref.orders)), "заказов"))
            stats_grid.add_widget(StatCard(f"{orders_total} ₽", "сумма заказов"))
            content.add_widget(stats_grid)

        ProfileModal(self.app_ref, "Статистика", build).open()

    def open_profile_parameters(self):
        if not self._require_login():
            return

        def build(content):
            content.add_widget(
                AppLabel(
                    "Управляй поведением приложения. Каждый параметр переключается отдельной кнопкой.",
                    font_size=13,
                    color=TEXT_MUTED,
                    fixed_height=44,
                )
            )

            rows = [
                (
                    "price_alerts",
                    "Уведомления о снижении цены",
                    "Показывать уведомления, когда у выбранного товара появляется более выгодная цена.",
                ),
                (
                    "best_first",
                    "Выгодные предложения первыми",
                    "Сортировать предложения так, чтобы самый дешевый вариант был выше остальных.",
                ),
                (
                    "save_history",
                    "Сохранять историю выбора",
                    "Запоминать просмотренные товары и действия для будущих рекомендаций.",
                ),
            ]

            for key, title, subtitle in rows:
                content.add_widget(ProfileSettingToggle(self.app_ref, key, title, subtitle))

        ProfileModal(self.app_ref, "Параметры", build).open()


class ClickMarketApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.favorite_ids = set()
        self.cart_ids = []
        self.selected_category = "Электроника"
        self.is_logged_in = False
        self.profile = {"name": "", "phone": "", "email": ""}
        self.orders = []
        self.profile_parameters = {
            "price_alerts": True,
            "best_first": True,
            "save_history": False,
        }
        self.last_tab = "home"
        self.storage_path = None
        self.shell = None
        self.toast_widget = None

    def build(self):
        self.title = "Клик Маркет"
        Window.clearcolor = PAGE_BG
        Window.size = (390, 760)
        Window.minimum_width = 360
        Window.minimum_height = 640
        Window.softinput_mode = "below_target"

        self.storage_path = os.path.join(self.user_data_dir, "click_market_storage.json")
        self.load_state()

        self.manager = ScreenManager(transition=FadeTransition(duration=0.22))
        self.splash = SplashScreen(self)
        self.shell = PhoneShell(self)
        self.manager.add_widget(self.splash)
        self.manager.add_widget(self.shell)

        Clock.schedule_once(self._open_app_after_splash, 5)
        Clock.schedule_once(lambda dt: self.shell.open_tab(self.last_tab), 0)
        return self.manager

    def _open_app_after_splash(self, *args):
        self.manager.current = "app"

    def _default_state(self):
        return {
            "favorite_ids": [],
            "cart_ids": [],
            "selected_category": "Электроника",
            "is_logged_in": False,
            "profile": {"name": "", "phone": "", "email": ""},
            "orders": [],
            "profile_parameters": {
                "price_alerts": True,
                "best_first": True,
                "save_history": False,
            },
            "last_tab": "home",
        }

    def load_state(self):
        state = self._default_state()

        if self.storage_path and os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as file:
                    loaded_state = json.load(file)
                if isinstance(loaded_state, dict):
                    state.update(loaded_state)
            except Exception as error:
                print(f"Не удалось прочитать сохраненные данные: {error}")

        self.favorite_ids = set(int(item) for item in state.get("favorite_ids", []))
        self.cart_ids = [int(item) for item in state.get("cart_ids", [])]
        self.selected_category = state.get("selected_category") or "Электроника"
        self.is_logged_in = bool(state.get("is_logged_in", False))
        self.profile = state.get("profile") or {"name": "", "phone": "", "email": ""}
        self.orders = state.get("orders") or []
        default_parameters = self._default_state()["profile_parameters"]
        loaded_parameters = state.get("profile_parameters") or {}
        self.profile_parameters = {
            key: bool(loaded_parameters.get(key, default_value))
            for key, default_value in default_parameters.items()
        }
        self.last_tab = state.get("last_tab") or "home"

        if self.last_tab not in {"home", "catalog", "cart", "profile"}:
            self.last_tab = "home"

        valid_categories = {category[0] for category in CATEGORIES}
        if self.selected_category not in valid_categories:
            self.selected_category = "Электроника"

    def save_state(self):
        if not self.storage_path:
            return

        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        current_tab = self.shell.current_tab if self.shell else self.last_tab
        state = {
            "favorite_ids": sorted(self.favorite_ids),
            "cart_ids": self.cart_ids,
            "selected_category": self.selected_category,
            "is_logged_in": self.is_logged_in,
            "profile": self.profile,
            "orders": self.orders,
            "profile_parameters": self.profile_parameters,
            "last_tab": current_tab,
        }

        try:
            with open(self.storage_path, "w", encoding="utf-8") as file:
                json.dump(state, file, ensure_ascii=False, indent=2)
        except Exception as error:
            print(f"Не удалось сохранить данные: {error}")

    def set_selected_category(self, category):
        self.selected_category = category
        self.save_state()
        current_tab = self.shell.current_tab if self.shell else "home"
        if current_tab not in {"home", "catalog"}:
            current_tab = "catalog"
        self.shell.open_tab(current_tab, preserve_scroll=True)

    def on_stop(self):
        self.save_state()

    def toggle_profile_parameter(self, setting_key):
        if setting_key not in self.profile_parameters:
            return
        self.profile_parameters[setting_key] = not self.profile_parameters[setting_key]
        self.save_state()
        status = "включен" if self.profile_parameters[setting_key] else "выключен"
        self.toast(f"Параметр {status}")

    def toggle_favorite(self, product_id):
        if product_id in self.favorite_ids:
            self.favorite_ids.remove(product_id)
            self.toast("Удалено из избранного")
        else:
            self.favorite_ids.add(product_id)
            self.toast("Добавлено в избранное")
        self.save_state()
        self.shell.open_tab(self.shell.current_tab, preserve_scroll=True)

    def add_to_cart(self, product_id):
        if product_id not in self.cart_ids:
            self.cart_ids.append(product_id)
            self.toast("Добавлено в корзину")
        else:
            self.toast("Товар уже в корзине")
        self.save_state()
        self.shell.open_tab(self.shell.current_tab, preserve_scroll=True)

    def remove_from_cart(self, product_id):
        if product_id in self.cart_ids:
            self.cart_ids.remove(product_id)
            self.toast("Удалено из корзины")
        self.save_state()
        self.shell.open_tab("cart")


    def checkout_order(self):
        if not self.is_logged_in:
            self.toast("Для оформления заказа войдите в профиль")
            if self.shell:
                self.shell.open_tab("profile")
            return

        cart_products = [product for product in PRODUCTS if product["id"] in self.cart_ids]
        if not cart_products:
            self.toast("Корзина пустая")
            return

        order_id = len(self.orders) + 1
        order = {
            "id": order_id,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "items": [
                {
                    "id": product["id"],
                    "name": product["name"],
                    "price": product["price"],
                    "source": product["source"],
                }
                for product in cart_products
            ],
            "total": sum(product["price"] for product in cart_products),
        }
        self.orders.append(order)
        self.cart_ids = []
        self.save_state()
        self.toast("Заказ оформлен")
        self.shell.open_tab("profile")

    def open_login_modal(self):
        AuthModal(self, mode="login").open()

    def open_register_modal(self):
        AuthModal(self, mode="register").open()

    def complete_login(self, phone):
        self.is_logged_in = True
        self.profile["phone"] = phone
        if not self.profile.get("name"):
            self.profile["name"] = "Пользователь"
        self.save_state()
        self.toast("Вход выполнен")
        self.shell.open_tab("profile")

    def complete_registration(self, payload):
        self.is_logged_in = True
        self.profile = {
            "name": payload.get("name", ""),
            "phone": payload.get("phone", ""),
            "email": payload.get("email", ""),
        }
        self.save_state()
        self.toast("Регистрация завершена")
        self.shell.open_tab("profile")

    def logout(self):
        self.is_logged_in = False
        self.save_state()
        self.toast("Вы вышли из профиля")
        self.shell.open_tab("profile")

    def toast(self, text):
        if self.manager.current != "app":
            return

        if self.toast_widget and self.toast_widget.parent:
            self.toast_widget.parent.remove_widget(self.toast_widget)

        overlay = AnchorLayout(anchor_x="center", anchor_y="bottom")
        overlay.padding = [0, 0, 0, dp(92)]
        overlay.size_hint = (1, 1)

        toast = Toast(text)
        overlay.add_widget(toast)
        self.shell.add_widget(overlay)
        self.toast_widget = overlay

        anim_in = Animation(opacity=1, duration=0.16)
        anim_out = Animation(opacity=0, duration=0.22)

        def remove_overlay(*args):
            if overlay.parent:
                overlay.parent.remove_widget(overlay)

        anim_out.bind(on_complete=remove_overlay)
        anim_in.start(toast)
        Clock.schedule_once(lambda dt: anim_out.start(toast), 1.25)


if __name__ == "__main__":
    ClickMarketApp().run()
