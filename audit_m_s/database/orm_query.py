import calendar
import datetime as dt
from datetime import datetime, timedelta as t

from sqlalchemy import select, update, delete, func, and_, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from database.models import Account_currency, Account_type, Account, Budget, Category, Operation, Place

## ------ ORM база данных account_type
##
async def orm_add_account_type(session: AsyncSession, data: dict):
    obj = Account_type(
           user_id = data['user_id'], 
           name = data['name'],
          )
    session.add(obj)
    await session.commit()

async def orm_get_account_types(session: AsyncSession, user_id: int):
    query = select(Account_type).where(Account_type.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_account_type(session: AsyncSession, type_id: int):
    query = select(Account_type).where(Account_type.id == type_id)
    result = await session.execute(query)
    return result.scalar()

async def orm_delete_account_types(session: AsyncSession, id: int):
    query = delete(Account_type).where(Account_type.id == id)
    await session.execute(query)
    await session.commit()

async def orm_change_account_types(session: AsyncSession, account_type_id: int, name):
    query = update(Account_type).where(Account_type.id == account_type_id).values(name=name)
    await session.execute(query)
    await session.commit()

## ------ ORM база данных account_currency
##
async def orm_add_account_currency(session: AsyncSession, user_id: int, data: dict):
    obj = Account_currency(
           user_id = user_id,
           name = data['name'],
           cod = data['cod'],
          )
    session.add(obj)
    await session.commit()

async def orm_get_account_currencies(session: AsyncSession, user_id: int):
    query = select(Account_currency).where(Account_currency.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_account_currency(session: AsyncSession, id: int):
    query = select(Account_currency).where(Account_currency.id == id)
    result = await session.execute(query)
    return result.scalar()

async def orm_delete_account_currency(session: AsyncSession, id: int):
    query = delete(Account_currency).where(Account_currency.id == id)
    await session.execute(query)
    await session.commit()

async def orm_change_account_currency(session: AsyncSession, account_currency_id: int, data: dict):
    query = update(Account_currency).where(Account_currency.id == account_currency_id).values(name=data['name'], cod=data['cod'])
    await session.execute(query)
    await session.commit()

## ------ ORM база данных account
##
async def orm_get_accounts(session: AsyncSession, user_id: int):
    query = select(Account).where(Account.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()   

async def orm_get_accounts_with_currencies(session: AsyncSession, user_id: int):
    query = select(Account.id, Account.name, Account_currency.cod.label("curr_cod"), Account_type.name.label("type")).where(Account.user_id == user_id) \
            .join(Account_currency, Account_currency.id==Account.currency_id) \
            .join(Account_type, Account_type.id==Account.type_id)
    print(query.compile(compile_kwargs={'literal_binds': True}))
    result = await session.execute(query)
    return result.all()   

async def orm_get_account(session: AsyncSession, id: int):
    a = aliased(Account)
    t = aliased(Account_type)
    c = aliased(Account_currency)
    query = select(a.id, a.name, t.name.label("type"), c.name.label("currency"), a.limit.label("limit")).where(a.id == id) \
            .join(t, a.type_id==t.id)                        \
            .join(c, a.currency_id==c.id)
    # print(query.compile(compile_kwargs={'literal_binds': True}))
    result = await session.execute(query)
    return result.first()

async def orm_get_account_limit(session: AsyncSession, id: int):
    a = aliased(Account)
    query = select(a.limit).where(a.id == id)
    result = await session.execute(query)
    return result.scalar()
    
async def orm_add_account(session: AsyncSession, user_id: int, data: dict):
    obj = Account(
           user_id = user_id,
           name = data['name'],
           type_id = data['type_id'],
           currency_id = data['currency_id'],
           limit = data['limit'],
          )
    session.add(obj)
    await session.commit()

async def orm_delete_account(session: AsyncSession, id: int):
    query = delete(Account).where(Account.id == id)
    await session.execute(query)
    await session.commit()


async def orm_change_account(session: AsyncSession, account_id: int, data: dict):
    query = update(Account).where(Account.id == account_id).values(name=data['name'], type_id=data['type_id'], \
                                                                   currency_id=data['currency_id'], limit=data['limit'])
    await session.execute(query)
    await session.commit()


## ------ ORM база данных category
##
async def orm_add_category(session: AsyncSession, data: dict):
    obj = Category(
           user_id = data['user_id'], 
           category_type = data['category_type'],
           name = data['name'],
          )
    session.add(obj)
    await session.commit()

async def orm_get_categories(session: AsyncSession, user_id: int):
    query = select(Category).where(Category.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_categories_by_operation(session: AsyncSession, user_id: int, operation: Operation):
    query = select(Category).where(Category.user_id == user_id).where(Category.category_type==operation) \
                            .where(Category.name!="Перевод").where(Category.name!="Остаток")
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_category(session: AsyncSession, id: int):
    query = select(Category).where(Category.id == id)
    result = await session.execute(query)
    return result.scalar()

async def orm_delete_category(session: AsyncSession, id: int):
    query = delete(Category).where(Category.id == id)
    await session.execute(query)
    await session.commit()

async def orm_change_category(session: AsyncSession, id: int, data):
    query = update(Category).where(Category.id == id).values(name=data['name'], category_type=data['category_type'])
    await session.execute(query)
    await session.commit()

## ------ ORM база данных places
##
async def orm_add_place(session: AsyncSession, data: dict):
    obj = Place(
           user_id = data['user_id'], 
           name = data['name'],
          )
    session.add(obj)
    await session.commit()

async def orm_get_places(session: AsyncSession, user_id: int):
    query = select(Place).where(Place.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_place(session: AsyncSession, id: int):
    query = select(Place).where(Place.id == id)
    result = await session.execute(query)
    return result.scalar()

async def orm_delete_place(session: AsyncSession, id: int):
    query = delete(Place).where(Place.id == id)
    await session.execute(query)
    await session.commit()

async def orm_change_place(session: AsyncSession, id: int, name):
    query = update(Place).where(Place.id == id).values(name=name)
    await session.execute(query)
    await session.commit()

## ------ ORM база данных budget
##
async def orm_add_transaction(session: AsyncSession, user_id, data: dict):
    obj = Budget(
           user_id = user_id, 
           account_id = data['account_id'],
           category_id = data['category_id'],
           place_id = data['place_id'],
           sum = data['sum'],
           comment = data['comment'],
          )
    session.add(obj)
    await session.commit()

async def orm_get_account_balance(session: AsyncSession, account_id: int):
    """
        with earnings as (
            select account_id, sum(sum) as earnings_sum
            from budget b 
            join categories c on c.id = b.category_id 
            WHERE c.category_type = "earnings" and account_id = 1
            ),
        expenses as (
            select account_id, sum(sum) as expenses_sum
            from budget b 
            join categories c on c.id = b.category_id 
            WHERE c.category_type = "expenses" and account_id = 1
            )
        SELECT earnings.account_id, earnings_sum-expenses_sum as balance 
        FROM  earnings 
        join expenses on earnings.account_id = expenses.account_id 
    """

    b = aliased(Budget)
    c = aliased(Category)

    cte_earnings = (
        select(func.sum(b.sum).label("earnings_sum"))
        .where(and_(c.category_type=="earnings", b.account_id==account_id))
        .join(c, c.id==b.category_id)
    ).cte("earnings")
    cte_expenses = (
        select(func.sum(b.sum).label("expenses_sum"))
        .where(and_(c.category_type=="expenses", b.account_id==account_id))
        .join(c, c.id==b.category_id)
    ).cte("expenses")
    query = select(cte_earnings.c.earnings_sum, cte_expenses.c.expenses_sum)

    print(query.compile(compile_kwargs={'literal_binds': True}))
    result = await session.execute(query)
    res = result.first()
    if not res[1]:
        return res[0]
    else:
        return res[0] - res[1]

async def orm_get_last_account_operation(session: AsyncSession, account_id: int):
    query = select(Budget.created).where(Budget.account_id==account_id).order_by(Budget.created.desc()).limit(1)
    result = await session.execute(query)
    return result.first()

async def orm_get_month_account_expenses(session: AsyncSession, account_id: int):
    month = dt.datetime.now().month
    year = dt.datetime.now().year
    start_date = dt.date(year, month, 1)
    days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
    end_date = start_date + t(days=days_in_month-1)
    
    query = select(func.sum(Budget.sum)).where(Budget.account_id==account_id) \
            .join(Category, Category.id==Budget.category_id) \
            .where(Category.category_type == Operation.expenses) \
            .where(Category.name!="Перевод").where(Category.name!="Остаток") \
            .where(Budget.created >= start_date).where(Budget.created <= end_date) 
    result = await session.execute(query)
    return result.scalar()

async def orm_get_period_account_transactions(session: AsyncSession, user_id: int, operation: Operation, start_date: datetime, end_date: datetime):
    query = select(Budget.created, Account.name.label("account_label"), Category.name.label("category_label"), Budget.sum.label("sum")).where(Budget.user_id==user_id) \
            .join(Category, Category.id==Budget.category_id) \
            .join(Account, Account.id==Budget.account_id) \
            .where(Category.category_type == operation.name) \
            .where(Category.name!="Перевод").where(Category.name!="Остаток") \
            .where(Budget.created >= start_date).where(Budget.created <= end_date) 
    result = await session.execute(query)
    return result.all()
