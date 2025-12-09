
import os

content = r'''
msgid "Biznes paneli - Fikrly"
msgstr "Панель бизнеса - Fikrly"

msgid "Biznes paneli"
msgstr "Панель бизнеса"

msgid "Biznes egasi"
msgstr "Владелец бизнеса"

msgid "Toshkent filiali faoliyati"
msgstr "Деятельность филиала в Ташкенте"

msgid "Profilni ko'rish"
msgstr "Посмотреть профиль"

msgid "Ishonch reytingi"
msgstr "Рейтинг доверия"

msgid "O'tgan oyga nisbatan"
msgstr "По сравнению с прошлым месяцем"

msgid "Jami sharhlar"
msgstr "Всего отзывов"

msgid "Javob berish"
msgstr "Ответить"

msgid "O'rtacha 2 soat"
msgstr "В среднем 2 часа"

msgid "Javob berish tezligi"
msgstr "Скорость ответа"

msgid "Ko'rishlar"
msgstr "Просмотры"

msgid "So'nggi sharhlar"
msgstr "Последние отзывы"

msgid "Barchasini ko'rish"
msgstr "Посмотреть все"

msgid "2 kun oldin"
msgstr "2 дня назад"

msgid "1 hafta oldin"
msgstr "1 неделю назад"

msgid "Yangi"
msgstr "Новый"

msgid "Javob berilgan"
msgstr "Отвечено"

msgid "Javobni ko'rish"
msgstr "Посмотреть ответ"

msgid "Reyting dinamikasi"
msgstr "Динамика рейтинга"

msgid "Oxirgi 30 kun"
msgstr "Последние 30 дней"

msgid "Oxirgi 3 oy"
msgstr "Последние 3 месяца"

msgid "Oxirgi 6 oy"
msgstr "Последние 6 месяцев"

msgid "Oxirgi yil"
msgstr "Последний год"

msgid "Reyting o'sish tendentsiyasi"
msgstr "Тенденция роста рейтинга"

msgid "4.6 dan 4.8 gacha (+4.3%)"
msgstr "С 4.6 до 4.8 (+4.3%)"

msgid "Tezkor amallar"
msgstr "Быстрые действия"

msgid "Sharhlarga javob berish"
msgstr "Ответить на отзывы"

msgid "Ma'lumotlarni yangilash"
msgstr "Обновить данные"

msgid "Rasm qo'shish"
msgstr "Добавить фото"

msgid "Muammoli sharhlar"
msgstr "Проблемные отзывы"

msgid "Mijozlar fikri"
msgstr "Мнение клиентов"

msgid "Ko'p maqtalgan"
msgstr "Часто хвалят"

msgid "Mazali taomlar (89% sharhlar)"
msgstr "Вкусная еда (89% отзывов)"

msgid "Tez xizmat (76% sharhlar)"
msgstr "Быстрое обслуживание (76% отзывов)"

msgid "Mehribon xodimlar (82% sharhlar)"
msgstr "Вежливый персонал (82% отзывов)"

msgid "Yaxshilash kerak"
msgstr "Нужно улучшить"

msgid "Kutish vaqti (23% sharhlar)"
msgstr "Время ожидания (23% отзывов)"

msgid "Joy kengligini oshirish (15% sharhlar)"
msgstr "Расширение пространства (15% отзывов)"

msgid "Narxlar (12% sharhlar)"
msgstr "Цены (12% отзывов)"

msgid "Bildirishnomalar"
msgstr "Уведомления"

msgid "Yangi 5 yulduzli sharh"
msgstr "Новый 5-звездочный отзыв"

msgid "4 yulduzli sharh javob kutmoqda"
msgstr "4-звездочный отзыв ждет ответа"

msgid "Reytingi 4.8 ga yetdi!"
msgstr "Рейтинг достиг 4.8!"

msgid "Bugun"
msgstr "Сегодня"

msgid "O'zbekistonning eng ishonchli sharh platformasi. Haqiqiy fikrlar, ishonchli tanlov."
msgstr "Самая надежная платформа отзывов в Узбекистане. Реальные мнения, надежный выбор."

msgid "Tezkor havolalar"
msgstr "Быстрые ссылки"

msgid "Biznes uchun"
msgstr "Для бизнеса"

msgid "Biznesni ro'yxatga olish"
msgstr "Регистрация бизнеса"

msgid "Reklama berish"
msgstr "Реклама"

msgid "Yordam"
msgstr "Помощь"

msgid "Yordam markazi"
msgstr "Центр помощи"

msgid "© 2025 Fikrly. Barcha huquqlar himoyalangan."
msgstr "© 2025 Fikrly. Все права защищены."
'''

with open('locale/ru/LC_MESSAGES/django.po', 'a', encoding='utf-8') as f:
    f.write(content)
