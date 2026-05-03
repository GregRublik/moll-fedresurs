from services.bitrix import BitrixMessageService, BitrixLotService, BitrixContactsService, BitrixService
from services.fedresurs import FedresursService
from services.matching import MatchingService
from aiohttp import ClientSession
import ast

class Stats:
    def __init__(self):
        self.created_messages = []
        self.created_lots = []
        self.updated_contacts = []
        self.processed_clients = []

class Orchestrator:

    def __init__(
            self,
            session: ClientSession,
            # contact_service: BitrixContactsService ,
            # matching_service: MatchingService ,
            # fedresurs_service: FedresursService ,
            # lot_service: BitrixLotService ,
            # message_service: BitrixMessageService ,
    ):
        self.contact_service = BitrixContactsService(session)
        self.matching_service = MatchingService()
        self.fedresurs_service = FedresursService(session)
        self.lot_service = BitrixLotService(session)
        self.message_service = BitrixMessageService(session)

    async def process_clients(self, count: int):
        """Процесс поиска информации о клиентах на федресурсе"""
        clients = await self.contact_service.get_contacts()

        for client in clients[:count]:
            await self.process_single_client(client)

    async def process_single_client(self, client):
        cashed, persons = await self.get_persons_for_client(client) # получаем ЗАКЭШИРОВАН ЛИ ОН И ДАННЫЕ КЭША, ЛИБО search_person

        if cashed:
            person_info = self.str_to_dict(client[self.contact_service.fields.info_fedresurs]) # берем данные из кэша
            await self.handle_matched_person(client, person_info, cashed)
            return

        else:
            for person in persons:
                if self.matching_service.is_same_person(client, person):
                    person_info = await self.fedresurs_service.get_person(person["id"]) # ищем новые данные
                    person_info["id"] = person["id"] # добавляем так как в get_person по id он не возвращается
                    await self.handle_matched_person(client, person_info)
                    return

            await self.contact_service.contact_not_found(client["ID"]) # отмечаем что контакт не найден на fedresurs

    async def handle_matched_person(self, client, person, cached: bool = False):
        if cached:
            messages = self.str_to_dict(client[self.contact_service.fields.messages_fedresurs])
        else:
            messages = await self.fedresurs_service.get_messages(person["id"])

        case_num = "" # номер дела о банкротстве (по умолчанию нет)
        for message in messages:
            case_num = await self.process_message(client, person, message, cached) # в некоторых сообщениях он есть, по этому мы берем его из них

        await self.contact_service.contact_found(client["ID"], case_num, len(messages), person) # отмечаем что нашли на fedresurs и заполнили карточки сообщений и лотов

    async def process_message(self, client, person, message, cashed: bool = False) -> str:

        if cashed:
            message_bitrix = await self.message_service.get_message(message["id"]) # берем из битрикса
            message_info = self.str_to_dict(message_bitrix[self.message_service.fields.cache])
        else:
            message_info = await self.fedresurs_service.get_message(message["id"]) # берем из федресурса
            b_message = await self.message_service.create_message(client["ID"], message_info)

        case_num = ""

        for lot in message_info.get("lots", []):
            if message_info["case_num"] != "":
                case_num = message_info["case_num"]
            await self.lot_service.create_lot(client["ID"], lot)

        return case_num


    def is_cache_valid(self, client):
        """Проверка валидности кэша"""
        if not client[self.contact_service.fields.find_fedresurs]:
            return False

        # # например кэш живёт 7 дней
        # return (now - cached_at).days < 7
        return True # TODO пока просто проверяем есть ли кэш, и если есть то используем

    async def get_persons_for_client(self, client):
        """Поиск персон на федрес по фио клиента"""

        if self.is_cache_valid(client):
            return True, [client[self.contact_service.fields.find_fedresurs]]

        return False, await self.fedresurs_service.search_person(
            client["LAST_NAME"],
            client["NAME"],
            client["SECOND_NAME"],
        )

    @staticmethod
    def str_to_dict(string) -> dict:
        return ast.literal_eval(string)