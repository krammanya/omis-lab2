"""Transparent local rules for text analysis and numerical calculations."""
import math
import re
from collections import Counter

POSITIVE = ("отлич", "хорош", "быстр", "спасибо", "удоб", "качествен", "доволен", "нравит")
NEGATIVE = ("плох", "ужас", "долго", "слом", "задерж", "груб", "брак", "разочар", "неудоб")
CATEGORIES = {"Доставка": ("достав", "курьер", "задерж", "посыл"),
              "Качество": ("качеств", "брак", "слом", "работает", "товар"),
              "Обслуживание": ("поддерж", "менеджер", "сервис", "консульт", "груб"),
              "Цена": ("цен", "дорог", "скид", "стоим")}
ENTITIES = ("смартфон", "наушники", "кофемашина", "курьер", "менеджер", "поддержка", "доставка")


def tokens(text):
    return re.findall(r"[а-яёa-z0-9]+", text.casefold())


def polarity(word):
    return int(any(word.startswith(x) for x in POSITIVE)) - int(any(word.startswith(x) for x in NEGATIVE))


def sentiment_score(words):
    return sum(polarity(word) * (-1 if index and words[index - 1] == "не" else 1)
               for index, word in enumerate(words))


def pearson(pairs):
    if len(pairs) < 2:
        return None
    xs, ys = zip(*pairs)
    return centered_correlation(xs, ys)


def centered_correlation(xs, ys):
    dx = [x - sum(xs) / len(xs) for x in xs]
    dy = [y - sum(ys) / len(ys) for y in ys]
    divisor = math.sqrt(sum(x*x for x in dx) * sum(y*y for y in dy))
    return round(sum(x*y for x, y in zip(dx, dy)) / divisor, 3) if divisor else None


def nps(reviews):
    scores = [r.recommendation for r in reviews if r.recommendation is not None]
    return round(100 * (sum(x >= 9 for x in scores) - sum(x <= 6 for x in scores)) / len(scores), 1) if scores else None


def summary(reviews):
    return {"Отзывы": len(reviews), "Средняя оценка": round(sum(r.rating for r in reviews) / len(reviews), 2) if reviews else None,
            "NPS": nps(reviews), "Ответов": sum(bool(r.reply_id) for r in reviews),
            "Требуют проверки": sum(r.suspicious for r in reviews)}
