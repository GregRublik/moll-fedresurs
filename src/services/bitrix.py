from aiohttp import ClientSession
from typing import Literal, Optional

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
