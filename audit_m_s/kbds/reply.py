from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboard(
    *btns: str,
    placeholder: str = None,
    request_contact: int = None,
    request_location: int = None,
    sizes: tuple[int] = (2,),
):
    '''
    Parameters request_contact and request_location must be as indexes of btns args for buttons you need.
    Example:
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона"
            placeholder="Что вас интересует?",
            request_contact=4,
            sizes=(2, 2, 1)
        )
    '''
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):
        
        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:

            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
            resize_keyboard=True, input_field_placeholder=placeholder)


main_KB = get_keyboard(
            "Доходы",
            "Расходы",
            "Остатки",
            "Переводы",
            "Отчеты",
            "Справочники",
            placeholder="Что вас интересует?",
            sizes=(2, 2, 2)
                )

directory_KB = get_keyboard(
            "Счета",
            "Категории",
            "Места",
            "В начало",
            placeholder="Что вас интересует?",
            sizes=(2, 2,)
                )

account_type_KB = get_keyboard(
    "Добавить тип счета",
    "Назад к меню счетов",
    "В начало",
    placeholder="Выберите действие",
    sizes=(2,),
    )

account_currency_KB = get_keyboard(
    "Добавить валютy",
    "Назад к меню счетов",
    "В начало",
    placeholder="Выберите действие",
    sizes=(2,),
    )

account_KB = get_keyboard(
    "Посмотреть счета",
    "Добавить счет",
    "Типы счетов",
    "Валюты счетов",
    "В начало",
    placeholder="Выберите действие",
    sizes=(2,2,2),
)

balance_KB = get_keyboard(
    "Посмотреть остатки",
    "Изменить остатки",
    "В начало",    
    placeholder="Выберите действие",
    sizes=(2,1),
)

category_KB = get_keyboard(
    "Добавить категорию",
    "В начало",
    placeholder="Выберите действие",
    sizes=(2,),
    )

place_KB = get_keyboard(
    "Добавить место",
    "В начало",
    placeholder="Выберите действие",
    sizes=(2,),
    )

earnings_KB = get_keyboard(
    "Посмотреть доходы",
    "Добавить доходы",
    "В начало",    
    placeholder="Выберите действие",
    sizes=(2,1),
)

expenses_KB = get_keyboard(
    "Посмотреть расходы",
    "Добавить расходы",
    "В начало",    
    placeholder="Выберите действие",
    sizes=(2,1),
)

transfer_KB = get_keyboard(
    "Посмотреть переводы",
    "Добавить переводы",
    "В начало",    
    placeholder="Выберите действие",
    sizes=(2,1),
)