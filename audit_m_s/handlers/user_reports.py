from datetime import datetime
import re

from aiogram import  F, types, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import AsyncSession

from common.states import Period
from database.models import Operation
from database.orm_query import orm_get_account_balance, orm_get_account,  \
                               orm_get_accounts_with_currencies, \
                                orm_get_last_account_operation, orm_get_period_account_transactions
from kbds.inline import get_callback_btns
from kbds.reply import balance_KB

user_reports_router = Router()

# Смотрим доходы
@user_reports_router.message(StateFilter(None), F.text.lower() == "посмотреть доходы")
async def get_earnings_cmd(message: types.Message, session: AsyncSession, state: FSMContext):

    await message.answer("Введите дату начала периода в формате ДД.ММ.ГГГГ:") 
    Period.action = Operation.earnings
    await state.set_state(Period.from_date) #, reply_markup=get_callback_btns(btns=btns)) 

# Смотрим расходы
@user_reports_router.message(StateFilter(None), F.text.lower() == "посмотреть расходы")
async def get_earnings_cmd(message: types.Message, session: AsyncSession, state: FSMContext):

    await message.answer("Введите дату начала периода в формате ДД.ММ.ГГГГ:") 
    Period.action = Operation.expenses
    await state.set_state(Period.from_date) #, reply_markup=get_callback_btns(btns=btns)) 


@user_reports_router.message(Period.from_date)
async def get_start_period_cmd(message: types.Message, session: AsyncSession, state: FSMContext):
    str_date = message.text.replace(",",".").replace("/", ".").replace("-", ".")
    try:
        from_date = re.findall(r'[0-9]{2}\.[0-9]{2}\.[0-9]{4}', str_date)[0]
        try:
            get_date = datetime.strptime(from_date, '%d.%m.%Y')
        except:
            await message.answer("Дата введена не правильно. Введите заново..")
            return   
    except:
        await message.answer("Дата введена не в правильном формате. Введите заново..")
        return     
    
    await state.update_data(from_date=datetime.date(get_date))

    await message.answer("Введите дату окончания периода в формате ДД.ММ.ГГГГ:") 
    await state.set_state(Period.to_date) 

@user_reports_router.message(Period.to_date)
async def get_start_period_cmd(message: types.Message, session: AsyncSession, state: FSMContext):
    str_date = message.text.replace(",",".").replace("/", ".").replace("-", ".")
    try:
        to_date = re.findall(r'[0-9]{2}\.[0-9]{2}\.[0-9]{4}', str_date)[0]
        try:
            get_date = datetime.strptime(to_date, '%d.%m.%Y')
        except:
            await message.answer("Дата введена не правильно. Введите заново..")
            return   
    except:
        await message.answer("Дата введена не в правильном формате. Введите заново..")
        return     
    await state.update_data(to_date=datetime.date(get_date))

    data = await state.get_data()
    result = await orm_get_period_account_transactions(session=session, user_id=message.from_user.id, operation=Period.action, start_date=data['from_date'], end_date=data['to_date'])
    if len(result) > 0:
        for r in result:
            print(r)
            await message.answer(str(datetime.date(r.created))+" счет: "+r.account_label + ", категория: " + r.category_label + " "+str(r.sum))
    else:
        await message.answer("Ничего не найдено в этом периоде... :(..") 
    await state.clear()
    Period.action = None

