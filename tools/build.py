import os, re, datetime, collections
import icalendar, jdatetime

# Rebuilds ../stock-land-persian-calendar.ics from source.ics (the original
# occasion data) and tips.txt. Run: python3 tools/build.py
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'stock-land-persian-calendar.ics')
cal = icalendar.Calendar.from_ical(open(os.path.join(HERE, 'source.ics'), 'rb').read())
TIPS = [l.split('|', 1) for l in open(os.path.join(HERE, 'tips.txt'), encoding='utf-8').read().splitlines()
        if l.strip() and not l.startswith('#')]
INSTAGRAM = 'https://www.instagram.com/stock_land.ir/'

FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
fa = lambda s: str(s).translate(FA)
MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
          'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
SOLAR_HOLIDAYS = {(1, 1), (1, 2), (1, 3), (1, 4), (1, 12), (1, 13),
                  (3, 14), (3, 15), (11, 22), (12, 29)}
LUNAR_HOLIDAY_KEYS = ['تاسوعا', 'عاشورا', 'اربعین', 'رحلت پیامبر', 'شهادت امام رضا',
                      'شهادت امام حسن عسکری', 'میلاد پیامبر', 'شهادت حضرت فاطمه',
                      'ولادت امام علی', 'مبعث', 'نیمه شعبان', 'ولادت حضرت قائم',
                      'ولادت امام زمان', 'ولادت حضرت مهدی', 'شهادت حضرت علی',
                      'شهادت امام علی', 'عید سعید فطر', 'شهادت امام جعفر صادق',
                      'عید سعید قربان', 'غدیر', 'ولادت امام مهدی', 'رحلت رسول',
                      'میلاد رسول اکرم و امام جعفر']
NOT_HOLIDAY = ['النقی', 'اهل سنت']
is_holiday_occ = lambda o: any(k in o for k in LUNAR_HOLIDAY_KEYS) and not any(x in o for x in NOT_HOLIDAY)
MONTH_EMOJI = ['🌱', '🌷', '🌾', '☀️', '🍉', '🍇', '🍂', '🍁', '🌧', '❄️', '⛄️', '🌸']
GREG_MONTHS = ['ژانویه', 'فوریه', 'مارس', 'آوریل', 'مه', 'ژوئن', 'ژوئیه', 'اوت',
               'سپتامبر', 'اکتبر', 'نوامبر', 'دسامبر']
FESTIVALS = {(9, 30): ('🍉', 'شب یلدا'), (11, 10): ('🔥', 'جشن سده')}
MOURNING = re.compile(r'(شهادت|وفات|رحلت|تاسوعا|عاشورا|اربعین)')
BIRTH = re.compile(r'^(ولادت|میلاد)')
CELEBRATION = re.compile(r'(جشن|عید|نوروز|یلدا)')

def occasion_emoji(o):
    if MOURNING.search(o): return '🖤'
    if BIRTH.search(o): return '💐'
    if CELEBRATION.search(o): return '🎉'
    return None

def last_tuesday(jy):
    d = jdatetime.date(jy + 1, 1, 1) - datetime.timedelta(days=1)
    while d.weekday() != 3:  # jdatetime: Saturday=0, Tuesday=3
        d -= datetime.timedelta(days=1)
    return d

def countdown(j):
    yalda = jdatetime.date(j.year, 9, 30)
    nowruz = jdatetime.date(j.year + 1, 1, 1)
    dy, dn = (yalda - j).days, (nowruz - j).days
    if dy == 1: return ('🍉', 'فردا شب یلدا')
    if 0 < dy <= 10: return ('🍉', f'{fa(dy)} روز تا یلدا')
    if dn == 1: return ('🐟', 'فردا نوروز')
    if 0 < dn <= 14: return ('🐟', f'{fa(dn)} روز تا نوروز')
    return None

NOTABLE = re.compile(r'^(روز |جشن|عید|شهادت|ولادت|میلاد|رحلت|تاسوعا|عاشورا|اربعین|مبعث|نیمه|سالروز|هفته)')

info, weekly = {}, {}
for e in cal.walk('VEVENT'):
    uid = str(e['UID'])
    if 'jalali-info' in uid:
        info[e['DTSTART'].dt] = e
    elif 'jalali-date' in uid:
        pass
    else:
        weekly[e['DTSTART'].dt] = e

stamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
out = icalendar.Calendar()
for k, v in cal.items():
    out.add(k, v)

holiday_count = collections.Counter()
for g in sorted(info):
    e = info[g]
    j = jdatetime.date.fromgregorian(date=g)
    weekday = str(e['SUMMARY']).split(' - ')[0].strip()
    lines = str(e['DESCRIPTION']).split('\n')
    occasions = [' '.join(x.split()) for x in lines[1:] if x.strip()] if lines[0].startswith('مناسبت های') else []
    occasions = [o for o in occasions if 'چهارشنبه سوری' not in o]
    holiday = (j.month, j.day) in SOLAR_HOLIDAYS or any(is_holiday_occ(o) for o in occasions)
    if holiday:
        holiday_count[j.year] += 1
    solar = (j.month, j.day) in SOLAR_HOLIDAYS
    festival = FESTIVALS.get((j.month, j.day))
    if j == last_tuesday(j.year):
        festival = ('🔥', 'چهارشنبه‌سوری')
    cd = countdown(j)

    date_str = f'{fa(j.day)} {MONTHS[j.month - 1]}'
    if holiday:
        pick = (occasions[0] if solar and occasions else
                next((o for o in occasions if is_holiday_occ(o)), None))
        emoji = '🔴'
    elif festival:
        emoji, pick = festival
    elif cd:
        emoji, pick = cd
    else:
        pick = next((o for o in occasions if NOTABLE.match(o) and len(o) <= 40), None)
        emoji = (pick and occasion_emoji(pick)) or MONTH_EMOJI[j.month - 1]
    # Two events per day, like separate pills in month view and the medium
    # widget. iOS sorts all-day events by title, so the plain-text weekday
    # line lands above the emoji-led date line; month view clips long titles
    # from their start, so the weekday goes last.
    lead = pick if (festival or cd) else (f'{fa(pick)} · ' if pick else '') + weekday
    titles = {'info': lead, 'date': f'{emoji} {date_str}'}

    nowruz_days = (jdatetime.date(j.year + 1, 1, 1) - j).days
    desc = [f'{weekday} {date_str} {fa(j.year)}',
            f'{fa(g.day)} {GREG_MONTHS[g.month - 1]} {fa(g.year)}']
    if holiday:
        desc.append('🔴 تعطیل رسمی')
    if festival and not holiday:
        desc.append(f'{festival[0]} {festival[1]}')
    if occasions:
        desc += ['', 'مناسبت‌های این روز:'] + [f'• {fa(o)}' for o in occasions]
    tip = weekly.get(g)
    if tip:
        title, body = TIPS[sorted(weekly).index(g) % len(TIPS)]
        desc += ['', f'🧠 نکته هفته: {title.strip()}', body.strip(),
                 '', f'آموزش‌های بیشتر در اینستاگرام استوک لند:', INSTAGRAM]
    desc += ['', f'🐟 {fa(nowruz_days)} روز تا نوروز', 'تقویم فارسی استوک لند']

    for kind, title in titles.items():
        ev = icalendar.Event()
        ev.add('UID', f'stockland-jalali-{kind}-{g:%Y%m%d}@stock-land')
        ev.add('DTSTAMP', stamp)
        ev.add('DTSTART', g)
        ev.add('DTEND', g + datetime.timedelta(days=1))
        ev.add('SUMMARY', title)
        ev.add('DESCRIPTION', '\n'.join(desc))
        ev.add('TRANSP', 'TRANSPARENT')
        if tip and kind == 'date':
            ev.add('URL', INSTAGRAM)
            for alarm in tip.walk('VALARM'):
                ev.add_component(alarm)
        out.add_component(ev)

open(OUT, 'wb').write(out.to_ical())
print('days', len(info), 'weekly', len(weekly), 'holidays per jalali year', dict(holiday_count))
