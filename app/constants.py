DEF_INVEST_AMOUNT = 0
MAX_LEN_NAME = 100
MIN_LEN = 1
GT_VALUE = 0
FORMAT = "%Y/%m/%d %H:%M:%S"
ROW_COUNT = 100
COLUMN_COUNT = 11
SPREADSHEET_WORKPIECE = {
    'properties': {
        'title': 'Отчёт от {now_date_time}',
        'locale': 'ru_RU',
    },
    'sheets': [
        {
            'properties': {
                'sheetType': 'GRID',
                'sheetId': 0,
                'title': 'Лист1',
                'gridProperties': {'rowCount': ROW_COUNT, 'columnCount': COLUMN_COUNT},
            }
        }
    ],
}
TABLE_VALUES = [
    ['Отчёт от', '{now_date_time}'],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание'],
]
RANGE_SHEET = r'A1:E30'
