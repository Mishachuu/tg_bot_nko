from datetime import date, timedelta, datetime
from calendar import monthrange
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Tuple


def _format_day(d: date, disabled: bool, unavailable: bool = False) -> str:
    if unavailable:
        return "❌"
    return f"{d.day:02d}" if not disabled else "—"


def month_keyboard(
    year: int,
    month: int,
    min_date: date,
    max_date: date,
    *,
    unavailable_dates: set[date] | None = None,
    include_cancel: bool = True,
    cancel_text: str = "⬅️ Назад",
) -> InlineKeyboardMarkup:
    """Return InlineKeyboardMarkup representing calendar for given month.

    Disabled days (before min_date or after max_date) are shown as '—' and non-clickable.
    Callback data for active days: 'cal:Y-M-D'
    Navigation callbacks: 'cal_prev:Y-M' and 'cal_next:Y-M'
    """
    first_weekday, days_in_month = monthrange(year, month)

    keyboard = []
    # Month title header (e.g. "December 2025")
    import calendar as _calendar
    month_name = _calendar.month_name[month]
    keyboard.append([InlineKeyboardButton(f"{month_name} {year}", callback_data="ignore")])

    # Weekday header
    headers = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    keyboard.append([InlineKeyboardButton(h, callback_data="ignore") for h in headers])

    # Fill days
    day = date(year, month, 1)
    # start from Monday index
    week = []
    # pad start
    for _ in range((day.weekday() + 0) % 7):
        week.append(InlineKeyboardButton(" ", callback_data="ignore"))

    for d in range(1, days_in_month + 1):
        current = date(year, month, d)
        disabled = current < min_date or current > max_date or current < date.today()
        unavailable = False
        if unavailable_dates and current in unavailable_dates:
            unavailable = True
            disabled = True

        if disabled:
            week.append(InlineKeyboardButton(_format_day(current, True, unavailable), callback_data="ignore"))
        else:
            # Use dd.mm.yyyy format in callback so bot logic expecting that format works
            cb = f"cal_select:{current.strftime('%d.%m.%Y')}"
            week.append(InlineKeyboardButton(_format_day(current, False, unavailable), callback_data=cb))

        if len(week) == 7:
            keyboard.append(week)
            week = []

    if week:
        # pad end
        while len(week) < 7:
            week.append(InlineKeyboardButton(" ", callback_data="ignore"))
        keyboard.append(week)

    # navigation
    prev_month = (date(year, month, 1) - timedelta(days=1)).replace(day=1)
    next_month = (date(year, month, days_in_month) + timedelta(days=1)).replace(day=1)

    nav = []
    nav.append(InlineKeyboardButton("« Prev", callback_data=f"cal_prev:{prev_month.year}-{prev_month.month}"))
    nav.append(InlineKeyboardButton("Now", callback_data="cal_today"))
    nav.append(InlineKeyboardButton("Next »", callback_data=f"cal_next:{next_month.year}-{next_month.month}"))
    keyboard.append(nav)

    if include_cancel:
        keyboard.append([InlineKeyboardButton(cancel_text, callback_data="cal_cancel")])

    return InlineKeyboardMarkup(keyboard)


def clamp_date(d: date) -> date:
    return d


def parse_calendar_callback(data: str) -> Tuple[str, str]:
    """Parse calendar callback data.

    Returns tuple (action, payload)
    Examples:
      'cal_select:2025-12-25' -> ('select', '2025-12-25')
      'cal_prev:2025-11' -> ('prev', '2025-11')
    """
    if data == "cal_today":
        return ("today", "")
    if data == "cal_cancel":
        return ("cancel", "")
    if data.startswith("cal_select:"):
        return ("select", data.split(":", 1)[1])
    if data.startswith("cal_prev:"):
        return ("prev", data.split(":", 1)[1])
    if data.startswith("cal_next:"):
        return ("next", data.split(":", 1)[1])
    return ("ignore", "")

