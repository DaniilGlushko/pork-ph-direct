"""Расчёт: сколько заработает своя компания в Маниле на свинине Талины без посредников.

Все входные цифры — из документов проекта и открытых источников (см. README).
Запуск: python3 calc.py  → печатает таблицы и пишет data.json для страницы.
"""
import json

# Курсы (ЦБ РФ на 31.10.2026; песо — как в сравнении юрлиц, entity-budget-asia)
RUB_USD = 80.6
PHP_USD = 63.7
RUB_PHP = RUB_USD / PHP_USD

MANILA_COSTS = 20.0      # ₱/кг: порт, брокер, SPSIC, холодильник, доставка — оценка, уточнить у брокера
FINANCING = 0.03         # 3 месяца оборота денег под ~12% годовых
FIXED_RUB = 9.0e6        # своя компания в Маниле, первый год (entity-budget-asia)
TAX = 0.25               # налог на прибыль на Филиппинах
CONTAINER_T = 27         # тонн в рефконтейнере (прайс Талины)

# Оптовая цена импортной заморозки в Маниле, ₱/кг
WHOLESALE_RATIO = 0.84   # опт / розница по ценам Бона (лопатка 285/340, грудинка 335/395, рёбра 310/370)
SELL = {
    "jowl":    (210, "₱210–250: опт импортной обрези 80/20–70/30 для переработчиков (Бон, 14.10). Берём нижнюю границу"),
    "belly":   (round(300 * WHOLESALE_RATIO), "грудинка-заморозка ₱300 в рознице (Минсельхоз PH, 20.10.2026) × 0,84"),
    "shoulder":(round(240 * WHOLESALE_RATIO), "лопатка-заморозка ₱240 в рознице (Минсельхоз PH, 20.10.2026) × 0,84"),
    "ribs_sh": (218, "рёбра: опт местной охлаждёнки ₱290–330 (Бон) минус 25% за заморозку"),
    "ribs":    (240, "рёбра: опт местной охлаждёнки ₱290–330 (Бон) минус 20–25% за заморозку"),
}

# Позиции: (название, CFR факт 2026 $/кг или None, CFR прайс 16.10.2026 $/кг, ключ цены продажи)
CUTS = [
    ("Щековина б/ш",          1.89, 3.10, "jowl"),
    ("Грудинка б/к",          3.15, 3.84, "belly"),
    ("Грудинка н/к",          2.95, 3.87, "belly"),
    ("Лопатка б/к",           None, 3.90, "shoulder"),
    ("Окорок б/к",            None, 3.97, "shoulder"),
    ("Рёбра подлопаточные",   None, 2.25, "ribs_sh"),
    ("Рёбра с грудинки",      None, 3.40, "ribs"),
    ("Рёбра корейки",         None, 3.94, "ribs"),
    ("Шкурка хребтовая",      None, 1.03, None),
    ("Шкурка корпусная",      None, 1.29, None),
    ("Рульки",                None, 2.52, None),
]

# Отгрузки 2026 (февраль–июль), тонн
SHIP_2026 = {"Щековина б/ш": 295.4, "Грудинка б/к": 54.0, "Грудинка н/к": 27.0}


def landed(cfr_usd, duty):
    """Себестоимость 1 кг на складе в Маниле, ₱."""
    return (cfr_usd * PHP_USD * (1 + duty) + MANILA_COSTS) * (1 + FINANCING)


def margin(cfr_usd, sell_key, duty):
    if cfr_usd is None or sell_key is None:
        return None
    return SELL[sell_key][0] - landed(cfr_usd, duty)


def mix_margin(duty, jowl_price=None):
    """Маржа ₱/кг на ассортимент 2026 года по фактическим ценам 2026."""
    total = sum(SHIP_2026.values())
    m = 0.0
    for name, fact, _, key in CUTS:
        if name in SHIP_2026:
            sell = jowl_price if (key == "jowl" and jowl_price) else SELL[key][0]
            m += (sell - landed(fact, duty)) * SHIP_2026[name] / total
    return m


def net_profit_rub(tonnes, m_php):
    pre_tax = tonnes * 1000 * m_php * RUB_PHP - FIXED_RUB
    return pre_tax * (1 - TAX) if pre_tax > 0 else pre_tax


def tonnes_for(net_rub, m_php):
    return (net_rub / (1 - TAX) + FIXED_RUB) / (m_php * RUB_PHP) / 1000


cuts_out = []
for name, fact, oct_, key in CUTS:
    cuts_out.append({
        "name": name, "fact": fact, "oct": oct_,
        "sell": SELL[key][0] if key else None,
        "sell_src": SELL[key][1] if key else "цены покупателя нет: запрошена у Harvey и Jervis",
        "landed_oct": round(landed(oct_, 0.15)),
        "m_oct": None if key is None else round(margin(oct_, key, 0.15)),
        "landed_fact": round(landed(fact, 0.15)) if fact else None,
        "m_fact": round(margin(fact, key, 0.15)) if fact else None,
    })

scen = {
    "base": mix_margin(0.15),
    "high": mix_margin(0.15, jowl_price=250),
    "no_quota": mix_margin(0.25),
    "da_quota": mix_margin(0.30),
}
volumes = [376, 750, 1500, 2500, 3500, 5000]
table = [{"t": v, "cont_m": v / CONTAINER_T / 12,
          **{k: net_profit_rub(v, m) / 1e6 for k, m in scen.items()}} for v in volumes]
need = {k: tonnes_for(100e6, m) for k, m in scen.items()}

total_2026 = sum(SHIP_2026.values())
landed_mix = sum(landed(f, 0.15) * SHIP_2026[n] for n, f, _, _ in CUTS if n in SHIP_2026) / total_2026
working_cap_rub = need["base"] / 4 * 1000 * landed_mix * RUB_PHP  # 3 месяца оборота

out = {
    "rates": {"RUB_USD": RUB_USD, "PHP_USD": PHP_USD, "RUB_PHP": RUB_PHP},
    "params": {"manila_costs": MANILA_COSTS, "financing": FINANCING, "fixed_rub": FIXED_RUB, "tax": TAX},
    "cuts": cuts_out,
    "scen_php": scen,
    "scen_rub": {k: v * RUB_PHP for k, v in scen.items()},
    "table": table,
    "need_t": need,
    "need_cont_m": {k: v / CONTAINER_T / 12 for k, v in need.items()},
    "working_cap_rub": working_cap_rub,
    "landed_mix": landed_mix,
    "fact_2026_t": total_2026,
}

if __name__ == "__main__":
    print(f"₽ за ₱: {RUB_PHP:.3f}")
    for r in cuts_out:
        print({k: v for k, v in r.items() if k != "sell_src"})
    for k, v in scen.items():
        print(f"{k}: маржа ₱{v:.1f}/кг = {v*RUB_PHP:.1f} ₽/кг; на 100 млн ₽ нужно {need[k]:.0f} т "
              f"= {need[k]/CONTAINER_T/12:.1f} конт./мес")
    for r in table:
        print({k: round(v, 1) for k, v in r.items()})
    print(f"оборотные деньги при {need['base']:.0f} т/год: {working_cap_rub/1e6:.0f} млн ₽")
    json.dump(out, open("data.json", "w"), ensure_ascii=False, indent=1)
