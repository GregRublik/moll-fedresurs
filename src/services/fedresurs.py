from aiohttp import ClientSession
from config import settings
from asyncio import sleep


class FedresursService:

    def __init__(self, api_url, http_session: ClientSession):
        self.api_url = api_url
        self.api_key = settings.fedresurs.api_key
        self.http_session = http_session

    async def _api_get(self, endpoint, params):
        await sleep(1)
        print(f"Делаем запрос к сервису {endpoint}")

        url = f"{self.api_url}/{endpoint}"

        retries = 5

        for attempt in range(retries):
            response = await self.http_session.get(url, params=params)

            if response.status == 200:
                data = await response.json()

                if data.get("success") == 1:
                    return data

                if "error" in data:
                    error_msg = data["error"]

                    # 🔥 ключевая логика
                    if "temporarily unavailable" in error_msg:
                        print(f"Сервис временно недоступен, попытка {attempt + 1} , {url}, {params}")
                        await sleep(2)
                        continue

                    raise Exception(f"status code: {response.status}, {error_msg}")

            else:
                print(f"HTTP ошибка {response.status}, попытка {attempt + 1}, {url}, {params}")
                await sleep(2)

        raise Exception("Fedresurs API не отвечает после нескольких попыток")

    async def search_person(
            self,
            last,
            first,
            patronymic

    ):
        """Поиск персоны"""
        params = {
            "key": self.api_key,
            "lastName": last,
            "firstName": first,
            "patronymic": patronymic
        }

        data = await self._api_get("search_fiz", params)

        return data.get("records", [])

    async def get_person(self, person_id):
        """Получить персону"""
        params = {
            "key": self.api_key,
            "id": person_id
        }

        data = await self._api_get("get_person", params)

        return data["record"]

    async def get_messages(self, person_id, start: int = 0):
        """Получить несколько сообщений о персоне"""

        params = {
            "key": self.api_key,
            "id": person_id,
            "from_record": start
        }

        data = await self._api_get("get_person_messages", params)

        return data.get("records", [])

    async def get_message(self, msg_id):
        """Получить 1 сообщение о персоне"""
        params = {
            "key": self.api_key,
            "id": msg_id
        }

        data = await self._api_get("get_message", params)

        return data["record"]
