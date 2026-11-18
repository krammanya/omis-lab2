"""Small deterministic review dataset for a visible end-to-end demonstration."""
from datetime import date, timedelta
from .models import Review, Client, Manager

SAMPLES = [
    (2, 3, "Доставка задержалась. Курьер груб, поддержка не помогла."),
    (4, 8, "Хороший смартфон, удобный экран, доставка вовремя."),
    (3, 6, "Кофемашина работает, но цена высокая."),
    (1, 1, "Товар сломан, качество ужасное. Нужна замена."),
    (5, 10, "Отличные наушники! Быстрая доставка, спасибо менеджеру."),
    (4, 9, "Хорошая кофемашина. Консультант помог, сервис отличный."),
    (5, 10, "Отличный смартфон, доволен покупкой!"),
    (3, 7, "Наушники работают. Доставка обычная."),
    (5, 9, "Хорошее качество, удобный товар. Спасибо!"),
]


def seed(s, products):
    for product in products:
        s.storage.save(product)
    for index, sample in enumerate(SAMPLES):
        add_sample(s, products[index % len(products)], index, sample)
    add_sample(s, products[0], 9, (5, 10, SAMPLES[6][2]))


def add_sample(s, product, index, sample):
    rating, recommendation, text = sample
    owner = s.auth.accounts["client@example.com"][2].id if index % 3 == 0 else f"demo-client-{index}"
    review = Review(text=text, rating=rating, recommendation=recommendation, client_id=owner, product_id=product.id, company_id=product.company_id)
    review.created_at = date.today() - timedelta(days=18 - index * 2)
    s.submit.submit(review)
