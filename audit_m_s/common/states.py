from aiogram.fsm.state import State, StatesGroup

 
class AddAccountType(StatesGroup):
    #Шаги состояний
    name = State()
    texts = {
            'AddAccounttype:name': 'Введите название типа счета заново:',
        }
        
class AddAccountCurrency(StatesGroup):
    #Шаги состояний
    user_id = int,
    name = State()
    cod = State()
    for_change = None
    texts = {
            'AddAccountCurrency:name': 'Введите название валюты заново:',
            'AddAccountCurrency:cod': 'Введите код валюты занова:',
        }
    
class AddAccount(StatesGroup):
    #Шаги состояний
    user_id = int,
    name = State()
    type_id = State()
    currency_id = State()
    limit = State()
    for_change = None
    texts = {
            'AddAccount:name': 'Введите название счета заново:',
            'AddAccount:type_id': 'Выберите тип счета заново:',
            'AddAccount:currency_id': 'Выберите валюту счета заново:',
            'AddAccount:limit': 'Введите лимит счета заново:',
        }
    
class AddCategory(StatesGroup):
    #Шаги состояний
    name = State()
    category_type = State()
    for_change = None
    texts = {
            'AddCategory:categoty_type': 'Выберите тип категории заново:',
            'AddCategory:name': 'Введите название типа счета заново:',
        }
    
class AddPlace(StatesGroup):
    #Шаги состояний
    name = State()
    texts = {
            'AddPlace:name': 'Введите название места заново:',
        }
        
class AddBudget(StatesGroup):
    #Шаги состояний
    action = None # запишем сюда вариант того, что вводим: переводы, отстатки, доходы или расходы
    account_id = State()
    transfer_account_id = State()
    category_id = State()
    place_id = State()
    sum = State()
    comment =State()
    texts = {
            'AddBudget:account_id': 'Выберете счет заново:',
            'AddBudget:category_type': 'Выберите тип категории заново',
            'AddBudget:category_id': 'Выберите категорию заново',
            'AddBudget:place': 'Выберите место заново',
            'AddBudget:sum': 'Введите сумму заново',
            'AddBudget:comment': 'Введите коментарий заново',
    }

class Period(StatesGroup):
    action = None # запишем сюда вариант того, что вводим: переводы, отстатки, доходы или расходы
    from_date = State()
    to_date =  State()
    texts = {
            'ListEarnings:from_date': 'Введите дату начала периода заново:',
            'ListEarnings:to_date': 'Введите дату окончания периода заново:'
            }