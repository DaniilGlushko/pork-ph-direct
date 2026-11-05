"""Собирает index.html из расчёта calc.py. Запуск: python3 build.py"""
import calc

d = calc.out
R = d["rates"]


def n(x, digits=0):
    """Число по-русски: пробел между тысячами, запятая в дробях."""
    s = f"{x:,.{digits}f}".replace(",", " ").replace(".", ",")
    return s.replace("-", "−")


def money_cell(v):
    cls = "ok" if v >= 100 else ("neg" if v < 0 else "")
    return f'<td class="num {cls}">{n(v)}</td>'


def m_cell(v):
    if v is None:
        return '<td class="num muted">—</td>'
    cls = "ok" if v > 0 else "neg"
    sign = "+" if v > 0 else ""
    return f'<td class="num {cls}">{sign}{n(v)}</td>'


need = d["need_t"]
need_c = d["need_cont_m"]
pace = next(r for r in d["table"] if r["t"] == 750)

rows_main = "\n".join(
    f'<tr><th scope="row">{n(r["t"])}{" <small>как за полгода 2026</small>" if r["t"] == 376 else ""}'
    f'{" <small>темп 2026</small>" if r["t"] == 750 else ""}</th>'
    f'<td class="num">{n(r["cont_m"], 1)}</td>'
    f'{money_cell(r["base"])}{money_cell(r["high"])}{money_cell(r["no_quota"])}{money_cell(r["da_quota"])}</tr>'
    for r in d["table"]
)
row_need = (
    '<tr class="need"><th scope="row">Нужно на 100 млн ₽</th><td class="num">—</td>'
    + "".join(f'<td class="num">{n(round(need[k], -1))} т<br><small>{n(need_c[k], 1)} конт./мес</small></td>'
              for k in ("base", "high", "no_quota", "da_quota"))
    + "</tr>"
)

rows_cuts = "\n".join(
    f'<tr><th scope="row">{c["name"]}</th>'
    f'<td class="num">{n(c["fact"], 2) if c["fact"] else "—"}</td>'
    f'<td class="num">{n(c["oct"], 2)}</td>'
    f'<td class="num">{n(c["sell"]) if c["sell"] else "—"}</td>'
    f'{m_cell(c["m_fact"])}{m_cell(c["m_oct"])}'
    f'<td class="src">{c["sell_src"]}</td></tr>'
    for c in d["cuts"]
)

sc = d["scen_php"]
sr = d["scen_rub"]
p = d["params"]

html = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Свинина на Филиппины напрямую</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #f7f5f0; --card: #fffefb; --ink: #14213d; --text: #3d4a5c; --muted: #6b7686;
  --line: #e2ded5; --accent: #b4501a; --ok: #1f7a4d; --ok-bg: #e5f3ea; --neg: #b3261e; --neg-bg: #fbe9e7;
  --head: #14213d; --head-ink: #f7f5f0;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #11161f; --card: #19202c; --ink: #eef1f6; --text: #c9d1dc; --muted: #8b96a6;
    --line: #2a3342; --accent: #f2a65a; --ok: #6fd39c; --ok-bg: #173527; --neg: #ff8a80; --neg-bg: #3a1c1a;
    --head: #0b0f16; --head-ink: #eef1f6;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #11161f; --card: #19202c; --ink: #eef1f6; --text: #c9d1dc; --muted: #8b96a6;
  --line: #2a3342; --accent: #f2a65a; --ok: #6fd39c; --ok-bg: #173527; --neg: #ff8a80; --neg-bg: #3a1c1a;
  --head: #0b0f16; --head-ink: #eef1f6;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--text); font: 16px/1.5 Inter, system-ui, -apple-system, sans-serif; }}
header {{ background: var(--head); color: var(--head-ink); padding: 40px 16px 32px; }}
.wrap {{ max-width: 1040px; margin: 0 auto; padding: 0 16px; }}
header .wrap {{ padding: 0; }}
.kicker {{ font-size: 13px; letter-spacing: .06em; text-transform: uppercase; opacity: .7; margin: 0 0 8px; }}
h1 {{ font-size: clamp(26px, 4.5vw, 40px); line-height: 1.15; margin: 0 0 12px; font-weight: 700; }}
header p {{ margin: 0; max-width: 760px; opacity: .85; }}
h2 {{ color: var(--ink); font-size: 22px; margin: 40px 0 8px; }}
.lead {{ margin: 0 0 16px; max-width: 760px; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 24px; }}
.card {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 18px; }}
.card .big {{ font-size: 30px; font-weight: 700; color: var(--ink); line-height: 1.1; }}
.card .big.acc {{ color: var(--accent); }}
.card p {{ margin: 6px 0 0; font-size: 14px; }}
.scroll {{ overflow-x: auto; -webkit-overflow-scrolling: touch; background: var(--card); border: 1px solid var(--line); border-radius: 12px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
thead th {{ color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: .03em; }}
tbody th {{ color: var(--ink); font-weight: 600; white-space: nowrap; }}
tbody th small {{ display: block; font-weight: 400; color: var(--muted); }}
td.num {{ text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }}
td.ok {{ color: var(--ok); background: var(--ok-bg); font-weight: 600; }}
td.neg {{ color: var(--neg); }}
td.muted {{ color: var(--muted); }}
td.src {{ font-size: 12px; color: var(--muted); min-width: 220px; }}
tr.need td, tr.need th {{ background: var(--bg); font-weight: 600; color: var(--ink); }}
tr.need small {{ font-weight: 400; color: var(--muted); }}
.note {{ font-size: 13px; color: var(--muted); margin: 8px 0 0; }}
ul {{ padding-left: 20px; margin: 8px 0; }}
li {{ margin: 6px 0; }}
.box {{ background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: 8px; padding: 14px 16px; margin: 16px 0; }}
a {{ color: var(--accent); }}
footer {{ margin: 48px 0 40px; font-size: 13px; color: var(--muted); }}
b, strong {{ color: var(--ink); }}
</style>
</head>
<body>
<header><div class="wrap">
<p class="kicker">Talina · Филиппины · расчёт на 5 ноября 2026</p>
<h1>Свинина на Филиппины без посредников: сколько можно заработать</h1>
<p>Схема: своя компания в Маниле покупает у завода по цене CFR Манила и сама продаёт мясо филиппинским переработчикам и оптовикам. Ей достаётся то, что сейчас забирают трейдер и филиппинский импортёр. Прибыль ниже считается после пошлины, расходов в порту, оборотных денег, содержания компании и налога на прибыль 25%.</p>
</div></header>

<main class="wrap">
<div class="cards">
  <div class="card"><div class="big acc">≈ {n(round(need["base"], -2))} т в год</div>
    <p>нужно продать, чтобы получить <b>100 млн ₽ чистыми</b>. Это ≈ {n(need_c["base"])} контейнеров в месяц, в 4 раза больше темпа 2026 года</p></div>
  <div class="card"><div class="big">≈ {n(pace["base"])} млн ₽</div>
    <p>чистыми в год при темпе 2026 года: 750 т, около 2 контейнеров в месяц</p></div>
  <div class="card"><div class="big">≈ {n(sr["base"])} ₽ с кг</div>
    <p>остаётся своей компании (₱{n(sc["base"])}) на ассортименте 2026 года (78% щековина, 22% грудинка) по ценам 2026 года</p></div>
</div>

<div class="box"><b>Главное условие:</b> цена завода должна быть на уровне фактических отгрузок 2026 года (щековина ≈ $1,89 за кг CFR). По прайсу от 16 октября (щековина $3,10) своя компания на щековине, грудинке, лопатке и окороке работает в минус: импортная заморозка в Маниле продаётся дешевле. Подробно — в таблице по позициям ниже.</div>

<h2>Тонны → чистая прибыль за год, млн ₽</h2>
<p class="lead">Ассортимент 2026 года по ценам 2026 года. Зелёным — 100 млн ₽ и больше. Колонки показывают, как меняется ответ при другой цене продажи щековины и другой пошлине.</p>
<div class="scroll"><table>
<thead><tr><th>Тонн в год</th><th>Контейнеров в месяц</th><th>Базовый: квота 15%, щековина ₱210</th><th>Щековина продаётся по ₱250</th><th>Без квоты: пошлина 25%</th><th>Пошлину поднимут до 30%</th></tr></thead>
<tbody>
{rows_main}
{row_need}
</tbody></table></div>
<p class="note">Контейнер — 27 т. Маржа на 1 кг: базовый ₱{n(sc["base"], 1)}, щековина по ₱250 — ₱{n(sc["high"], 1)}, без квоты — ₱{n(sc["no_quota"], 1)}, при пошлине 30% — ₱{n(sc["da_quota"], 1)}. Содержание компании {n(p["fixed_rub"] / 1e6)} млн ₽ в год уже вычтено.</p>

<h2>Что нужно для 100 млн ₽ в год</h2>
<ul>
<li><b>Объём ≈ {n(round(need["base"], -2))} т в год</b>, в основном щековина. За полгода 2026 года ушло 295 т щековины. Сколько щековины завод может давать в год — вопрос коммерческой службе.</li>
<li><b>Цена завода как в 2026 году</b>, а не по октябрьскому прайсу.</li>
<li><b>Место в квоте MAV</b> (пошлина 15%). Без квоты нужно ≈ {n(round(need["no_quota"], -2))} т в год.</li>
<li><b>Деньги в обороте ≈ {n(round(d["working_cap_rub"] / 1e6, -1))} млн ₽</b>: три месяца закупок (дорога + продажа + оплата) и уставный капитал компании $200 000 ≈ 16 млн ₽.</li>
<li><b>Подтверждённая цена покупателей щековины.</b> Сейчас она взята по обрези 80/20–70/30 (₱210–250). Щековина жирнее, поэтому цена может оказаться ниже. Это главная неизвестная, её запросили у партнёров в Маниле.</li>
</ul>

<h2>По позициям: сколько остаётся с 1 кг, ₱</h2>
<p class="lead">Себестоимость на складе в Маниле = цена CFR × (1 + пошлина 15%) + ₱{n(p["manila_costs"])} расходов в порту + {n(p["financing"] * 100)}% за деньги в обороте. Остаток = оптовая цена в Маниле минус себестоимость, до содержания компании и налога.</p>
<div class="scroll"><table>
<thead><tr><th>Позиция</th><th>CFR факт 2026, $/кг</th><th>CFR прайс 16.10, $/кг</th><th>Опт в Маниле, ₱/кг</th><th>Остаток по цене 2026</th><th>Остаток по прайсу 16.10</th><th>Откуда цена продажи</th></tr></thead>
<tbody>
{rows_cuts}
</tbody></table></div>
<p class="note">По прайсу от 16 октября в плюсе только подлопаточные рёбра. Для шкурки и рулек нет цены покупателя, поэтому они не посчитаны, хотя по себестоимости (₱98–118 и ₱211) это кандидаты.</p>

<h2>Риски, которые могут изменить ответ</h2>
<ul>
<li>Минсельхоз Филиппин обсуждает паузу на ввоз лопатки, грудинки и окорока на 2 месяца с середины ноября, а также защитные меры против импорта свинины.</li>
<li>Минсельхоз предлагает поднять пошлины на свинину до 30% в квоте и 40% вне квоты. Расширенная квота 204 210 т действует до 31.12.2026.</li>
<li>Расходы в Маниле (₱{n(p["manila_costs"])} с кг) — оценка: портовые сборы за 40-футовый рефконтейнер около $1 070, остальное нужно уточнить у таможенного брокера и холодильника.</li>
<li>Не учтены налог при выводе дивидендов в Россию, дополнительные сотрудники при 10 контейнерах в месяц, колебания курса.</li>
</ul>

<h2>Исходные данные</h2>
<ul>
<li>Отгрузки МПК Атяшевский на Филиппины, февраль–июль 2026: 376 т, 14 контейнеров, цены CFR (данные завода).</li>
<li>Экспортный прайс Талины CFR Манила от 16.10.2026 («с минимальной маржой»).</li>
<li>Оптовые ориентиры по Маниле от партнёров (14.10.2026): лопатка/окорок ₱270–300, грудинка ₱320–350, рёбра ₱290–330, обрезь 80/20–70/30 ₱210–250.</li>
<li>Розница импортной заморозки, Минсельхоз Филиппин, 20.10.2026: лопатка ₱240, грудинка ₱300 — <a href="https://context.ph/2026/10/20/da-moves-to-support-local-hog-producers-amid-low-farmgate-prices/">Context.ph</a>.</li>
<li>Пауза на ввоз: <a href="https://tribune.net.ph/2026/10/22/da-eyes-mid-november-freeze-on-pork-imports">Daily Tribune, 22.10.2026</a>. Повышение пошлин: <a href="https://www.philstar.com/business/2026/11/02/2567165/pork-tariff-hike-seen-stoke-inflation">Philstar, 02.11.2026</a>. Квота MAV 2026: <a href="https://globaltradealert.org/intervention/155764-philippines-minimum-access-volume-for-pork-imports-increased-for-2026-and-2027">Global Trade Alert</a>.</li>
<li>Содержание компании в Маниле ≈ 9 млн ₽ в первый год и капитал $200 000: <a href="https://daniilglushko.github.io/entity-budget-asia/">сравнение юрлиц</a>.</li>
<li>Курсы: $1 = {n(R["RUB_USD"], 1)} ₽ (ЦБ, 31.10.2026), $1 = ₱{n(R["PHP_USD"], 1)}, ₱1 = {n(R["RUB_PHP"], 3)} ₽.</li>
</ul>

<footer>Расчёт воспроизводится скриптом calc.py в этом репозитории: все допущения — в начале файла. Подготовил Д. Глушко.</footer>
</main>
</body>
</html>
"""

open("index.html", "w", encoding="utf-8").write(html)
print("index.html готов")
