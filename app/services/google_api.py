from datetime import datetime

from aiogoogle import Aiogoogle

from app.constants import (
    FORMAT,
    SPREADSHEET_WORKPIECE,
    TABLE_VALUES,
    RANGE_SHEET,
)
from app.core.config import settings
from app.utils import get_spreadsheet_json
from app.api.validators import check_google_sheet_capacity


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = get_spreadsheet_json(SPREADSHEET_WORKPIECE)
    spreadsheet_body['properties']['title'] = spreadsheet_body['properties'][
        'title'
    ].format(now_date_time=now_date_time)

    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheetid = response['spreadsheetId']
    return spreadsheetid


async def set_user_permissions(
    spreadsheetid: str, wrapper_services: Aiogoogle
) -> None:
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email,
    }
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields="id",
        )
    )


async def spreadsheets_update_value(
    spreadsheetid: str, projects: list, wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = get_spreadsheet_json(TABLE_VALUES)
    table_values[0][1] = table_values[0][1].format(now_date_time=now_date_time)
    for project in projects:
        new_row = [
            project['name'],
            str(project['donation_timedelta']),
            project['description'],
        ]
        table_values.append(new_row)

    need_rows = len(table_values)
    need_column = max(len(col) for col in table_values)
    spreadsheet = await get_spreadsheet(
        spreadsheetid, service, wrapper_services
    )
    await check_google_sheet_capacity(spreadsheet, need_rows, need_column)

    update_body = {'majorDimension': 'ROWS', 'values': table_values}
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range=RANGE_SHEET,
            valueInputOption='USER_ENTERED',
            json=update_body,
        )
    )


async def get_spreadsheet(
    spreadsheetid: str, service: Aiogoogle, wrapper_services: Aiogoogle
):
    spreadsheet = await wrapper_services.as_service_account(
        service.spreadsheets.get(spreadsheetId=spreadsheetid)
    )
    return spreadsheet
