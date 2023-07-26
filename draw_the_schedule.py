# https://docs.gspread.org/en/v5.7.1/
# https://www.youtube.com/watch?v=bu5wXjz2KvU&t=391s
# https://github.com/robin900/gspread-formatting

import time
import datetime
import logging
import gspread
from gspread.utils import rowcol_to_a1
from gspread.exceptions import APIError
from utils.db_script import get_bookings, Booking
from gspread_formatting import *

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


def row_cow_range_to_a1(first_row: int, first_col: int, last_row: int, last_col: int) -> str:
    """

    :param first_row: (int) – First row number
    :param first_col: (int) – First column number
    :param last_row: (int) – Last row number
    :param last_col: (int) – Last column number
    :return:
    """
    result = rowcol_to_a1(first_row, first_col) + ':' + rowcol_to_a1(last_row, last_col)
    return result


def add_cell_value_to_array(row, col, value, array_to_patch: list = None) -> list:
    try:
        if array_to_patch is None:
            array_to_patch = []
        array_to_patch.append(
            {'range': rowcol_to_a1(row, col),
             'values': [[value], ]
             })
    except Exception as err:
        pass
    return array_to_patch


def fill_the_rules(wks: gspread.Worksheet, dtime: datetime.datetime = None, start_row: int = 1) -> int:
    dtime_str = dtime.strftime('%H:%M %d.%m.%Y')
    arr = add_cell_value_to_array(1, 1, 'Таблица записей на теннисные корты Овсянниковского сада')

    rules_list = [
        f'Данные, указанные в таблице, актуальны на {dtime_str}',
        'Данная таблица сформирована автоматически для удобства визуального восприятия, '
        'запись на корты осуществляется только по средствам ТГ бота',
        '=HYPERLINK("https://t.me/ovsyannykovsky_open_tennis"; "Ссылка на группу в Телеграме")',
        '=HYPERLINK("https://t.me/tennis_rentbot"; "Ссылка на бот для внесения записи")'
    ]
    for i, rule in enumerate(rules_list):
        arr = add_cell_value_to_array(i + 2, 2, rule, arr)
    # # Format the header
    wks.format('A' + str(start_row), {'textFormat': {'bold': True}})

    wks.batch_update(arr, value_input_option='user_entered')
    return len(rules_list) + 1


def get_bookings_and_courts(depth: int):
    bookings_court_1, bookings_court_2 = [], []
    bookings = get_bookings(depth)
    bookings.sort(key=lambda booking: (booking.court_id, booking.start_time, booking.created_at))

    for b in bookings:
        if b.court_id == 1:
            bookings_court_1.append(b)
        elif b.court_id == 2:
            bookings_court_2.append(b)

    booking_conflicts = []

    for i in range(len(bookings_court_1) - 1, 0, -1):
        if bookings_court_1[i].start_time <= bookings_court_1[i - 1].end_time:
            # можно сделать похитрее, но и так сойдет пока
            booking_conflicts.append((bookings_court_1[i], bookings_court_1[i - 1]))
            bookings_court_1.pop(i)

    for i in range(len(bookings_court_2) - 1, 0, -1):
        if bookings_court_2[i].start_time <= bookings_court_2[i - 1].end_time:
            # можно сделать похитрее, но и так сойдет пока
            booking_conflicts.append((bookings_court_2[i], bookings_court_2[i - 1]))
            bookings_court_2.pop(i)

    for booking_1, booking_2 in booking_conflicts:
        logger.error(f'Найден следующий конфликт записей {booking_1.id=}, {booking_1.start_time=}, '
                     f'{booking_1.end_time=}, {booking_2.id=}, {booking_2.start_time=}, {booking_2.end_time=}')

    return (
        {'title': 'Корт №1', 'records': bookings_court_1},
        {'title': 'Корт №2', 'records': bookings_court_2}
    )


def create_the_schedule(court_dict: dict, wks: gspread.Worksheet, start_row: int = 1, depth: int = 14) -> int:
    weekdays = {
        0: 'ПН',
        1: 'ВТ',
        2: 'СР',
        3: 'ЧТ',
        4: 'ПТ',
        5: 'СБ',
        6: 'ВС',
    }
    start_datetime = datetime.datetime(1900, 1, 1, 7, 0, 0)
    time_list = [start_datetime.strftime('%H:%M'), ]
    while start_datetime.time() < datetime.time(23, 0, 0):
        start_datetime += datetime.timedelta(minutes=15)
        time_list.append(start_datetime.strftime('%H:%M'))

    arr = add_cell_value_to_array(start_row, 1, court_dict['title'])
    wks.format('A' + str(start_row), {'textFormat': {'bold': True}})
    wks.update('A' + str(start_row + 1), [['Дата', 'День недели', *[str(i) for i in time_list]], ])
    a1_range_time_list = row_cow_range_to_a1(start_row + 1, 1 + 2, start_row + 1, len(time_list) + 2)
    # https://habr.com/ru/articles/305378/ - ширина столбцов
    wks.format(a1_range_time_list, {'textFormat': {'fontSize': 8,
                                                   'foregroundColor': {
                                                       "red": 38.0,
                                                       "green": 240.0,
                                                       "blue": 38.0
                                                   }},
                                    'textRotation': {'angle': 90}
                                    }
               )

    currant_date = datetime.datetime.now()
    dates = [currant_date + datetime.timedelta(days=i) for i in range(depth)]
    wks.update('A' + str(start_row + 2), [[str(i.strftime('%d.%m.%Y')), weekdays[i.weekday()]] for i in dates],
               value_input_option='USER_ENTERED')

    records = []
    for record in court_dict['records']:
        cell_row, cell_col, cell_value, cells_count_to_merge, cell_note = record_the_draw(record, start_row)
        records.append({
            'cell_row': cell_row,
            'cell_col': cell_col,
            'cell_value': cell_value,
            'cells_count_to_merge': cells_count_to_merge,
            'cell_note': cell_note}
        )
        # arr = add_cell_value_to_array(cell_row, cell_col, cell_value, arr)

    notes_dict = {}
    formats_list = []
    merge_requests = []
    sheet_id = wks._properties['sheetId']
    for record in records:
        arr = add_cell_value_to_array(record['cell_row'], record['cell_col'], record['cell_value'], arr)
        a1_range = rowcol_to_a1(record['cell_row'], record['cell_col'])
        notes_dict.update({a1_range: record['cell_note']})
        formats_list.append({
            'range': a1_range,
            'format': {
                "backgroundColor": {
                    "red": 5.0,
                    "green": 15.0,
                    "blue": 100.0
                },
                'borders': {
                    "top": {'style': 'SOLID_MEDIUM'},
                    "right": {'style': 'SOLID_MEDIUM'},
                    "bottom": {'style': 'SOLID_MEDIUM'},
                    "left": {'style': 'SOLID_MEDIUM'}
                }}
        })

        merge_requests.append({
            "mergeCells": {
                "mergeType": "MERGE_ALL",
                "range": {  # In this sample script, all cells of "A1:C3" of "Sheet1" are merged.
                    "sheetId": sheet_id,
                    "startRowIndex": record['cell_row'] - 1,
                    "endRowIndex": record['cell_row'],
                    "startColumnIndex": record['cell_col'] - 1,
                    "endColumnIndex": record['cell_col'] + record['cells_count_to_merge']
                }
            }
        })

    wks.batch_update(arr, value_input_option='user_entered')
    wks.update_notes(notes_dict)
    wks.batch_format(formats_list)

    # https://stackoverflow.com/questions/57166738/gspread-cell-merging
    try:
        wks.spreadsheet.batch_update({"requests": merge_requests})
    except APIError as err:
        logger.error('error', err)

    return start_row + depth + 1


def record_the_draw(booking: Booking, start_row: int = 1):
    today = (datetime.datetime.utcnow() + datetime.timedelta(hours=3))
    row_num = start_row + 2 + (booking.start_time.date() - today.date()).days
    start_col_num = int(((booking.start_time.hour * 60 + booking.start_time.minute) - 7 * 60) / 15 + 3)
    user = booking.user
    name = f'{user.first_name.capitalize()} {user.last_name.capitalize()}' if (
            user.first_name and user.last_name) else 'Анонимный пользователь'
    if user.user_name:
        if user.user_name.startswith('@'):
            link = f'https://t.me/{user.user_name[1:]}' if user.user_name else 'ссылка на профиль ТГ отсутствует'
            cell_value = f'=HYPERLINK("{link}"; "{name}")'
    else:
        cell_value = name
    ntrp = user.ntrp if user.ntrp else 'данные об ntrp отсутствуют'
    record_type = booking.type
    additional_member = booking.additional_member
    start_datetime_str = booking.start_time.strftime('%H:%M')
    duration = (booking.end_time - booking.start_time)

    cell_row = row_num
    cell_col = start_col_num
    cells_count_to_merge = int(round((booking.end_time - booking.start_time).seconds / 60 / 15, 0)) - 1
    cell_note = f'Тип записи: {record_type},\n' \
                f'NTRP: {ntrp},\n' \
                f'Дополнительно заявленные участники: {additional_member} \n' \
                f'(Время брони: {start_datetime_str}, продолжительность: {duration})'

    return cell_row, cell_col, cell_value, cells_count_to_merge, cell_note


def main() -> None:
    # Глубина в днях
    days_depth = 14

    basic_rows_count, basic_columns_count = 100, 5

    # Получаем список кортов и записей
    bookings_list = get_bookings_and_courts(depth=days_depth)

    # Получаем актуальную дату и время
    actual_datetime = datetime.datetime.utcnow() + datetime.timedelta(hours=3)

    # Подключаемся к листу 'Бронирование кортов'
    gc = gspread.service_account(filename='service_account.json')
    ss = gc.open('TennisCourtsSchedule')
    logger.info(f'Подключено к гугл-таблице по адресу {ss.url}')
    wsh_title = 'Бронирование кортов'
    try:
        wsh = ss.add_worksheet(title=wsh_title, rows=basic_rows_count, cols=basic_columns_count)
    except APIError as err:
        logger.info(f'Не удалось создать лист {wsh_title} {err}')
        wsh = ss.worksheet(wsh_title)
        wsh.resize(rows=3)
        wsh.resize(rows=basic_rows_count)

    sheets = ss.worksheets()
    for i in range(len(sheets) - 1, 0, -1):
        ws = sheets[i]
        if ws.title != wsh_title:
            ss.del_worksheet(ws)

    wsh.clear()
    wsh.unmerge_cells(wsh.row_count, wsh.col_count)

    # https://stackoverflow.com/questions/9574793/how-to-convert-a-python-datetime-datetime-to-excel-serial-date-number

    last_filled_row_number = fill_the_rules(wsh, actual_datetime)
    for court in bookings_list:
        last_filled_row_number = create_the_schedule(court, wsh, last_filled_row_number + 2, days_depth)
        court_title = court['title']
        valid_bookings_count = len(court['records'])
        logger.info(f'Записи корта "{court_title}" отрисованы. Получено валидных записей - {valid_bookings_count} ')

    data = [
        'Данное табличное представление создано Никитой М.',
        'По всем вопросам, пожеланиям, предложениям, найденным ошибкам просим обращаться к автору по ссылке ниже',
        '=HYPERLINK("https://t.me/@MaN1Le"; "Ссылка на Телеграм")'
    ]
    wsh.update('A' + str(last_filled_row_number + 2), [[d] for d in data], value_input_option='user_entered')


if __name__ == '__main__':
    start_time = time.time()
    main()
    logger.info(f"Execution time: {time.time() - start_time:.2f} seconds")
