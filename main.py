# https://docs.gspread.org/en/v5.7.1/
# https://www.youtube.com/watch?v=bu5wXjz2KvU&t=391s
# https://github.com/robin900/gspread-formatting

import time
import datetime
import logging
import gspread
from gspread.utils import rowcol_to_a1
from utils.db_script import get_bookings, Booking
from gspread_formatting import *

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


def row_cow_range_to_a1(
        first_row: int, first_col: int, last_row: int, last_col: int
) -> str:
    """

    :param first_row: (int) – First row number
    :param first_col: (int) – First column number
    :param last_row: (int) – Last row number
    :param last_col: (int) – Last column number
    :return:
    """
    print(f'{first_row=}')
    print(f'{first_col=}')
    print(f'{last_row=}')
    print(f'{last_col=}')
    result = rowcol_to_a1(first_row, first_col) + ':' + rowcol_to_a1(last_row, last_col)
    print(result)
    return result


def fill_the_rules(wks: gspread.Worksheet, start_row: int = 1) -> int:
    """
    :param start_row:
    :param wks:
    :return:
    """

    # Update the first cell
    wks.update('A' + str(start_row), 'Как записаться на корт')

    rules_list = [
        'Находим свободное время (разные листы под разные корты)',
        'Вписываем в ячейку через запятую: Имя, телефон (или ник telegram), кол-во игроков, далее через запятую можно добавить любой комментарий',
        'Далее выделяем ячейку соответствующим цветом',
        'Далее копируем информацию в остальые ячейки, соответствующие времени, на которое вы хотите записаться (или объединяем ячейки)',
        'Важно! В будние дни после 17:00 записываемся максимум на 1,5 часа в таблицу (если хотите играть дольше, то если корты после вашей записи будут свободны, то можете сколько хотите оставаться без записи, но запись в таблице только на 1,5 часа, чтобы другие тоже могли прийти)'
    ]
    rules_count = len(rules_list)

    # Update a range of cells using the top left corner address
    wks.update('A' + str(start_row + 1), [[i + 1, rules_list[i]] for i in range(rules_count)])

    # Format the header
    # wks.format('A' + str(start_row) + ':' + 'A' + str(start_row + 1), {'textFormat': {'bold': True}})

    return rules_count + 1


def get_bookings_and_courts(depth: int):
    bookings_court_1, bookings_court_2 = [], []
    for b in get_bookings(depth):
        if b.court_id == 1:
            bookings_court_1.append(b)
        elif b.court_id == 2:
            bookings_court_2.append(b)
    return (
        {'title': 'Корт №1', 'records': bookings_court_1},
        {'title': 'Корт №2', 'records': bookings_court_2}
    )


def create_the_schedule(court_dict: dict, wks: gspread.Worksheet, start_row: int = 1, depth: int = 14) -> int:
    weekdays = {
        1: 'ПН',
        2: 'ВТ',
        3: 'СР',
        4: 'ЧТ',
        5: 'ПТ',
        6: 'СБ',
        0: 'ВС',
    }
    start_datetime = datetime.datetime(1900, 1, 1, 7, 0, 0)
    time_list = [start_datetime.strftime('%H:%M'), ]
    while start_datetime.time() < datetime.time(23, 0, 0):
        start_datetime += datetime.timedelta(minutes=15)
        time_list.append(start_datetime.strftime('%H:%M'))

    wks.update('A' + str(start_row), court_dict['title'])
    wks.format('A' + str(start_row), {'textFormat': {'bold': True}})
    wks.update('A' + str(start_row + 1), [['Дата', 'День недели', *[str(i) for i in time_list]], ])

    currant_date = datetime.datetime.now()
    dates = [currant_date + datetime.timedelta(days=i) for i in range(depth)]
    wks.update('A' + str(start_row + 2), [[str(i.date()), weekdays[i.weekday()]] for i in dates])

    for record in court_dict['records']:
        record_the_draw(wks, record, start_row)

    # https://docs.gspread.org/en/v5.7.2/api/models/worksheet.html#gspread.worksheet.Worksheet.merge_cells
    # wks.update('D'+str(start_row + 3), 'Пример какой-то записи')
    # wks.format('D'+str(start_row + 3), {
    #     "backgroundColor": {
    #         "red": 120.0,
    #         "green": 15.0,
    #         "blue": 12.0
    #     },
    # })
    # wks.merge_cells('D' + str(start_row + 3) + ':' + 'K' + str(start_row + 3))
    return start_row + depth + 1


def record_the_draw(wks: gspread.Worksheet, booking: Booking, start_row: int = 1):
    time.sleep(4)
    today = (datetime.datetime.utcnow() + datetime.timedelta(hours=3))
    row_num = start_row + 2 + (booking.start_time.date() - today.date()).days
    start_col_num = int(((booking.start_time.hour * 60 + booking.start_time.minute) - 7 * 60) / 15 + 3)
    unite_cells_count = int(round((booking.end_time - booking.start_time).seconds / 60 / 15, 0)) - 1
    end_col_number = start_col_num + unite_cells_count

    user = booking.user

    name = f'{user.first_name.capitalize()} {user.last_name.capitalize()}' if (
                user.first_name and user.last_name) else 'Анонимный пользователь'
    link = f'https://t.me/{user.user_name[1:]}' if user.user_name else 'ссылка на профиль ТГ отсутствует'
    ntrp = user.ntrp if user.ntrp else 'данные об ntrp отсутствуют'
    record_type = booking.type
    additional_member = booking.additional_member

    start_datetine_str = booking.start_time.strftime('%H:%M')
    duration = (booking.end_time - booking.start_time)
    wks.update_cell(row_num, start_col_num,
                    value=f'=HYPERLINK("{link}"; "{name} (Время брони: {start_datetine_str}, продолжительность: {duration}")'
                    )

    a1_cell = rowcol_to_a1(row_num, start_col_num)
    wks.update_note(cell=a1_cell,
                    content=f'Тип записи: {record_type},\n'
                            f'NTRP: {ntrp},\n'
                            f'Дополнительно заявленные участники: {additional_member}'
                    )

    a1_range = row_cow_range_to_a1(row_num, start_col_num, row_num, end_col_number)

    try:
        wks.merge_cells(a1_range)
    except Exception as ex:
        logger.error(ex, booking)

    wks.format(a1_range, {
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
        }
    })


def main() -> None:
    # Глубина в днях
    days_depth = 14

    # Получаем список кортов и записей
    bookings_list = get_bookings_and_courts(depth=days_depth)

    gc = gspread.service_account(filename='service_account.json')
    ss = gc.open('TennisCourtsSchedule')
    logger.info(f'Подключено к гугл-таблице по адресу {ss.url}')

    try:
        wsh = ss.add_worksheet(title='Бронирование кортов', rows=100, cols=5, index=None)
    except:
        wsh = ss.get_worksheet(0)

    last_filled_row_number = fill_the_rules(wsh)
    # last_filled_row_number = 0

    for court in bookings_list:
        last_filled_row_number = create_the_schedule(court, wsh, last_filled_row_number + 2, days_depth)

    # https://developers.google.com/sheets/api/guides/concepts  # a1_notation
    # for booking in bookings_list:
    #     print(booking['title'])
    #     print(len(booking['records']))
    #     for row in booking['records']:
    #         record_the_draw(row)


if __name__ == '__main__':
    start_time = time.time()
    main()
    logger.info(f"Execution time: {time.time() - start_time:.2f} seconds")
