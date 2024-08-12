from aiogram import  F, types, Router
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_account_balance, orm_get_account,  \
                               orm_get_accounts_with_currencies, \
                                orm_get_last_account_operation
from kbds.inline import get_callback_btns
from kbds.reply import balance_KB

user_balance_router = Router()

# Смотрим остатки
@user_balance_router.message(F.text.lower() == "посмотреть остатки")
async def get_balance_cmd(message: types.Message, session: AsyncSession):
    accounts = await orm_get_accounts_with_currencies (session, message.from_user.id)
    if len(accounts) == 0:
        await message.answer("У Вас пока нет счетов.", reply_markup=types.ReplyKeyboardRemove())    
    else:
        btns = {'Все счета':'getaccbal_Все счета'}
        for account in accounts:
            btns[account.name+' ('+account.curr_cod+")"] = f"getaccbal_{account.id}"
        await message.answer("Выберите счет:", reply_markup=get_callback_btns(btns=btns)) 

@user_balance_router.callback_query(F.data.startswith("getaccbal_"))
async def get_balance_accounts_callback_cmd(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    var = callback.data.split("_")[-1]
    if var == "Все счета":
        accounts = await orm_get_accounts_with_currencies(session, callback.from_user.id)
        await callback.message.answer("Остатки на счетах:")
        total = {}
        for account in accounts:
           balance = await orm_get_account_balance(session, account.id)
           last_date = await orm_get_last_account_operation(session, account.id)
           if not balance:
               balance = 0
           message_line = "Счет: <b>" + account.name + " ("+ account.type +") </b> Остаток: " + \
                           "<b>" + str(round(balance, 2)) + "</b> ("+account.curr_cod+")" 
           if last_date:
               message_line = message_line + " \n Последняя операция: " + str(last_date[0].day) + "-" + str(last_date[0].month) + \
                          "-" + str(last_date[0].year)
           if account.curr_cod in total:
               total[account.curr_cod] = total[account.curr_cod] + balance
           else:
               total[account.curr_cod] = balance
           await callback.message.answer(message_line, parse_mode='HTML')

        await callback.message.answer("Итого:")
        for key, value in total.items():
            await callback.message.answer(key + ": <b>"+str(round(total[key], 2))+"</b>", parse_mode='HTML')

    else:
        account = await orm_get_account(session, id=int(var))
        balance = await orm_get_account_balance(session, account.id)
        last_date = await orm_get_last_account_operation(session, account.id)
        if not balance:
            balance = 0
        message_line = "Счет: <b>" + account.name + " ("+ account.type +") </b> Остаток: " + \
                        "<b>" + str(round(balance, 2)) + "</b> " 
        if last_date:
            message_line = message_line + " \n Последняя операция: " + str(last_date[0].day) + "-" + str(last_date[0].month) + \
                        "-" + str(last_date[0].year)

        await callback.message.answer(message_line, parse_mode='HTML', reply_markup=balance_KB)

