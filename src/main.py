from asyncio import sleep

from depends import get_bitrix_service, get_fedresurs_service
import asyncio
from config import SessionManager
from datetime import datetime, timezone, timedelta


async def main(count):
    print(f"Количество клиентов: ", count)
    session = await SessionManager.get_session()

    try:
        f_service = get_fedresurs_service(session)
        b_service = get_bitrix_service(session)

        clients = await b_service.send_request(
            "crm.contact.list",
            json={
                "select": [
                    "ID",
                    "NAME",
                    "SECOND_NAME",
                    "LAST_NAME",
                    "UF_CRM_FEDRESURS_MONITORING",
                    "UF_CRM_FEDRESURS_CHECKUP_DATETIME",
                    "UF_CRM_FEDRESURS_IP",# Номер дела о банкротстве c Федресурса
                    "UF_CRM_FEDRESURS_INFO", # "Количество сообщений о банкротстве с Федресурса"
                    "BIRTHDATE",
                ],
                "filter": {
                    "ID": "18609",
                    "UF_CRM_FEDRESURS_MONITORING": "1",
                    "!=NAME": "",
                    "!=SECOND_NAME": "",
                    "!=LAST_NAME": "",
                    "!=BIRTHDATE": ""
                },
                "order": {
                    "UF_CRM_FEDRESURS_CHECKUP_DATETIME": "ASC", # "ASC", "DESC"
                    "BIRTHDATE": "DESC"
                },
                "start": 0
            }
        )

        for client in clients["result"][:count]:
            print(client)
            if client["BIRTHDATE"] == "":
                print(f"У контакта {client['ID']} не заполнена дата рождения")
                continue
            else:
                birthdate = datetime.fromisoformat(client["BIRTHDATE"]).date()

            f_persons = await f_service.search_person(
                client["LAST_NAME"],
                client["NAME"],
                client["SECOND_NAME"],
            )
            # print(f_persons)
            for f_person in f_persons:

                f_person_info = await f_service.get_person(f_person["id"])
                # print(f_person_info)

                dob = datetime.strptime(f_person_info["dob"], "%d.%m.%Y").date()

                if dob == birthdate:

                    case_num = ""
                    messages = await f_service.get_messages(f_person["id"])
                    for message in messages:

                        message_info = await f_service.get_message(message["id"])
                        case_num = message_info["case_num"]
                        print(case_num)

                        if "lots" in message_info:
                            for lot in message_info["lots"]:
                                lot["message_id"] = message["id"]


                    tz = timezone(timedelta(hours=3))
                    now = datetime.now(tz)

                    contact = await b_service.send_request(
                        "crm.contact.update",
                        json={
                            "id": client["ID"],
                            "fields": {
                                "UF_CRM_FEDRESURS_CHECKUP_DATETIME": now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat(), #
                                "UF_CRM_FEDRESURS_IP": case_num, # номер дела о банкротстве
                                "UF_CRM_FEDRESURS_INFO": len(messages), # количество сообщений
                            }
                        }
                    )
                    print(len(messages), case_num, now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat())
                    print(contact)


    finally:
        await SessionManager.close_session()

if __name__ == "__main__":
    count_clients = input("Количество обрабатываемых клиентов: ")

    if count_clients == "":
        count_clients = 1
        asyncio.run(
            main(count_clients)
        )
    elif int(count_clients) <= 50:
        asyncio.run(
            main(int(count_clients))
        )
    elif int(count_clients) > 50:
        print("более 50 обрабатываемых персон")

