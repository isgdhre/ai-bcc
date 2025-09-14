import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
from typing import Dict, Tuple, List

# ----------------------
# Настройки / шаблоны
# ----------------------
PRODUCTS = [
    "Карта для путешествий",
    "Премиальная карта",
    "Кредитная карта",
    "Обмен валют",
    "Кредит наличными",
    "Депозит Мультивалютный",
    "Депозит Сберегательный", 
    "Депозит Накопительный",  
    "Инвестиции",
    "Золотые слитки"
]

MONTHS_RU = {
    1: {
        "январе"
        #kk: "қаңтарда",
        #en: "January"
    }, 
    2: {
        "феврале"
        #kk: "ақпанда",
        #en: "February"
    }, 
    3: {
        "марте"
        #kk: "наурызда",
        #en: "March"
    }, 
    4: {
        "апреле"
        #kk: "сәуірде",
        #en: "April"
    },
    5: {
        "мае"
        #kk: "мамырда",
        #en: "May"
    }, 
    6: {
        "июне"
        #kk: "маусымда",
        #en: "June"
    },
    7: {
        "июле"
        #kk: "шілдеде",
        #en: "July"
    }, 
    8: {
        "августе"
        #kk: "тамызда",
        #en: "August"
    }, 
    9: {
        "сентябре"
        #kk: "қыркүйекте",
        #en: "September"
    }, 
    10: {
        "октябре"
        #kk: "қазанда",
        #en: "October"
    }, 
    11: {
        "ноябре"
        #kk: "қарашада",
        #"en: "November"
    }, 
    12: {
        "декабре"
        #kk: "желтоқсанда",
        #en: "December"
    }
}

TEMPLATES = {
    "Карта для путешествий": {
        "{name}, в {month} вы провели поездки на сумму {spend} ₸. С картой для путешествий вы вернули бы ≈{benefit} ₸! Откройте карту в приложении.",
        #"kk": "{name}, {month} айында сіздің сапарларыңыз {spend} ₸ болды. Саяхат картасымен шамамен {benefit} ₸ қайтарылып отырады! Картаны қосымшада ашыңыз.",
        #"en": "{name}, in {month} you spent {spend} ₸ on trips. With the Travel Card you could have earned ≈{benefit} ₸ cashback! Open the card in the app."
    },
    "Премиальная карта": {
        "{name}, у вас стабильно крупный остаток {balance} ₸ и траты в ресторанах. Премиальная карта даст до 4% кешбэка и бесплатные снятия. Оформить сейчас.",
        #"kk": "{name}, сіздің тұрақты қалдығыңыз {balance} ₸ және мейрамханаларда шығындарыңыз бар. Премиум карта 4%-ға дейін кешбэк және тегін ақша алу мүмкіндігін береді. Қазір рәсімдеңіз.",
        #"en": "{name}, you maintain a stable balance of {balance} ₸ and spend in restaurants. The Premium Card gives up to 4% cashback and free withdrawals. Apply now."
    },
    "Кредитная карта": {
        "{name}, ваши топ-категории — {categories}. Кредитная карта даёт до 10% в любимых категориях. Оформить карту.",
        #"kk": "{name}, сіздің негізгі шығын категорияларыңыз — {categories}. Кредиттік карта сүйікті категорияларда 10%-ға дейін кешбэк береді. Картаны ашыңыз.",
        #"en": "{name}, your top categories are {categories}. The Credit Card gives up to 10% cashback in your favorite categories. Apply for the card."
    },
    "Обмен валют": {
        "{name}, вы часто обмениваете валюту ({fx_ops} операций). В приложении выгодный обмен и авто-покупка по целевому курсу. Настроить обмен.",
        #"kk": "{name}, сіз жиі валюта айырбастайсыз ({fx_ops} операция). Қосымшада тиімді айырбас және мақсатты бағам бойынша авто-сатып алу бар. Орнатыңыз.",
        #"en": "{name}, you often exchange currency ({fx_ops} operations). The app offers favorable rates and auto-purchase at your target rate. Set up now."
    },
    "Кредит наличными": {
        "{name}, если нужен запас на крупные траты — можно оформить кредит наличными с гибкими выплатами. Узнать доступный лимит.",
        #"kk": "{name}, егер ірі шығындарға қосымша қаражат қажет болса — икемді төлемдері бар қолма-қол несие алуға болады. Қолжетімді лимитті біліңіз.",
        #"en": "{name}, if you need extra funds for big expenses — you can get a cash loan with flexible repayments. Check your available limit."
    },
    "Депозит Мультивалютный": {
        "{name}, вы активно используете иностранную валюту. Мультивалютный вклад поможет сохранить и приумножить сбережения. Открыть вклад.",
        #"kk": "{name}, сіз шетел валютасын белсенді қолданасыз. Көпвалюталы депозит жинағыңызды сақтауға және көбейтуге көмектеседі. Депозит ашыңыз.",
        #"en": "{name}, you actively use foreign currency. A Multi-currency Deposit will help you save and grow your funds. Open a deposit."
    },
    "Депозит Сберегательный": {
        "{name}, у вас есть свободные средства {balance} ₸. Разместите их на вкладе под 16.5% годовых. Открыть вклад.",
        #"kk": "{name}, сізде бос қаражат {balance} ₸ бар. Оларды жылдық 16.5% мөлшерлемесімен депозитке салыңыз. Депозит ашыңыз.",
        #"en": "{name}, you have free funds of {balance} ₸. Place them in a deposit at 16.5% per annum. Open a deposit."
    },
    "Депозит Накопительный": {
        "{name}, вы регулярно пополняете счёт. Накопительный вклад под 15.5% годовых поможет копить с повышенной ставкой. Открыть вклад.",
        #"kk": "{name}, сіз шотты үнемі толықтырасыз. Жинақ депозиті жылдық 15.5% мөлшерлемемен жинауға мүмкіндік береді. Депозит ашыңыз.",
        #"en": "{name}, you regularly add funds to your account. A Savings Deposit at 15.5% per annum will help you save with a higher rate. Open a deposit."
    },
    "Инвестиции": {
        "{name}, попробуйте инвестиции с низким порогом входа и без комиссий на старт. Открыть счёт.",
        #"kk": "{name}, төмен кіру шегімен және бастапқыда комиссиясыз инвестицияны байқап көріңіз. Шот ашыңыз.",
        #"en": "{name}, try investments with a low entry threshold and zero starting fees. Open an account."
    },
    "Золотые слитки": {
        "{name}, отличная возможность диверсифицировать накопления. Покупайте и продавайте золотые слитки в приложении. Узнать подробнее.",
        #"kk": "{name}, жинағыңызды әртараптандырудың тамаша мүмкіндігі. Қосымшада алтын құймаларды сатып алыңыз және сатыңыз. Толығырақ біліңіз.",
        #"en": "{name}, a great opportunity to diversify your savings. Buy and sell gold bars in the app. Learn more."
    }
}

# Маппинг статусов
STATUS_MAPPING = {
    'зп': 'Зарплатный клиент',
    'студ': 'Студент', 
    'премиум': 'Премиальный клиент',
    'стандарт': 'Стандартный клиент'
}

# ----------------------
# Утилиты форматирования
# ----------------------
def fmt_amount(x: float) -> str:
    """Форматирование суммы с пробелами между разрядами"""
    if pd.isna(x) or x < 1:
        return "0"
    val = int(round(x))
    s = f"{val:,}".replace(",", " ")
    return s

def format_categories(categories: List[str]) -> str:
    """Форматирование списка категорий с правильными союзами"""
    if not categories:
        return ""
    if len(categories) == 1:
        return categories[0]
    elif len(categories) == 2:
        return f"{categories[0]} и {categories[1]}"
    else:
        return ", ".join(categories[:-1]) + " и " + categories[-1]

# ----------------------
# Загрузка данных
# ----------------------
def load_data(data_folder='.'):
    """Загружает все данные из отдельных файлов и объединяет их"""
    
    # 1. Загружаем профили клиентов
    clients_path = os.path.join(data_folder, 'clients.csv')
    df_clients = pd.read_csv(clients_path)
    
    # Преобразуем статусы к официальным значениям
    df_clients['status'] = df_clients['status'].map(STATUS_MAPPING).fillna(df_clients['status'])
    print(f"Загружено {len(df_clients)} клиентов из {clients_path}")
    
    # 2. Загружаем и объединяем все транзакции
    transactions_files = glob.glob(os.path.join(data_folder, 'client_*_transactions_3m.csv'))
    df_transactions_list = []
    
    for file_path in transactions_files:
        try:
            df_temp = pd.read_csv(file_path)
            # Оставляем только нужные колонки по ТЗ
            df_temp = df_temp[['client_code', 'date', 'category', 'amount', 'currency']]
            df_transactions_list.append(df_temp)
        except Exception as e:
            print(f"Ошибка загрузки {file_path}: {e}")
    
    df_transactions = pd.concat(df_transactions_list, ignore_index=True)
    print(f"Загружено {len(df_transactions)} транзакций из {len(transactions_files)} файлов")
    
    # 3. Загружаем и объединяем все переводы
    transfers_files = glob.glob(os.path.join(data_folder, 'client_*_transfers_3m.csv'))
    df_transfers_list = []
    
    for file_path in transfers_files:
        try:
            df_temp = pd.read_csv(file_path)
            # Оставляем только нужные колонки по ТЗ
            df_temp = df_temp[['client_code', 'date', 'type', 'direction', 'amount', 'currency']]
            df_transfers_list.append(df_temp)
        except Exception as e:
            print(f"Ошибка загрузки {file_path}: {e}")
    
    df_transfers = pd.concat(df_transfers_list, ignore_index=True)
    print(f"Загружено {len(df_transfers)} переводов из {len(transfers_files)} файлов")
    
    return df_clients, df_transactions, df_transfers

# ----------------------
# Фичи / сигналы
# ----------------------
def compute_client_features(clients: pd.DataFrame,
                            transactions: pd.DataFrame,
                            transfers: pd.DataFrame) -> pd.DataFrame:
    # Предобработка дат
    transactions['date'] = pd.to_datetime(transactions['date'])
    transfers['date'] = pd.to_datetime(transfers['date'])

    # Анализ транзакций
    tx = transactions.copy()
    tx['is_spend'] = tx['amount'] > 0
    spends = tx[tx['is_spend']].groupby(['client_code', 'category'])['amount'].sum().unstack(fill_value=0)

    # Анализ переводов для FX
    fx_ops = transfers[transfers['type'].isin(['fx_buy', 'fx_sell'])]
    fx_ops_count = fx_ops.groupby('client_code').size().rename('fx_ops_count')
    # Определяем основную валюту обмена
    main_fx_curr = fx_ops.groupby('client_code')['currency'].agg(
        lambda x: x.mode()[0] if not x.mode().empty else 'USD').rename('main_fx_curr')

    # Категории для разных продуктов (в monthly эквиваленте)
    travel_cats = ['Путешествия', 'Такси', 'Отели', 'АЗС']
    travel_spend = tx[tx['category'].isin(travel_cats) & tx['is_spend']].groupby('client_code')['amount'].sum().rename('travel_spend') / 3
    travel_count = tx[tx['category'].isin(travel_cats)].groupby('client_code').size().rename('travel_count') / 3

    premium_cats = ['Кафе и рестораны', 'Ювелирные украшения', 'Косметика и Парфюмерия']
    premium_spend = tx[tx['category'].isin(premium_cats) & tx['is_spend']].groupby('client_code')['amount'].sum().rename('premium_spend') / 3

    online_cats = ['Едим дома', 'Смотрим дома', 'Играем дома', 'Кино']
    online_spend = tx[tx['category'].isin(online_cats) & tx['is_spend']].groupby('client_code')['amount'].sum().rename('online_spend') / 3

    # Анализ переводов (monthly)
    transfers['is_in'] = transfers['direction'] == 'in'
    salary_income = transfers[transfers['type'] == 'salary_in'].groupby('client_code')['amount'].sum().rename('salary_income') / 3
    total_inflow = transfers[transfers['is_in']].groupby('client_code')['amount'].sum().rename('total_inflow') / 3
    total_outflow = transfers[~transfers['is_in']].groupby('client_code')['amount'].sum().rename('total_outflow') / 3
    
    # Признак потребности в кредите
    has_loan_payments = (transfers['type'] == 'loan_payment_out').groupby(transfers['client_code']).any().rename('has_loan_payments')
    
    # Активность снятия наличных
    atm_activity = transfers[transfers['type'] == 'atm_withdrawal'].groupby('client_code')['amount'].sum().rename('atm_activity') / 3
    
    # Операции с рассрочкой
    has_installments = (transfers['type'] == 'installment_payment_out').groupby(transfers['client_code']).any().rename('has_installments')

    # Собираем все фичи вместе
    feats = clients.set_index('client_code').copy()
    feats = feats.join(spends, how='left').fillna(0)
    feats = feats.join(travel_spend, how='left').fillna(0)
    feats = feats.join(travel_count, how='left').fillna(0)
    feats = feats.join(premium_spend, how='left').fillna(0)
    feats = feats.join(online_spend, how='left').fillna(0)
    feats = feats.join(salary_income, how='left').fillna(0)
    feats = feats.join(total_inflow, how='left').fillna(0)
    feats = feats.join(total_outflow, how='left').fillna(0)
    feats = feats.join(has_loan_payments, how='left').fillna(False)
    feats = feats.join(has_installments, how='left').fillna(False)
    feats = feats.join(atm_activity, how='left').fillna(0)
    feats = feats.join(fx_ops_count, how='left').fillna(0)
    feats = feats.join(main_fx_curr, how='left')
    feats['main_fx_curr'].fillna('USD', inplace=True)

    # Общие траты (monthly)
    feats['total_spend'] = tx[tx['is_spend']].groupby('client_code')['amount'].sum().fillna(0) / 3

    # Поиск топ-3 категорий для кредитной карты (исключая travel и premium)
    def get_top_categories(client_spends):
        exclude_cats = travel_cats + premium_cats
        filtered = client_spends.drop(index=exclude_cats, errors='ignore')
        return filtered.nlargest(3)

    top_cats_map = {}
    grouped = tx[tx['is_spend']].groupby('client_code')
    for cid, g in grouped:
        s = g.groupby('category')['amount'].sum() / 3  # monthly
        top_cats_map[cid] = get_top_categories(s)

    feats['top_cats_series'] = feats.index.map(lambda x: top_cats_map.get(x, pd.Series(dtype=float)))
    
    # Определяем последний активный месяц для пуша
    last_month_per_client = tx.groupby('client_code')['date'].max().dt.month
    feats['last_active_month'] = feats.index.map(lambda x: last_month_per_client.get(x, tx['date'].max().month))

    return feats.reset_index()

# ----------------------
# Метрики выгоды (переработано)
# ----------------------
def benefit_score_for_all(feat_row: pd.Series) -> Dict[str, Tuple[float, Dict]]:
    res = {}

    balance = float(feat_row.get('avg_monthly_balance_KZT', 0))
    total_spend = float(feat_row.get('total_spend', 1))

    # -------------------------
    # 1. Карта для путешествий
    # -------------------------
    travel_cats = ['Путешествия', 'Такси', 'Отели', 'АЗС']
    travel_spend = sum([float(feat_row.get(cat, 0)) for cat in travel_cats])
    travel_benefit = min(travel_spend * 0.04, 50000)  # Лимит 50к
    travel_count = int(feat_row.get('travel_count', 0))
    travel_score = travel_benefit + (travel_count * 1000)
    res["Карта для путешествий"] = (
        travel_score,
        {"benefit": travel_benefit, "spend": travel_spend, "trips_count": travel_count}
    )

    # -------------------------
    # 2. Премиальная карта
    # -------------------------
    premium_cats = ['Кафе и рестораны', 'Ювелирные украшения', 'Косметика и Парфюмерия']
    premium_spend = sum([float(feat_row.get(cat, 0)) for cat in premium_cats])
    
    # Определяем уровень кешбэка по балансу
    if balance >= 6000000:
        base_cashback = 0.04
    elif balance >= 1000000:
        base_cashback = 0.03
    else:
        base_cashback = 0.02
    
    premium_benefit = min((base_cashback * total_spend) + (0.04 * premium_spend), 100000)  # Лимит 100к
    # Экономия на снятиях наличных
    atm_savings = min(float(feat_row.get('atm_activity', 0)) * 0.01, 30000)
    
    premium_score = premium_benefit + atm_savings + (balance / 1000000)
    res["Премиальная карта"] = (
        premium_score,
        {"benefit": premium_benefit, "balance": balance, "premium_spend": premium_spend, "atm_savings": atm_savings}
    )

    # -------------------------
    # 3. Кредитная карта
    # -------------------------
    top_series = feat_row.get('top_cats_series', pd.Series(dtype=float))
    online_spend = float(feat_row.get('online_spend', 0))
    
    if isinstance(top_series, pd.Series) and not top_series.empty:
        top3_sum = top_series.sum()
        credit_benefit = min((top3_sum * 0.10) + (online_spend * 0.10), 50000)  # Лимит 50к
    else:
        credit_benefit = min(online_spend * 0.10, 50000)
    
    # Бонус за использование рассрочки
    if feat_row.get('has_installments', False):
        credit_benefit += 5000
    
    credit_score = credit_benefit
    res["Кредитная карта"] = (credit_score, {"benefit": credit_benefit, "top3": top_series, "online_spend": online_spend})

    # -------------------------
    # 4. Обмен валют
    # -------------------------
    fx_ops_count = int(feat_row.get('fx_ops_count', 0))
    # Предполагаем экономию 1% на каждой операции
    fx_benefit = min(fx_ops_count * 1000, 20000)  # Лимит 20к
    fx_score = fx_benefit
    res["Обмен валют"] = (fx_score, {"benefit": fx_benefit, "fx_curr": feat_row.get('main_fx_curr', 'USD'), "fx_ops": fx_ops_count})

    # -------------------------
    # 5. Кредит наличными
    # -------------------------
    loan_score = 0
    outflow = float(feat_row.get('total_outflow', 0))
    inflow = float(feat_row.get('total_inflow', 0))
    
    # Рекомендуем только при явных сигналах
    if (feat_row.get('has_loan_payments', False) or 
        (outflow > inflow * 1.5 and balance < 200000)):
        loan_need = max(outflow - inflow, 0)
        loan_score = min(loan_need * 0.1, 50000)  # Ограничиваем скор
    
    res["Кредит наличными"] = (loan_score, {"need": loan_score, "outflow": outflow})

    # -------------------------
    # 6. Депозиты
    # -------------------------
    free_balance = max(0.0, balance - (total_spend / 3))
    
    # 6a. Мультивалютный депозит
    fx_activity = feat_row.get('fx_ops_count', 0) > 1
    mult_deposit_benefit = free_balance * 0.05 / 12  # 5% годовых
    mult_deposit_score = mult_deposit_benefit
    res["Депозит Мультивалютный"] = (
        mult_deposit_score,
        {"benefit": mult_deposit_benefit, "fx_curr": feat_row.get('main_fx_curr', 'USD')}
    )

    # 6b. Сберегательный депозит
    savings_benefit = free_balance * 0.165 / 12  # 16.5% годовых
    savings_deposit_score = savings_benefit
    res["Депозит Сберегательный"] = (
        savings_deposit_score,
        {"benefit": savings_benefit, "balance": free_balance}
    )

    # 6c. Накопительный депозит
    savings_benefit = free_balance * 0.155 / 12  # 15.5% годовых
    savings_deposit_score = savings_benefit
    res["Депозит Накопительный"] = (
        savings_deposit_score,
        {"benefit": savings_benefit, "balance": free_balance}
    )

    # -------------------------
    # 7. Инвестиции
    # -------------------------
    invest_benefit = free_balance * 0.07 / 12  # 7% годовых
    invest_score = invest_benefit
    res["Инвестиции"] = (invest_score, {"benefit": invest_benefit})

    # -------------------------
    # 8. Золотые слитки
    # -------------------------
    gold_benefit = free_balance * 0.01 / 12  # Консервативная оценка
    gold_score = gold_benefit
    res["Золотые слитки"] = (gold_score, {"benefit": gold_benefit})

    return res

# ----------------------
# Генерация пуша
# ----------------------
def generate_push(client_row: pd.Series, product: str, info: Dict, last_month: int) -> str:
    name = client_row.get('name', '')
    if isinstance(name, str) and ' ' in name:
        name = name.split()[0]  # Берем только имя

    tpl = TEMPLATES.get(product, "{name}, у вас есть рекомендация. Открыть приложение.")

    # Форматируем данные для подстановки
    params = {
        "name": name,
        "month": MONTHS_RU.get(last_month, f"{last_month}-й месяц"),
        "trips_count": "",
        "spend": fmt_amount(info.get('spend', 0)),
        "benefit": fmt_amount(info.get('benefit', 0)),
        "balance": fmt_amount(info.get('balance', client_row.get('avg_monthly_balance_KZT', 0))),
        "categories": "",
        "fx_curr": info.get('fx_curr', 'USD'),
        "fx_ops": info.get('fx_ops', 0)
    }

    # Обрабатываем категории для кредитной карты
    if product == "Кредитная карта":
        top3 = info.get('top3')
        if isinstance(top3, pd.Series) and not top3.empty:
            categories = list(top3.index)
            params['categories'] = format_categories(categories)

    # Обрабатываем поездки для travel карты
    if product == "Карта для путешествий":
        trips_count = info.get('trips_count', 0)
        if trips_count > 0:
            trips_count = round(trips_count)  # Округляем до целого
            if trips_count % 10 == 1 and trips_count % 100 != 11:
                params['trips_count'] = f"{trips_count} поездку"
            elif 2 <= trips_count % 10 <= 4 and not (12 <= trips_count % 100 <= 14):
                params['trips_count'] = f"{trips_count} поездки"
            else:
                params['trips_count'] = f"{trips_count} поездок"

    # Генерируем текст
    text = tpl.format(**params)

    # Убираем возможные дубли пробелов и обрезаем если слишком длинный
    text = text.replace("  ", " ")
    if len(text) > 220:
        text = text[:217].rstrip() + "..."

    return text

# ----------------------
# Основная процедура
# ----------------------
def run(data_folder='.', out_csv='result_pushes.csv'):
    # Загружаем данные
    df_clients, df_transactions, df_transfers = load_data(data_folder)
    
    # Вычисляем фичи
    feats = compute_client_features(df_clients, df_transactions, df_transfers)
    
    # Обрабатываем каждого клиента
    rows = []
    for _, client_row in feats.iterrows():
        try:
            scores = benefit_score_for_all(client_row)
            ranked = sorted(scores.items(), key=lambda kv: kv[1][0], reverse=True)
            
            if ranked:  # Если есть результаты
                top_product, (top_score, info) = ranked[0]
                last_month = client_row.get('last_active_month', 6)
                push = generate_push(client_row, top_product, info, last_month)
                
                rows.append({
                    "client_code": client_row['client_code'],
                    "product": top_product,
                    "push_notification": push
                })
        except Exception as e:
            print(f"Ошибка обработки клиента {client_row.get('client_code', 'unknown')}: {e}")
    
    # Сохраняем результаты
    out_df = pd.DataFrame(rows)
    out_df.to_csv(out_csv, index=False, encoding='utf-8-sig')
    print(f"Сохранено {len(out_df)} записей в {out_csv}")

if __name__ == "__main__":
    run(data_folder="case 1")
