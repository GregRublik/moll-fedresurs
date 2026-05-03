import asyncio



from config import SessionManager, settings
from services.bitrix import BitrixService, BitrixContactsService, BitrixMessageService, BitrixLotService
from services.fedresurs import FedresursService
from services.orchestrator import Orchestrator

from depends import (
    get_bitrix_service,
    get_fedresurs_service,
    get_bitrix_contact_service,
    get_matching_service,
    get_message_service,
    get_lot_service
)
from services.matching import MatchingService

created_messages, created_lots, updated_contact, processed_clients = [], [], [], []

async def main(count):
    print(f"Количество клиентов: ", count)
    session = await SessionManager.get_session()

    try:
        f_service: FedresursService = get_fedresurs_service(session)
        c_service: BitrixContactsService = get_bitrix_contact_service(session)
        b_service: BitrixService = get_bitrix_service(session)
        m_service: MatchingService = get_matching_service()
        message_service: BitrixMessageService = get_message_service(session)
        lot_service: BitrixLotService = get_lot_service(session)

        # mes = await message_service.get_message(2)
        # print(mes)

        clients = await c_service.get_contacts() # получаем 50 первых контактов

        number_of_clients_processed = 0


        for client in clients[:count]:
            processed_clients.append(client["ID"])
            print(client)

            if number_of_clients_processed == count:
                break

            if client[c_service.fields.fedresurs_found] == "Да":
                f_persons = [client[c_service.fields.info_fedresurs]] # если ранее делали по нему запрос, то берем из поля contact

            else:
                f_persons = await f_service.search_person(
                    client["LAST_NAME"],
                    client["NAME"],
                    client["SECOND_NAME"],
                )

            is_same_person = False
            # print(f_persons)

            for f_person in f_persons:
                f_person_info = await f_service.get_person(f_person["id"])
                print(f_person_info)

                if m_service.is_same_person(client, f_person_info):
                    is_same_person = True

                    number_of_clients_processed += 1 # пользователь совпал
                    case_num = ""
                    messages = await f_service.get_messages(f_person["id"])

                    for message in messages:

                        message_info = await f_service.get_message(message["id"])
                        # print(message_info)

                        b_message = await message_service.create_message(client["ID"], message_info)
                        print(f"NEW MESS: {settings.bitrix.url}/crm/type/{settings.bitrix.id_sp_message}/details/{b_message['item']['id']}/")
                        created_messages.append(b_message['item']['id'])

                        if "lots" in message_info:
                            for lot in message_info["lots"]:

                                b_lot = await lot_service.create_lot(client["ID"], lot)
                                print(f"NEW LOT: {settings.bitrix.url}/crm/type/{settings.bitrix.id_sp_lot}/details/{b_lot['item']['id']}/")
                                created_lots.append(b_lot['item']['id'])

                    # todo Отмечаем что контакт найден (проверить), нужно также добавить сохранение кэшированной инфы (проверить)
                    await c_service.contact_found(client["ID"], message_info["case_num"], len(messages), f_person_info)

                    updated_contact.append(client["ID"])
                break

            if not is_same_person:
                # todo Отмечаем контакт как не найденный (Надо проверить)
                await c_service.contact_not_found(client["ID"])



    finally:
        await SessionManager.close_session()

if __name__ == "__main__":
    count_clients = input("Количество обрабатываемых клиентов: ")

    if count_clients == "":
        count_clients = 1
        asyncio.run(
            main(count_clients)
        )
    elif 1 > int(count_clients) > 6:
        print(f"Некорректное количество персон: {count_clients}")
    elif int(count_clients) <= 6:
        asyncio.run(
            main(int(count_clients))
        )

    print(f"""
Обрабатываемые контакты: {processed_clients}\n Обновленные контакты: {updated_contact}\n 
Созданные сообщения: {created_messages}\n Созданные лоты: {created_lots}\n 
""")

