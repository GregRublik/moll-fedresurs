class BitrixLotConstants:
    description = "ufCrm148_1758037968"
    type_lot = "ufCrm148_1758037977"
    start_price = "ufCrm148_1758037984"
    step = "ufCrm148_1758037994"
    deposit = "ufCrm148_1758038013"

class BitrixMessageConstants:
    type_message = "ufCrm138_1744310823"
    date_published = "ufCrm138_1744310803"
    num = "ufCrm138_1744310779"
    url = "ufCrm138_1744310786"
    text = "ufCrm138_1744310814"
    id_fedresurs = "ufCrm145_1777874302"

    cache = "ufCrm145_1777789355" # сюда кладу кэш во время создания сообщения в битрикс

class BitrixContactConstants:
    date_updated_fedresurs = "UF_CRM_FEDRESURS_CHECKUP_DATETIME"    # дата обновления федресурс
    bankruptcy_case_number = "UF_CRM_FEDRESURS_IP"                  # Номер дела о банкротстве
    count_messages = "UF_CRM_FEDRESURS_INFO"                        # Количество сообщений
    inn = "UF_CRM_1636582822241"
    fedresurs_monitoring = "UF_CRM_FEDRESURS_MONITORING"            # Отслеживаем ли через федресурс

    fedresurs_found = "UF_CRM_1777451201"                           # Был ли найден контакт при поиске на федресурсе
    fedresurs_found_status_yes = 2613
    fedresurs_found_status_no = 2614

    find_fedresurs = "UF_CRM_1777786944"                            # JSON Полученный при search_person на федресурс (CACHE)
    info_fedresurs = "UF_CRM_1777455350"                            # JSON полученный при get_person на федресурс (CACHE)
    messages_fedresurs = "UF_CRM_1777788590"                        # JSON Полученный при get_messages