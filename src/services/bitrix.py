from aiohttp import ClientSession
from typing import Literal, Optional
from datetime import datetime, timezone, timedelta

from config import settings
from constants import BitrixLotConstants, BitrixMessageConstants, BitrixContactConstants
from config import SessionManager


class BitrixService:

    def __init__(
            self,
            http_session: ClientSession = SessionManager.get_session(),
    ):
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
        self.fields = BitrixLotConstants()

    async def create_lot(self, client_id: int, lot: dict):
        response = await self.send_request(
            "crm.item.add",
            json={
                "entityTypeId": self.entity_type_id,
                "fields": {
                    "title": f"{lot.get('num')} {lot.get('type')}",
                    "contactId": client_id,

                    self.fields.description: lot.get("description"),
                    self.fields.type_lot: lot.get("type"),
                    self.fields.start_price: lot.get("start_price"),
                    self.fields.step: lot.get("step"),
                    self.fields.deposit: lot.get("deposit"),

                }
            }
        )
        return response["result"]


class BitrixMessageService(BitrixService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_type_id = settings.bitrix.id_sp_message
        self.fields = BitrixMessageConstants()


    async def create_message(self, client_id: int, message: dict):
        response = await self.send_request(
            "crm.item.add",
            json={
                "entityTypeId": self.entity_type_id,
                "fields": {
                    "id": message.get("id"), # надо проверить будет ли создаваться сообщение с таким id
                    "title": f"{message.get('num')} {message.get('type')}",
                    "contactId": client_id,
                    self.fields.type_message: message.get("type"),
                    self.fields.date_published: message.get("date_published"),
                    self.fields.num: message.get("num"),
                    self.fields.url: f"https://fedresurs.ru/bankruptmessages/{message.get("id")}",
                    self.fields.text: message.get("text"),
                    self.fields.cache: message

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = BitrixContactConstants()

    async def get_fields(self):
        response = await self.send_request(
            "crm.item.fields",
            json={
                "entityTypeId": 3
            }
        )
        return response

    async def contact_not_found(self, client_id: int, ):
        """Отмечаем что не найден на федресурсе"""
        response = await self.send_request(
            "crm.contact.update",
            json={
                "id": client_id,
                "fields": {
                    self.fields.fedresurs_found: self.fields.fedresurs_found_status_no
                }
            }
        )
        return response

    async def contact_found(
            self,
            client_id: int,
            num_activity: str,
            count_messages: int,
            info_person: dict,
            search_info: dict,
            search_messages: dict
    ):
        """Когда нашли на федресурсе отмечаем как найденый"""
        tz = timezone(timedelta(hours=3))
        now = datetime.now(tz)

        response = await self.send_request(
            "crm.contact.update",
            json={
                "id": client_id,
                "fields": {
                    self.fields.fedresurs_found: self.fields.fedresurs_found_status_yes,
                    self.fields.date_updated_fedresurs: now.replace(hour=0, minute=0, second=0,
                                                                     microsecond=0).isoformat(),
                    self.fields.bankruptcy_case_number: num_activity,
                    self.fields.count_messages: count_messages,
                    self.fields.info_fedresurs: info_person,

                    self.fields.find_fedresurs: search_info,
                    self.fields.messages_fedresurs: search_messages

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
                    self.fields.inn,
                    self.fields.fedresurs_monitoring,
                    self.fields.date_updated_fedresurs,
                    self.fields.bankruptcy_case_number,
                    self.fields.count_messages,
                    self.fields.info_fedresurs,
                    self.fields.fedresurs_found,
                    self.fields.find_fedresurs,
                    self.fields.messages_fedresurs,
                    "BIRTHDATE",
                ],
                "filter": {
                    "ID": "18609",
                    self.fields.fedresurs_monitoring: "1", # мониторинг в федресурсе
                    # f"={self.fields.fedresurs_found}": "", # Только необработанные ранее
                    "!=NAME": "",               # только с заполненными колями
                    "!=SECOND_NAME": "",        # только с заполненными колями
                    "!=LAST_NAME": "",          # только с заполненными колями
                    "!=BIRTHDATE": ""           # только с заполненными колями
                },
                "order": {
                    self.fields.date_updated_fedresurs: "ASC",  # "ASC", "DESC"
                    "BIRTHDATE": "DESC"
                },
                "start": start
            }
        )
        try:
            return response["result"]
        except KeyError:
            print(f"error response: {response}")
            raise
