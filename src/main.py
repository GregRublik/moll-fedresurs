import asyncio



from config import SessionManager
from services.bitrix import BitrixService, BitrixContactsService, BitrixMessageService
from services.fedresurs import FedresursService

from depends import (
    get_bitrix_service,
    get_fedresurs_service,
    get_bitrix_contact_service,
    get_matching_service,
    get_message_service
)
from services.matching import MatchingService


async def main(count):
    print(f"Количество клиентов: ", count)
    session = await SessionManager.get_session()

    try:
        f_service: FedresursService = get_fedresurs_service(session)
        c_service: BitrixContactsService = get_bitrix_contact_service(session)
        b_service: BitrixService = get_bitrix_service(session)
        m_service: MatchingService = get_matching_service()
        message_service: BitrixMessageService = get_message_service(session)

        clients = await c_service.get_contacts() # получаем 50 первых контактов

        number_of_clients_processed = 0

        for client in clients[:count]:
            print(client)

            if number_of_clients_processed == count:
                break

            f_persons = await f_service.search_person(
                client["LAST_NAME"],
                client["NAME"],
                client["SECOND_NAME"],
            )
            # print(f_persons)
            for f_person in f_persons:
                f_person_info = await f_service.get_person(f_person["id"])
                # print(f_person_info)

                if m_service.is_same_person(client, f_person_info):

                    number_of_clients_processed += 1 # пользователь совпал, записываем как успешного чтобы выйти когда будет более нужного нам количества

                    case_num = ""
                    messages = await f_service.get_messages(f_person["id"])

                    for message in messages:

                        message_info = await f_service.get_message(message["id"])
                        # todo message_service.create()
                        case_num = message_info["case_num"]

                        if "lots" in message_info:
                            for lot in message_info["lots"]:
                                lot["message_id"] = message["id"]
                                # todo lot_service.create()


                    contact = await c_service.update_contact(client["ID"], case_num, len(messages))


    finally:
        await SessionManager.close_session()

if __name__ == "__main__":
    count_clients = input("Количество обрабатываемых клиентов: ")

    if count_clients == "":
        count_clients = 1
        asyncio.run(
            main(count_clients)
        )
    elif 1 > int(count_clients) > 50:
        print(f"Некорректное количество персон: {count_clients}")
    elif int(count_clients) <= 50:
        asyncio.run(
            main(int(count_clients))
        )

