from app.bot.main_bot import MainBot


def test_menu_text_normalization_removes_variation_selectors():
    # U+FE0F (variation selector-16) часто появляется/исчезает у emoji в зависимости от клиента.
    # Обходим тяжелый __init__ (он создает сервисы/хендлеры), нам нужен только метод нормализации.
    bot = MainBot.__new__(MainBot)

    a = "⬅️ В главное меню"            # includes VS16 in many keyboards
    b = "⬅\uFE0F В главное меню"      # explicit VS16
    c = "⬅ В главное меню"             # without VS16

    assert bot._normalize_menu_text(a) == bot._normalize_menu_text(b)
    assert bot._normalize_menu_text(a) == bot._normalize_menu_text(c)


def test_menu_text_normalization_strips_whitespace():
    bot = MainBot.__new__(MainBot)
    assert bot._normalize_menu_text("  🔍 Найти оборудование  ") == bot._normalize_menu_text(
        "🔍 Найти оборудование"
    )

