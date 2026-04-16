from services import bitrix, fedresurs
from aiohttp import ClientSession
from config import settings, SessionManager

def get_bitrix_service(
    http_session: ClientSession
) -> bitrix.BitrixService:
    return bitrix.BitrixService(
        http_session
    )

def get_fedresurs_service(
    http_session: ClientSession
) -> fedresurs.FedresursService:
    return fedresurs.FedresursService(
        settings.fedresurs.api_url,
        http_session
    )