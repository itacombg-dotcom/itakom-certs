"""
Генератор на паспорти за БАС — ИТА КОМ ООД  (Лот 1, 2026)
Шрифт: Liberation Serif (= Times New Roman)
"""
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, PageBreak)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from pypdf import PdfReader, PdfWriter
import io

# ── Пътища ────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
SIEMENS_PDF  = os.path.join(BASE, 'Сертификати_Siemens.pdf')
WILO_PDF     = os.path.join(BASE, 'Сертификати_Wilo.pdf')
DANFOSS_PDF  = os.path.join(BASE, 'Сертификати_Danfoss.pdf')
SHEMI_PDF    = os.path.join(BASE, 'SHEMI_AS.pdf')

# Техноописания (конвертирани от RTF с LibreOffice)
TEHNOPIS = {
    '1H0W': os.path.join(BASE, 'Tehnopisanie1H1H.pdf'),
    '1H2W': os.path.join(BASE, 'Tehnopisanie1H1H2W.pdf'),
}

# Всички 8 сертификата (PDF файл, индекс на страница)
CERT_PAGES = [
    (SIEMENS_PDF, 0),   # Siemens RVD
    (SIEMENS_PDF, 1),   # Siemens/Danfoss AVPB (в Siemens PDF)
    (SIEMENS_PDF, 2),   # Siemens VVG
    (SIEMENS_PDF, 3),   # Siemens SAS
    (WILO_PDF,    0),   # Wilo Yonos Maxo
    (DANFOSS_PDF, 0),   # Danfoss XB топлообменник
    (DANFOSS_PDF, 1),   # Danfoss AVPB
    (WILO_PDF,    1),   # Wilo ZRS
]

# ── Шрифтове ──────────────────────────────────────────────────────────────────
FP = '/Users/jeanpierre/Library/Fonts/'
pdfmetrics.registerFont(TTFont('TR',  FP + 'LiberationSerif-Regular.ttf'))
pdfmetrics.registerFont(TTFont('TB',  FP + 'LiberationSerif-Bold.ttf'))
pdfmetrics.registerFont(TTFont('TI',  FP + 'LiberationSerif-Italic.ttf'))
pdfmetrics.registerFont(TTFont('TBI', FP + 'LiberationSerif-BoldItalic.ttf'))

W, H = A4
ML = 2.5*cm; MR = 2.5*cm; MT = 2*cm; MB = 2*cm
TW = W - ML - MR

ORANGE   = colors.HexColor('#F5DEB3')
ORANGE_B = colors.HexColor('#CC8800')

# ── Стилове ───────────────────────────────────────────────────────────────────
def S(name, font='TR', size=11, align=TA_LEFT, leading=15, sb=0, sa=2,
      color=colors.black):
    return ParagraphStyle(name, fontName=font, fontSize=size, alignment=align,
                          leading=leading, spaceBefore=sb, spaceAfter=sa,
                          textColor=color)

N   = S('N')
NC  = S('NC', align=TA_CENTER)
NR  = S('NR', align=TA_RIGHT)
NJ  = S('NJ', align=TA_JUSTIFY, sa=3)
B   = S('B',  font='TB')
BC  = S('BC', font='TB', align=TA_CENTER)
H1  = S('H1', font='TB', size=14, align=TA_CENTER, leading=18, sb=6, sa=6)
H1U = S('H1U', font='TB', size=14, align=TA_CENTER, leading=18, sb=6, sa=6)
H2  = S('H2', font='TB', size=12, align=TA_CENTER, leading=16, sb=4, sa=4)
H3  = S('H3', font='TB', size=11, align=TA_CENTER, leading=15, sb=2, sa=2)
IT  = S('IT', font='TI',  align=TA_CENTER)
IB  = S('IB', font='TBI', align=TA_CENTER)

def _bgv_vvg(dhw):
    """Siemens VVG модел за регулиращ вентил БГВ по мощност."""
    if dhw <= 75:
        return 'VVG 549.15-2.5K'
    elif dhw <= 150:
        return 'VVG 549.20-4K'
    else:
        return 'VVG 549.25-6.3K'

def sp(h): return Spacer(1, h*mm)
def hr(): return HRFlowable(width=TW, thickness=0.5, color=colors.black,
                             spaceAfter=3, spaceBefore=3)

# ── Хедър (ИТА КОМ) ───────────────────────────────────────────────────────────
def header():
    return [
        Paragraph('<u><b>"И Т А   К О М"  ЕООД</b></u>', H1),
        Paragraph('София кв."Враждебна", ул.3-та, №16А', NC),
        sp(6),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# СТР.1 — КОРИЦА
# ══════════════════════════════════════════════════════════════════════════════
def pg1_cover(s):
    dhw = s['dhw']
    schema = 'смесена по БГВ' if dhw > 0 else 'само отопление'
    return [
        Paragraph('<u><b>"И Т А   К О М"  ЕООД</b></u>', H1),
        Paragraph('София кв."Враждебна", ул.3-та, №16А', NC),
        sp(20),
        Paragraph('<u><b>ПАСПОРТ на БЛОКОВА  АБОНАТНА СТАНЦИЯ</b></u>', H1U),
        sp(4),
        Paragraph(f'<b>BAS  {s["type"]}  {s["he"]}/{dhw} kW  №{s["num"]}</b>', H2),
        Paragraph(f'<b>{s.get("month","юни")} 2026</b>', H2),
        sp(4),
        Paragraph('<u><i>"ИТА  КОМ" ООД</i></u>', IB),
        Paragraph('<i>Техническа документация</i>', IT),
        sp(12),
        Table([
            [Paragraph('Мощност:', N), Paragraph(f'<i>отопление  - {s["he"]} kW</i>', N)],
            [Paragraph('', N),         Paragraph(f'<i>битова вода  - {dhw} kW</i>', N)],
            [Paragraph('Схема:', N),   Paragraph(f'<i>{schema}</i>', N)],
            [Paragraph('Обект:', N),   Paragraph(f'<i>{s["addr"]}</i>', N)],
            [Paragraph('Възложител:', N),    Paragraph('<i>ТП СОФИЯ</i>', N)],
            [Paragraph('Производство:', N),  Paragraph('<i>' + s.get("month","юни") + ' 2026  г.</i>', N)],
        ], colWidths=[TW*0.32, TW*0.68],
        style=TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'),
                          ('TOPPADDING', (0,0), (-1,-1), 1),
                          ('BOTTOMPADDING', (0,0), (-1,-1), 1)])),
        sp(18),
        Paragraph('Управител:', N),
        Paragraph('<b>/В. Бояджиев/</b>', B),
        Paragraph(f'<i>София,  {s.get("month","юни")} 2026  г</i>', IT),
        PageBreak(),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# СТР.2 — ПРОТОКОЛ ЗА КАЧЕСТВО
# ══════════════════════════════════════════════════════════════════════════════
def pg2_quality(s):
    return [
        sp(8),
        Paragraph('ПРОТОКОЛ ЗА КАЧЕСТВО', H1),
        sp(2),
        Paragraph(f'№ {s["num"]} – {s.get("month","юни")} 2026 г', NC),
        sp(2),
        Paragraph('издадено от', NC),
        sp(2),
        Paragraph('<u><b>„ИТА КОМ" ЕООД</b></u>', H1U),
        sp(4),
        Paragraph('Наименование на изделието:', NC),
        sp(2),
        Paragraph('БЛОКОВА АБОНАТНА СТАНЦИЯ', BC),
        Paragraph(f'Мощност за отопление: {s["he"]} kW', NC),
        Paragraph(f'Мощност за БГВ: {s["dhw"]} kW', NC),
        Paragraph('Количество: 1 /една/', NC),
        sp(4),
        Paragraph(f'Днес    {s["day"]} {s.get("month","юни")} 2026 г. след извършен оглед на', NC),
        Paragraph(f'Абонатна станция  {s["he"]}/{s["dhw"]} квт за  <b><i>ТП СОФИЯ</i></b>   бе установено:', NC),
        sp(3),
        Paragraph('1. АС е окомплектована съгласно техническата документация', NC),
        Paragraph('2. Спазени са изискванията за качество и работен обхват', NC),
        Paragraph('3. Съоръжението отговаря на работния проект', NC),
        sp(4),
        Paragraph('При констатациите има следните забележки:', NC),
        sp(2),
        *[HRFlowable(width='100%', thickness=0.5, color=colors.black, spaceAfter=8, spaceBefore=2) for _ in range(8)],
        sp(6),
        Paragraph(f'Дата:      {s.get("month","юни")} 2026 г.', N),
        sp(2),
        Paragraph('ПРИЕЛ:', N),
        sp(2),
        Paragraph('/Г Велинов/', N),
        PageBreak(),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# СТР.3 — ГАРАНЦИОННИ УСЛОВИЯ
# ══════════════════════════════════════════════════════════════════════════════
def pg3_warranty_conditions():
    return [
        *header(),
        Paragraph('УВАЖАЕМИ КЛИЕНТИ,', H3),
        sp(4),
        Paragraph(
            'Абонатните станции, произведени от "ИТА КОМ" ООД съответстват на действащите '
            'в България норми и отговарят на изискванията на "Топлофикация". В паспорта на '
            'станцията са приложени сертификатите за качество на основните елементи от състава.',
            NJ),
        sp(6),
        Paragraph('УСЛОВИЯ ЗА ГАРАНЦИОННО ПОДДЪРЖАНЕ', H3),
        sp(3),
        Paragraph(
            'Гаранцията важи 24 месеца от датата на приемане на станцията и е валидна само '
            'при представена гаранционна карта.', NJ),
        Paragraph(
            'През гаранционния период абонатната станция се ремонтира безплатно, ако повредата '
            'е причинена от материален или производствен дефект, установен при нормална '
            'експлоатацията на същата.', NJ),
        Paragraph('При ремонт през гаранционния период гаранцията не се удължава.', NJ),
        Paragraph('Гаранционно поддържане може да бъде отказано при следните случаи:', NJ),
        Paragraph('Лош транспорт;', N),
        Paragraph('Неправилно съхранение;', N),
        Paragraph('Неспазване указанията за монтаж и експлоатация, посочени в паспорта на станцията;', N),
        Paragraph('Направен опит за отстраняване на дефект, технически промени или поправки от страна на неквалифицирани лица;', N),
        Paragraph('Механично повреждане, поради невнимателно боравене със станцията;', N),
        Paragraph('Нормално износване на детайли;', N),
        sp(8),
        Table([
            [Paragraph('Доставчик:', N), Paragraph('Клиент:', NR)],
            [Paragraph('Подпис:____________', N), Paragraph('Подпис:__________', NR)],
            [Paragraph('/____________/', N), Paragraph('/___________/', NR)],
        ], colWidths=[TW/2, TW/2],
        style=TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')])),
        PageBreak(),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# СТР.4 — ГАРАНЦИОННА КАРТА
# ══════════════════════════════════════════════════════════════════════════════
def pg4_warranty_card(s):
    ts = TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DDDDDD')),
        ('FONTNAME', (0,0), (-1,0), 'TB'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ])
    CW = [TW*0.38, TW*0.22, TW*0.30, TW*0.10]

    def row(name, maker, model, qty='1'):
        return [Paragraph(name, N), Paragraph(maker, NC),
                Paragraph(model, NC), Paragraph(qty, NC)]

    rows = [
        [Paragraph('<b>Наименование</b>', BC), Paragraph('<b>Производител</b>', BC),
         Paragraph('<b>Тип/Модел</b>', BC),    Paragraph('<b>Бр</b>', BC)],
        row('Топлообменник ВОИ',       'Danfoss',     s['voi_hex']),
        row('Циркулационна помпа ВОИ', 'WILO',        s['pump_voi']),
        row('Регулиращ вентил ВОИ',    'Siemens',     s['vvg_valve']),
        row('Сервозадвижка ВОИ',       'Siemens',     'SAS31.00'),
        row('Регулатор на налягане',   'Danfoss',
            'AVPB, PN16, Kvs 4' if s['he'] <= 200 else
            'AVPB, PN16, Kvs 6.3' if s['he'] <= 300 else 'AVPB, PN16, Kvs 8'),
        row('Електронен регулатор',    'Siemens',     'RVD 145/109'),
        row('Разширителен съд',        'Aquasystem',  f'{s["exp_vol"]} л'),
    ]

    if s['dhw'] > 0:
        rows += [
            row('Топлообменник БГВ',       'Danfoss', s['bgv_hex']),
            row('Циркулационна помпа БГВ', 'WILO',    s['pump_bgv']),
            row('Регулиращ вентил БГВ',    'Siemens', _bgv_vvg(s['dhw'])),
            row('Сервозадвижка БГВ',       'Siemens', 'SAT31.51'),
            row('Водомер БГВ',             'Zenner',  'MTKD-Qn 4'),
        ]

    rows.append(row('Електрозахранване', '1 x 230 V', '', '1'))

    return [
        *header(),
        Paragraph('<b>ГАРАНЦИОННА  КАРТА</b>', H1),
        Paragraph('на', NC),
        Paragraph(f'<i>BAS {s["type"]} {s["he"]}/{s["dhw"]}  №{s["num"]} – {s.get("month","юни")} 2026 г</i>', IT),
        sp(4),
        Table(rows, colWidths=CW, style=ts),
        sp(4),
        Paragraph(f'Дата на продажба: {s.get("month","юни")} 2026 г', N),
        Paragraph('Гаранционен срок: 24 месеца', N),
        Paragraph('Данни за купувача: ТП СОФИЯ', N),
        PageBreak(),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# СТР.5 — СЕРВИЗЕН ДНЕВНИК
# ══════════════════════════════════════════════════════════════════════════════
def pg5_service_log():
    rows = [
        [Paragraph('<b>ДАТА</b>', BC), Paragraph('<b>ВИД НА РЕМОНТА</b>', BC),
         Paragraph('<b>ОПИСАНИЕ НА ДЕФЕКТА</b>', BC), Paragraph('<b>ПОДПИС</b>', BC)],
        *[['', '', '', ''] for _ in range(4)],
    ]
    tbl = Table(rows, colWidths=[TW*0.18, TW*0.27, TW*0.37, TW*0.18],
                rowHeights=[10*mm, 14*mm, 14*mm, 14*mm, 14*mm],
                style=TableStyle([
                    ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#DDDDDD')),
                    ('FONTNAME', (0,0), (-1,0), 'TB'),
                    ('FONTSIZE', (0,0), (-1,-1), 10),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
    return [
        sp(10),
        Paragraph('<u>СЕРВИЗЕН ДНЕВНИК</u>', B),
        sp(4),
        tbl,
        sp(10),
        Paragraph('Управител:  ......................................', N),
        sp(3),
        Paragraph('/ инж Веселин Бояджиев /', N),
        PageBreak(),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# СТР.6 — ХИДРАВЛИЧНА ПРОБА
# ══════════════════════════════════════════════════════════════════════════════
def pg6_hydro(s):
    bgv_line  = '\nконтур БГВ при налягане от 1,5 МРа' if s['dhw'] > 0 else ''
    pump_bgv  = 'помпи БГВ – 1бр. ' if s['dhw'] > 0 else ''
    return [
        *header(),
        Paragraph('<b>П Р О Т О К О Л</b>', H1),
        sp(4),
        Paragraph('<b>За 2-часова  хидравлична  проба на абонатна станция</b>', H3),
        Paragraph(f'<b>{s["type"]}  {s["he"]}/{s["dhw"]} kW  №{s["num"]} -  {s.get("month","юни")} 2026</b>', H3),
        Paragraph(f'<b>Обект:</b>  {s["addr"]},  гр.София', NC),
        sp(5),
        Paragraph(
            f'Днес, {s["day"]} {s.get("month","юни")} 2026 год. приключи 2 часова хидравлична и функционална '
            f'проба на абонатна станция с мощност {s["he"]}/{s["dhw"]} KW.', NJ),
        Paragraph(
            'При проверката отделните контури на станцията бяха напълнени със студена вода '
            'и бяха изпитани следните възли:', NJ),
        Paragraph('контур ТЕЦ при налягане от 2.4 МРа', N),
        Paragraph(f'контур ВОИ при налягане от 1,0 МРа{bgv_line}', N),
        Paragraph(
            'При завършването на хидравличната и функционалната проба на станцията, '
            'беше констатирано следното:', NJ),
        Paragraph(
            'Пробите бяха извършени при напълнена система с вода и съответните налягания '
            'на станцията в продължение на 2 часа.', NJ),
        Paragraph(
            f'По време на пробите съораженията показаха стабилна работа. Не са установени '
            f'течове и пропуски. Ел. Съоръженията – помпи ВОИ – 1бр. {pump_bgv}както и '
            f'елементите от регулиращата система работеха нормално. Постигнати са '
            f'нормативните изисквания към съоръженията.', NJ),
        Paragraph(
            'Предвид гореизложеното считам, че 2-часовата функционална и хидравлична проба '
            'на станцията е успешна. Станцията е комплектована в съответствие с изискванията '
            'на Техническата документация към нея.', NJ),
        sp(5),
        Paragraph('ПОДПИСАЛИ:', B),
        sp(3),
        Table([
            [Paragraph('извършил изпитването__________________', N), Paragraph('', N)],
            [Paragraph('/ Г.Велинов /', NC), Paragraph('', N)],
            [Paragraph('', N), Paragraph('', N)],
            [Paragraph('н-к ОТК  ________________________________', N), Paragraph('', N)],
            [Paragraph('/ Веселин Бояджиев /', NC), Paragraph('', N)],
        ], colWidths=[TW*0.65, TW*0.35]),
        PageBreak(),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# СТР.7 — ДЕКЛАРАЦИЯ ЗА СЪОТВЕТСТВИЕ
# ══════════════════════════════════════════════════════════════════════════════
def pg7_declaration(s):
    return [
        sp(6),
        Paragraph('<b>съгласно Директива за оценяване съответствието на</b>', H3),
        Paragraph('<b>съоръжения под налягане 2014/68/EU</b>', H3),
        sp(5),
        Table([
            [Paragraph('Производител:', N),
             Paragraph('"ИТА КОМ" ООД гр.София\nул."Проф. Александър Фол" №2,', N)],
            [Paragraph('Адрес на производството:\nгр. София.', N),
             Paragraph('кв.Враждебна, ул."3-та" No 16А,', N)],
            [Paragraph('Продукт:', N),
             Paragraph(
                 f'Абонатна станция с пластинчати топлообменници\n'
                 f'<b>{s["type"]} №{s["num"]}, с мощност {s["he"]}/{s["dhw"]} kW</b>', N)],
            [Paragraph('Тип:\nkW', N),
             Paragraph('ИТА КОМ – 1Н, 1H2W 50 ÷ 5000', N)],
            [Paragraph('Приложима категория на изделието съгласно чл.3.', N),
             Paragraph('II', N)],
            [Paragraph('Процедури за оценка на съответствието по чл.10', N),
             Paragraph('Модул А2', N)],
            [Paragraph('Нотифициран орган:\nгр.София, България', N),
             Paragraph('"ИТЕМ Консулт"ЕООД –\nбул."История славянобългарска"', N)],
            [Paragraph('№ 8\nИдентификационен номер', N),
             Paragraph('1837', N)],
        ], colWidths=[TW*0.42, TW*0.58],
        style=TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'),
                          ('TOPPADDING', (0,0), (-1,-1), 3),
                          ('BOTTOMPADDING', (0,0), (-1,-1), 3)])),
        sp(4),
        Paragraph(
            'Долуподписаният производител удостоверява, че е предприел всички необходими '
            'мерки за това производственият процес, неговото наблюдение и крайното оценяване, '
            'да осигурят съответствието на функционалната група с техническата документация '
            'и с приложимите за нея изисквания на Директива 2014/68/EU, въведена с "Наредба '
            'за съществените изисквания и оценяване съответствието на съоръженията под '
            'налягане".', NJ),
        sp(4),
        Table([[Paragraph('Дата: юни  2026 г.  София', N),
                Paragraph('Управител:', NR)],
               [Paragraph('(В. Бояджиев)', N), Paragraph('', NR)]],
              colWidths=[TW*0.6, TW*0.4],
              style=TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'),
                                ('TOPPADDING', (0,0), (-1,-1), 2),
                                ('BOTTOMPADDING', (0,0), (-1,-1), 2)])),
        sp(3),
        Table([
            [Paragraph('<i>GF  12/8.5-5    „Декларация за</i>',
                       S('gf1', font='TI', size=9, color=ORANGE_B)),
             Paragraph('<i>Издание 2/Изменение 0</i>',
                       S('gf2', font='TI', size=9, color=ORANGE_B, align=TA_CENTER)),
             Paragraph('<i>Стр. 1/ 1</i>',
                       S('gf3', font='TI', size=9, color=ORANGE_B, align=TA_RIGHT))],
            [Paragraph('<i>съответствие"</i>',
                       S('gf4', font='TI', size=9, color=ORANGE_B)), '', ''],
        ], colWidths=[TW*0.45, TW*0.35, TW*0.20],
        style=TableStyle([('BACKGROUND', (0,0), (-1,-1), ORANGE),
                          ('BOX', (0,0), (-1,-1), 0.5, ORANGE_B),
                          ('TOPPADDING', (0,0), (-1,-1), 2),
                          ('BOTTOMPADDING', (0,0), (-1,-1), 2)])),
        PageBreak(),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# СТР.8 — ТЕХНОЛОГИЧНИ РАЗХОДИ
# ══════════════════════════════════════════════════════════════════════════════
def pg8_heat_losses(s):
    dhw    = s['dhw']
    schema = 'смесена по БГВ' if dhw > 0 else 'само отопление'
    return [
        sp(4),
        Paragraph('<u><b>блокова абонатна станция</b></u>', BC),
        sp(2),
        Paragraph(f'<b><i>BAS {s["type"]} {s["he"]}/{dhw} kW  юни  2026 г</i></b>', IB),
        sp(2),
        Paragraph('<b>технологични РАЗХОДИ ОТ ТОПЛООТДАВАНЕ</b>', BC),
        Paragraph('<b>от блокова абонатна Станция</b>', BC),
        sp(6),
        Paragraph(f'1.  Мощност на БАС:       <b><i>отопление              - {s["he"]} kW</i></b>', NC),
        Paragraph(f'                                 <b><i>битова гореща вода /БГВ/ - {dhw} kW</i></b>', NC),
        Paragraph(f'2.  Схема на БАС:            <b><i>{schema}</i></b>', NC),
        Paragraph(f'3.  Обект за монтаж на БАС:  {s["addr"]}.', NC),
        Paragraph('4.  Възложител:               <b><i>ТП СОФИЯ</i></b>', NC),
        Paragraph('5.  Производител на БАС:  <b><i>„ИТА КОМ" ООД, гр. София</i></b>', NC),
        Paragraph(f'6.  Производство на БАС:  <b><i>{s.get("month","юни")} 2026 г.</i></b>', NC),
        Paragraph('7.  Технолог. разходи от топлоотдаване:', NC),
        sp(2),
        Paragraph(f'1.  зимен режим   -   <b><i>{s["brunata_w"]} W</i></b>', NC),
        *(
            [Paragraph(f'2.  летен режим   -   <b><i>{s["brunata_s"]} W</i></b>', NC)]
            if s['dhw'] > 0 else []
        ),
        sp(10),
        Paragraph('Управител:', N),
        Paragraph('..  ..............................', N),
        Paragraph('/ инж В. Бояджиев /', N),
        PageBreak(),
    ]

# ══════════════════════════════════════════════════════════════════════════════
# ГЛАВНА ФУНКЦИЯ
# ══════════════════════════════════════════════════════════════════════════════
def build(s, out_path):
    tmp = '/tmp/passport_body_rl.pdf'
    doc = SimpleDocTemplate(tmp, pagesize=A4,
                            leftMargin=ML, rightMargin=MR,
                            topMargin=MT, bottomMargin=MB)
    story = []
    story += pg1_cover(s)
    story += pg2_quality(s)
    story += pg3_warranty_conditions()
    story += pg4_warranty_card(s)
    story += pg5_service_log()
    story += pg6_hydro(s)
    story += pg7_declaration(s)
    story += pg8_heat_losses(s)
    doc.build(story)

    writer = PdfWriter()

    # 8 основни страницi
    for page in PdfReader(tmp).pages:
        writer.add_page(page)

    # Техноописание (6 стр. от конвертиран RTF)
    tech_reader = PdfReader(TEHNOPIS[s['type']])
    for page in tech_reader.pages:
        writer.add_page(page)

    # Схема (1 страница от SHEMI_AS.pdf)
    shemi_reader = PdfReader(SHEMI_PDF)
    writer.add_page(shemi_reader.pages[s['scheme_idx']])

    # Сертификати — зависят от типа станция
    if s['dhw'] > 0:
        # 1H2W: VVG ×2, XB ×2, ZRS
        cert_pages = [
            (SIEMENS_PDF, 0),   # RVD
            (SIEMENS_PDF, 1),   # AVPB (Siemens PDF)
            (SIEMENS_PDF, 2),   # VVG — ВОИ
            (SIEMENS_PDF, 2),   # VVG — БГВ
            (SIEMENS_PDF, 3),   # SAS
            (WILO_PDF,    0),   # Yonos Maxo
            (WILO_PDF,    1),   # ZRS
            (DANFOSS_PDF, 0),   # XB — ВОИ
            (DANFOSS_PDF, 0),   # XB — БГВ
            (DANFOSS_PDF, 1),   # AVPB
        ]
    else:
        # 1H0W: без ZRS, без втори VVG и XB
        cert_pages = [
            (SIEMENS_PDF, 0),   # RVD
            (SIEMENS_PDF, 1),   # AVPB (Siemens PDF)
            (SIEMENS_PDF, 2),   # VVG
            (SIEMENS_PDF, 3),   # SAS
            (WILO_PDF,    0),   # Yonos Maxo
            (DANFOSS_PDF, 0),   # XB
            (DANFOSS_PDF, 1),   # AVPB
        ]

    cert_readers = {}
    for pdf_path, page_idx in cert_pages:
        if pdf_path not in cert_readers:
            cert_readers[pdf_path] = PdfReader(pdf_path)
        writer.add_page(cert_readers[pdf_path].pages[page_idx])

    with open(out_path, 'wb') as f:
        writer.write(f)

    return len(writer.pages)


# ══════════════════════════════════════════════════════════════════════════════
# ДАННИ ЗА СТАНЦИИТЕ — ЛОТ 1, 2026  (общо 18 бр., 18-та = TODO)
# ══════════════════════════════════════════════════════════════════════════════
STATIONS = [
    dict(num='i1L126',  type='1H0W', he=250, dhw=0,   day='01',
         addr='ЖК Сухата Река, бл.208, Вх.В',
         voi_hex='XB12L-1-80',        pump_voi='Yonos Maxo 40/0.5-12',
         vvg_valve='VVG 549.25-6.3K', exp_vol=250,
         bgv_hex='', pump_bgv='',     scheme_idx=1,
         brunata_w='358,97', brunata_s='325,60'),

    dict(num='i2L126',  type='1H0W', he=200, dhw=0,   day='02',
         addr='ЖК Сухата Река, бл.208, Вх.В',
         voi_hex='XB12L-1-60',        pump_voi='Yonos Maxo 25/0.5-12',
         vvg_valve='VVG 549.20-4K',   exp_vol=200,
         bgv_hex='', pump_bgv='',     scheme_idx=1,
         brunata_w='335,44', brunata_s='308,46'),

    dict(num='i3L126',  type='1H2W', he=200, dhw=75,  day='04',
         addr='бул.Дондуков, №53',
         voi_hex='XB12L-1-60',        pump_voi='Yonos Maxo 25/0.5-12',
         vvg_valve='VVG 549.20-4K',   exp_vol=200,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='352,54', brunata_s='322,03'),

    dict(num='i4L126',  type='1H2W', he=200, dhw=75,  day='05',
         addr='ул.Г.С.Раковски, №61-63',
         voi_hex='XB12L-1-60',        pump_voi='Yonos Maxo 25/0.5-12',
         vvg_valve='VVG 549.20-4K',   exp_vol=200,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='352,54', brunata_s='322,03'),

    dict(num='i5L126',  type='1H2W', he=250, dhw=100, day='10',
         addr='ул.Антими, №75, Вх.1',
         voi_hex='XB12L-1-80',        pump_voi='Yonos Maxo 25/0.5-12',
         vvg_valve='VVG 549.25-6.3K', exp_vol=250,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='365,40', brunata_s='329,17'),

    dict(num='i6L126',  type='1H2W', he=350, dhw=125, day='11',
         addr='ул.Дамянгруев, №10, Вх.1',
         voi_hex='XB12L-1-120',       pump_voi='Yonos Maxo 40/0.5-12',
         vvg_valve='VVG 549.32-10K',  exp_vol=350,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='381,64', brunata_s='345,41'),

    dict(num='i7L126',  type='1H2W', he=300, dhw=100, day='17',
         addr='ул.Владайска, №39',
         voi_hex='XB12L-1-100',       pump_voi='Yonos Maxo 40/0.5-12',
         vvg_valve='VVG 549.32-10K',  exp_vol=300,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='365,40', brunata_s='329,17'),

    dict(num='i8L126',  type='1H2W', he=350, dhw=175, day='18',
         addr='бул.Македония, №9',
         voi_hex='XB12L-1-120',       pump_voi='Yonos Maxo 40/0.5-12',
         vvg_valve='VVG 549.32-10K',  exp_vol=350,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='407,86', brunata_s='360,43'),

    dict(num='i9L126',  type='1H2W', he=200, dhw=75,  day='22',
         addr='ул.АмиБуе, №1',
         voi_hex='XB12L-1-60',        pump_voi='Yonos Maxo 25/0.5-12',
         vvg_valve='VVG 549.20-4K',   exp_vol=200,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='352,54', brunata_s='322,03'),

    dict(num='i10L126', type='1H2W', he=250, dhw=100, day='23',
         addr='ул.ФеликсКаниц, №20, А-Б',
         voi_hex='XB12L-1-80',        pump_voi='Yonos Maxo 25/0.5-12',
         vvg_valve='VVG 549.25-6.3K', exp_vol=250,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='365,40', brunata_s='329,17'),

    dict(num='i11L126', type='1H2W', he=200, dhw=100, day='25',
         addr='ул.Смолянска, №12, А',
         voi_hex='XB12L-1-60',        pump_voi='Yonos Maxo 25/0.5-12',
         vvg_valve='VVG 549.20-4K',   exp_vol=200,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='352,54', brunata_s='322,03'),

    dict(num='i12L126', type='1H2W', he=300, dhw=175, day='29',
         addr='ж.к.Лагера, №38, А',
         voi_hex='XB12L-1-100',       pump_voi='Yonos Maxo 40/0.5-12',
         vvg_valve='VVG 549.32-10K',  exp_vol=300,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='396,76', brunata_s='349,78'),

    dict(num='i13L126', type='1H2W', he=250, dhw=100, day='30',
         addr='ул.Хризантема, №19, А',
         voi_hex='XB12L-1-80',        pump_voi='Yonos Maxo 25/0.5-12',
         vvg_valve='VVG 549.25-6.3K', exp_vol=250,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='365,40', brunata_s='329,17'),

    dict(num='i14L126', type='1H2W', he=300, dhw=200, day='01', month='юли',
         addr='ул.Лерин, №3, А',
         voi_hex='XB12L-1-100',       pump_voi='Yonos Maxo 40/0.5-12',
         vvg_valve='VVG 549.32-10K',  exp_vol=300,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='396,76', brunata_s='349,78'),

    dict(num='i15L126', type='1H2W', he=250, dhw=150, day='02', month='юли',
         addr='ул.Ворино, №16, А',
         voi_hex='XB12L-1-80',        pump_voi='Yonos Maxo 25/0.5-12',
         vvg_valve='VVG 549.25-6.3K', exp_vol=250,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='381,64', brunata_s='345,41'),

    dict(num='i16L126', type='1H2W', he=250, dhw=125, day='03', month='юли',
         addr='ул.Ворино, №52, А',
         voi_hex='XB12L-1-80',        pump_voi='Yonos Maxo 25/0.5-12',
         vvg_valve='VVG 549.25-6.3K', exp_vol=250,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='365,40', brunata_s='329,17'),

    dict(num='i17L126', type='1H2W', he=200, dhw=75,  day='09', month='юли',
         addr='бул.България, №13, А',
         voi_hex='XB12L-1-60',        pump_voi='Yonos Maxo 25/0.5-12',
         vvg_valve='VVG 549.20-4K',   exp_vol=200,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='352,54', brunata_s='322,03'),

    dict(num='i18L126', type='1H2W', he=200, dhw=150, day='10', month='юли',
         addr='ул.Ястребец №9, бл.2, Б',
         voi_hex='XB12L-1-60',        pump_voi='Yonos Maxo 25/0.5-12',
         vvg_valve='VVG 549.20-4K',   exp_vol=200,
         bgv_hex='XB12L-2-20/20',     pump_bgv='ZRS 15/16-130',
         scheme_idx=0,
         brunata_w='352,54', brunata_s='322,03'),
]

if __name__ == '__main__':
    out_dir = BASE  # PDF-ите се записват до скрипта
    for s in STATIONS:
        fname = f"Паспорт_{s['num']}_BAS_{s['type']}_{s['he']}_{s['dhw']}.pdf"
        out   = os.path.join(out_dir, fname)
        pages = build(s, out)
        print(f"✓ {fname}  ({pages} стр.)")
    print("Готово.")
