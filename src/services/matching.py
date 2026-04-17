from datetime import datetime

class MatchingService:

    @staticmethod
    def is_same_person(client: dict, f_person_info: dict) -> bool:
        """
        Проверяет, является ли человек из Fedresurs тем же, что и клиент в Bitrix.
        Приоритет:
        1. ИНН
        2. Дата рождения
        3. ФИО (как fallback)
        """

        # 1. Проверка по ИНН (если есть)
        client_inn = client.get("UF_CRM_1636582822241") # поле INN
        person_inn = f_person_info.get("inn")

        if client_inn and person_inn:
            return client_inn == person_inn

        # 2. Проверка по дате рождения
        client_birthdate = client.get("BIRTHDATE")
        person_dob = f_person_info.get("dob")

        if client_birthdate and person_dob:
            try:
                client_date = datetime.fromisoformat(client_birthdate).date()
                person_date = datetime.strptime(person_dob, "%d.%m.%Y").date()
                if client_date == person_date:
                    return True
            except Exception:
                pass

        return False
