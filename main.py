
import os
import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Конфигурация
START_DATE = datetime.date(2025, 4, 23)
PORT = int(os.environ.get("PORT", 5000))

# Хранилище состояний
user_states = {}

def get_current_day() -> int:
    today = datetime.date.today()
    return (today - START_DATE).days

def get_available_day() -> int:
    current_day = get_current_day()
    return current_day if current_day >= 0 else -1

def get_user_state(user_id: int):
    available_day = get_available_day()
    if user_id not in user_states:
        start_day = max(0, available_day) if available_day >= 0 else 0
        user_states[user_id] = {'day': start_day, 'step': 0}
    elif user_states[user_id]['day'] > available_day:
        user_states[user_id] = {'day': available_day, 'step': 0}
    return user_states[user_id]

def update_user_state(user_id: int, day: int, step: int):
    available_day = get_available_day()
    user_states[user_id] = {'day': min(day, available_day), 'step': step}

# Данные квеста (полностью скопируйте ваш QUEST_DATA сюда)
QUEST_DATA = {
    "day0": [  # Вступление (сегодня)
        {
            "text": "Вы мне дорогие подарки дарили, теперь настала моя очередь, правда это будет 1 большой подарок на весь год...",
            "buttons": [("Следующее сообщение ▶️", "next")]
        },
        {
            "text": "Так вот, сейчас собираетесь и едете на вокзал на поезд №050*С, а завтра утром узнаете, что будете делать. Вас везде ждут, в большинстве мест все оплачено, где необходимо доплатить, увидите значок 💸 — ищите конверт с адресом",
            "buttons": [("Поняли, ждём завтра!", "finish")]
        }
    ],
    "day1": [  # Первый день (завтра)
        {
            "text": "Добро пожаловать в Санкт-Петербург! В 10:00 Вас ждут по адресу: Невский просп., 28.",
            "hint": "2 этаж, ресторан René на имя Андрей, 💸",
            "map_link": "https://yandex.ru/maps/2/saint-petersburg/house/nevskiy_prospekt_28/Z0kYdQVlQUICQFtjfXVydHRjZA==/?indoorLevel=1&ll=30.325876%2C59.935800&z=16.59",
            "photo": "https://core-pht-proxy.maps.yandex.ru/v1/photos/download?photo_id=yOqBYrOb6qVQJpesufk&image_size=X5L",
            "buttons": [
                ("👉 Что здесь?", "hint"),
                ("Следующий адрес ▶️", "next")
            ]
        },
        {
            "text": "В 12:00 ожидают по адресу: Кирочная ул., 9",
            "hint": "Мастерская Oh là là Art на имя Андрей",
            "map_link": "https://yandex.ru/maps/2/saint-petersburg/house/kirochnaya_ulitsa_9/Z0kYdQJkSEUOQFtjfXV1cntqYg==/?ll=30.354110%2C59.943796&z=16.59",
            "photo": "https://avatars.mds.yandex.net/get-altay/10767436/2a000001924e9f64945c1d24dd9977ea6e70/XXXL",
            "buttons": [
                ("👉 Что здесь?", "hint"),
                ("Следующий адрес ▶️", "next")
            ]
        },
        {
            "text": "На обед в 15:30 нужно быть по адресу: ул. Чайковского, 36",
            "hint": "Полный бизнес-ланч в Kiln на имя Андрей, 💸",
            "map_link": "https://yandex.ru/maps/2/saint-petersburg/house/ulitsa_chaykovskogo_36/Z0kYdQJnTEwCQFtjfXV1d3pqbA==/?ll=30.357595%2C59.946698&z=16.59",
            "photo": "https://core-pht-proxy.maps.yandex.ru/v1/photos/download?photo_id=Okm1jieviqg1ssseZrJpVw&image_size=XXL",
            "buttons": [
                ("👉 Что здесь?", "hint"),
                ("Следующий адрес ▶️", "next")
            ]
        },
        {
            "text": "Теперь у вас свободное время, но с 18:30 до 19:00 необходимо оказаться на проспекте Обуховской обороны, 106",
            "hint": "Напротив трамвайной остановки ул. Шелгунова",
            "additional_hint": "Да-да, вам на речной вокзал, конкретнее открывайте конверт.",
            "map_link": "https://yandex.ru/maps/2/saint-petersburg/house/prospekt_obukhovskoy_oborony_195k/Z0kYcgFiTEMEQFtjfXR3eXVqZw==/?from=mapframe&ll=30.462745%2C59.868940&z=19.85",
            "photo": "https://avatars.mds.yandex.net/get-altay/10767436/2a000001924e9f64945c1d24dd9977ea6e70/XXXL",
            "buttons": [
                ("👉 Что здесь?", "hint"),
                ("🔎 Конкретнее", "more_hint"),
                ("Следующий адрес ▶️", "next")
            ]
        },
        {
            "text": "Сегодня у вас будет ужин, завтра: завтрак, обед и ужин, послезавтра — завтрак. Завтра ожидает насыщенная программа, состоит из 2-х частей:\n\n1) Пешеходная экскурсия «Скиты Валаама» на 3,5 часа\nУвидите: Воскресенский, Гефсиманский и Коневский скиты; Валаамская Палестина; Большая Никоновская бухта.\n\nОписание: Маршрут экскурсии проходит по трем Валаамским скитам: Воскресенскому, Гефсиманскому и Коневскому. Именно здесь вы сможете ощутить гармонию дикой, суровой северной природы и строгой подвижнической иноческой жизни.\n\nИЛИ\n\n1) Пешеходная экскурсия «Скалистый берег» на 2,5 часа\nУвидите: Живописный залив Скалистый берег; Никоновский форт; Ладожское озеро.\n\nИ\n\n2) Пешеходная экскурсия в Центральную усадьбу Спасо-Преображенского Валаамского мужского монастыря на 3-4 часа\n\n! Идти 7 км. до усадьбы, есть трансфер если что! 💸",
            "photo": "https://cruiseinform.ru/upload/iblock/35f/27gtr7y42rfu1f3w5l8ap7j44oilvzkm.jpg",
            "buttons": [("Следующий день ▶️", "next_day")]
        }
    ],
    "day2": [  # Второй день (послезавтра)
        {
            "photo": "https://ic.pics.livejournal.com/ivanujriev/35612782/221741/221741_original.jpg",
            "buttons": [("Следующий день ▶️", "next_day")]
        }
    ],
    "day3": [  # Третий день
        {
            "text": "С возвращением! До 11:00 есть время попить кофе, а в 11:00 вас ждут на Загородный пр., 2",
            "hint": "Станция метро «Владимирская», у ограждения возле кафе Теремок",
            "map_link": "https://yandex.ru/maps/2/saint-petersburg/house/zagorodny_prospekt_2/Z0kYdQNmT0wPQFtjfXVzdnpiYw==/?from=mapframe&ll=30.347201%2C59.927558&z=19.39",
            "photo": "https://avatars.mds.yandex.net/get-altay/6159907/2a00000190fb2847dd66ebd929db4eaef32e/XXXL",
            "buttons": [
                ("👉 Что здесь?", "hint"),
                ("Следующий адрес ▶️", "next")
            ]
        },
        {
            "text": "В 14:30 обед на пл. Восстания, 4",
            "hint": "Братья Кебабцы на имя Андрей, 💸",
            "map_link": "https://yandex.ru/maps/2/saint-petersburg/house/ulitsa_vosstaniya_4/Z0kYdQJpTkYEQFtjfXVyc3RrZw==/?from=mapframe&ll=30.360124%2C59.931256&z=15.93",
            "photo": "https://avatars.mds.yandex.net/get-altay/13477341/2a000001913732681edf4fb88504bd5697c7/XXXL",
            "buttons": [
                
                ("👉 Что здесь?", "hint"),
                ("Следующий адрес ▶️", "next")
            ]
        },
        {
            "text": "Далее рекомендую закинуть вещи в гостиницу по адресу: Спасский пер., 9/24",
            "hint": "Гостиница Блюз, бронь на фамилию Штейн, 💸",
            "map_link": "https://yandex.ru/maps/2/saint-petersburg/house/spasskiy_pereulok_9_24/Z0kYdQZoSkcOQFtjfXVzeXhhZA==/?from=mapframe&indoorLevel=1&ll=30.318329%2C59.928420&z=16.59",
            "photo": "https://core-pht-proxy.maps.yandex.ru/v1/photos/download?photo_id=B1Z3eCP7P4Zhdvsa5l2IjQ&image_size=XL",
            "buttons": [
                
                ("👉 Что здесь?", "hint"),
                ("Следующий адрес ▶️", "next_day")
            ]
        },
        {
            "text": "При всем параде ровно в 17:50 быть на Зверинская улица, 5Б",
            "hint": "Вход через ворота, со двора, Точка массажа на имя Андрей",
            "photo": 'https://avatars.mds.yandex.net/get-altay/11421909/2a00000192a4f87d041bf1d69a53622e755f/XXXL?clckid=ea5aa617',
            "map_link": "https://yandex.ru/maps/2/saint-petersburg/house/zverinskaya_ulitsa_5b/Z0kYdA5kS0cPQFtjfXV0c3VkZA==/?ll=30.294306%2C59.952984&z=18",
            "buttons": [
                
                ("👉 Что здесь?", "hint"),
                ("Следующий адрес ▶️", "next")
            ]
        },
        {
            "text": "Отдохнули, но проголодались? Вас ждут к 18:40 (начало в 19:00) по адресу: Биржевой переулок, 2",
            "hint": "Вход через отель Palace Bridge, ресторан Dans Le Noir? на имя Андрей, 💸",
            "photo": 'https://avatars.mds.yandex.net/get-altay/10261179/2a000001912a02c76330041ff82bf68bac99/XXXL?clckid=c226f751',
            "map_link": "https://yandex.ru/maps/2/saint-petersburg/house/birzhevoy_pereulok_2/Z0kYdA5jTEMEQFtjfXV1dHxhZg==/?ll=30.293347%2C59.945027&z=18",
            "buttons": [
                
                ("👉 Что здесь?", "hint"),
                ("Следующий адрес ▶️", "next")
            ]
        },
        {
            "text": "А теперь или погулять, или спать, если забыли, то тут: Спасский переулок, 9/24",
            "hint": "Гостиница Блюз",
            "additional_hint": "Утром собираем вещи, оставляем в отеле, по возможности переселяемся",
            "photo": 'https://core-pht-proxy.maps.yandex.ru/v1/photos/download?photo_id=B1Z3eCP7P4Zhdvsa5l2IjQ&image_size=XL&clckid=f89d3e7d',
            "map_link": "https://yandex.ru/maps/2/saint-petersburg/house/spasskiy_pereulok_9_24/Z0kYdQZoSkcOQFtjfXVzeXhhZA==/?from=mapframe&indoorLevel=1&ll=30.318329%2C59.928420&z=16",
            "buttons": [
                
                ("👉 Что здесь?", "hint"),
                ("🔎 Конкретнее?", "more_hint"),
                ("Следующий день ▶️", "next_day")
            ]
        }
    ],
    "day4": [  # Четвертый день
        {
            "text": "В 10:30 быть по адресу: Цветочная ул., 16Л",
            "map_link": "https://yandex.ru/maps/2/saint-petersburg/house/tsvetochnaya_ulitsa_16l/Z0kYdQRhSUUCQFtjfXR5eXxmbA==/?from=mapframe&ll=30.347201%2C59.927558&z=19.39",
            "buttons": [
        
                ("👉 Что здесь?", "hint"),
                ("Продолжение следует...", "finish")
            ]
        }
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_quest_step', methods=['POST'])
def get_quest_step():
    user_id = request.json.get('user_id')
    day = request.json.get('day', None)
    step = request.json.get('step', None)
    
    if day is None or step is None:
        user_state = get_user_state(user_id)
        day = user_state['day']
        step = user_state['step']
    
    available_day = get_available_day()
    if day > available_day:
        if available_day < 0:
            return jsonify({
                'error': f"Квест начнётся {START_DATE}!"
            })
        else:
            next_date = START_DATE + datetime.timedelta(days=day)
            return jsonify({
                'error': f"Этот день будет доступен {next_date}"
            })
    
    day_key = f"day{day}"
    if day_key not in QUEST_DATA or step >= len(QUEST_DATA[day_key]):
        return jsonify({
            'error': "На сегодня задания закончились!"
        })
    
    content = QUEST_DATA[day_key][step].copy()
    update_user_state(user_id, day, step)
    
    return jsonify(content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)