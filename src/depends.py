from services import bitrix, fedresurs
from aiohttp import ClientSession
from config import settings, SessionManager
from services.matching import MatchingService


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

def get_bitrix_contact_service(
    http_session: ClientSession
) -> bitrix.BitrixContactsService:
    return bitrix.BitrixContactsService(
        http_session
    )

def get_message_service(
        http_session: ClientSession
) -> bitrix.BitrixMessageService:
    return bitrix.BitrixMessageService(
        http_session
    )

def get_matching_service() -> MatchingService:
    return MatchingService()
