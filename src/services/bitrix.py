from aiohttp import ClientSession
from typing import Literal, Optional
from datetime import datetime, timezone, timedelta

from config import settings


class BitrixService:

    def __init__(self, http_session: ClientSession):
        self.http_session = http_session

    async def _request(self, method, url, params, json):
        return await self.http_session.request(
            method=method,
            url=url,
            params=params,
            json=json,
        )

    async def send_request(
        self,
        endpoint: str,
        method: Literal['get', 'post'] = 'post',
        params: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> dict:
        url = f"{settings.bitrix.webhook_url}/{endpoint}.json"

        response = await self._request(
            method=method,
            url=url,
            params=params,
            json=json
        )

        return await response.json()

class BitrixLotService(BitrixService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_type_id = settings.bitrix.id_sp_lot

    async def create_message(self, client_id: int, lot: dict):
        response = await self.send_request(
            "crm.item.add",
            json={
                "entityTypeId": self.entity_type_id,
                "fields": {
                    "title": f"{lot.get('num')} {lot.get('type')}",
                    "contactId": client_id,
                    "ufCrm148_1758037968": lot.get("description"),
                    "ufCrm148_1758037977": lot.get("type"),
                    "ufCrm148_1758037984": lot.get("start_price"),
                    "ufCrm148_1758037994": lot.get("step"),
                    "ufCrm148_1758038013": lot.get("deposit"),
                }
            }
        )
        return response["result"]


class BitrixMessageService(BitrixService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_type_id = settings.bitrix.id_sp_message


    async def create_message(self, client_id: int, message: dict):
        response = await self.send_request(
            "crm.item.add",
            json={
                "entityTypeId": self.entity_type_id,
                "fields": {
                    "title": f"{message.get('num')} {message.get('type')}",
                    "contactId": client_id,
                    "ufCrm138_1744310823": message.get("type"), # тип сообщения
                    "ufCrm138_1744310803": message.get("date_published"), # дата
                    "ufCrm138_1744310779": message.get("num"), # номер
                    "ufCrm138_1744310786": f"https://fedresurs.ru/bankruptmessages/{message.get("id")}", # url a412e48d-5b84-4bf9-8bde-6236093ad886
                    "ufCrm138_1744310814": message.get("text")# текст сообщения
                }
            }
        )
        return response["result"]

    async def get_message(self, message_id: int):
        print(self.entity_type_id)
        response = await self.send_request(
            "crm.item.get",
            json={
                "entityTypeId": self.entity_type_id,
                "id": message_id,
                "useOriginalUfNames": "Y"
            }
        )
        return response

class BitrixContactsService(BitrixService):

    async def get_fields(self):
        response = await self.send_request(
            "crm.item.fields",
            json={
                "entityTypeId": 3
            }
        )
        return response

    async def update_contact(self, client_id: int, num_activity: str, count_messages: int, ):

        tz = timezone(timedelta(hours=3))
        now = datetime.now(tz)

        response = await self.send_request(
            "crm.contact.update",
            json={
                "id": client_id,
                "fields": {
                    "UF_CRM_FEDRESURS_CHECKUP_DATETIME": now.replace(hour=0, minute=0, second=0,
                                                                     microsecond=0).isoformat(),  #
                    "UF_CRM_FEDRESURS_IP": num_activity,  # номер дела о банкротстве
                    "UF_CRM_FEDRESURS_INFO": count_messages,  # количество сообщений
                }
            }
        )
        return response

    async def get_contacts(self, start: Optional[int] = 0):
        response = await self.send_request(
            "crm.contact.list",
            json={
                "select": [
                    "ID",
                    "NAME",
                    "SECOND_NAME",
                    "LAST_NAME",
                    "UF_CRM_1636582822241", # INN
                    "UF_CRM_FEDRESURS_MONITORING",
                    "UF_CRM_FEDRESURS_CHECKUP_DATETIME",
                    "UF_CRM_FEDRESURS_IP",  # Номер дела о банкротстве c Федресурса
                    "UF_CRM_FEDRESURS_INFO",  # "Количество сообщений о банкротстве с Федресурса"
                    "BIRTHDATE",
                ],
                "filter": {
                    "ID": "18609",
                    "UF_CRM_FEDRESURS_MONITORING": "1", # мониторинг в федресурсе
                    "!=NAME": "",               # только с заполненными колями
                    "!=SECOND_NAME": "",        # только с заполненными колями
                    "!=LAST_NAME": "",          # только с заполненными колями
                    "!=BIRTHDATE": ""           # только с заполненными колями
                },
                "order": {
                    "UF_CRM_FEDRESURS_CHECKUP_DATETIME": "ASC",  # "ASC", "DESC"
                    "BIRTHDATE": "DESC"
                },
                "start": start
            }
        )
        return response["result"]

