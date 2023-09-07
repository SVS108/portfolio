-- ************* Первые пять задач — написание SELECT запросов к таблице sales

--1. Вывести все параметры, относящиеся к покупкам, которые
--   совершал Calvin Potter

select  transaction_id , transaction_date, transaction_time,
		quantity, unit_price, product_id, product_name  
from coffe_shop.sales s
left join coffe_shop.customer c 
on s.customer_id = c.customer_id 
where c.customer_name  = 'Calvin Potter'

-- 2. Посчитать средний чек покупателей по дням

select transaction_date, avg(quantity*unit_price) as avg_bill
from coffe_shop.sales s 
group by 1
order by transaction_date

-- 3. Преобразуйте дату транзакции в нужный формат: год, месяц, день.
--    Приведите названия продуктов к стандартному виду в нижнем регистре

select transaction_date, 
	   date_part('year', date(transaction_date)) as trans_year,
	   date_part('month', date(transaction_date)) as trans_month,
	   date_part('day', date(transaction_date)) as trans_day,
	   lower(product_name)
from coffe_shop.sales s 

-- 4. Сделать анализ покупателей и разделить их по категориям.
--    Посчитать количество транзакций, сделанных каждым покупателем. 
--    Разделить их на категории: 
	--    Частые гости (>= 23 транзакций), 
	--    Редкие посетители (< 10 транзакций), 
	--    Стандартные посетители (все остальные)

select *,
case
	when transactions >= 23 then 'Частые гости'
	when transactions < 10 then 'Редкие посетители'
	else 'Стандартные посетители'
end
from 
	(select  c.customer_id, c.customer_name, count(s.transaction_id) as transactions
	from coffe_shop.sales s
	left join coffe_shop.customer c 
	on s.customer_id = c.customer_id
	where c.customer_name is not null
	group by 1
	order by transactions desc,customer_id  desc) as tab 


-- 	5. Посчитать количество уникальных посетителей в каждом магазине
--     каждый день

select transaction_date, store_address, count(customer_id) as customers
from
	(
	select DISTINCT (customer_id), transaction_date, store_address
	from coffe_shop.sales
	) as d
group by 2, 1
order by 2, 1

-- ************* Задачи 6-10 проверяют темы: отношения таблиц (JOIN), агрегация, оконные функции

-- 6. Посчитать количество клиентов по поколениям

select g.generation, count(c.customer_id) as customers_count  
from coffe_shop.customer c 
left join coffe_shop.generations g 
on c.birth_year = g.birth_year 
group by 1 
order by 1

-- 7. Найдите топ 10 самых продаваемых товаров каждый день и
--    проранжируйте их по дням и кол-ву проданных штук

with quant_prods as (
	select transaction_date, product_name, sum(quantity) as quantity_sold_per_day
	from coffe_shop.sales
	group by 2, 1
	order by 1, 3 desc
	),
quant_prods2 as (
	select *,
	ROW_NUMBER() OVER (PARTITION by transaction_date 
					   order by transaction_date, quantity_sold_per_day desc)
	from quant_prods
	)
select * 
from quant_prods2
where row_number <= 10

-- 8. Выведите только те названия регионов, в которых продавался
--    продукт “Columbian Medium Roast”, с последней датой продажи

with qwery1 as (
	select so.neighborhood, s.transaction_date  
	from coffe_shop.sales s 
	left join coffe_shop.sales_outlet so 
	on s.sales_outlet_id = so.sales_outlet_id 
	where s.product_name = 'Columbian Medium Roast'
	order by so.neighborhood, s.transaction_date  
	)
select distinct neighborhood,
last_value(transaction_date) OVER (PARTITION by neighborhood) as last_transaction
from qwery1

-- 9. Соберите витрину из следующих полей:
--    Transaction_date, sales_outlet_id, store_address, product_id,
--    product_name, customer_id, customer_name, gender (заменить на Male, Female, 
--    Not Defined если пустое значение), unit_price, quantity, line_item_amount

-- tables: sales, sales_reciepts

with showcase as (
	select s.transaction_date, s.sales_outlet_id, s.store_address, s.product_id,
	       s.product_name, s.customer_id, s.customer_name, 
			case
				when s.gender = 'F' then 'Female'
				when s.gender = 'M' then 'Male'
				else 'Not Defined'
			end as gender,
			s.unit_price, s.quantity, sr.line_item_amount
	from coffe_shop.sales s 
	left join coffe_shop.sales_reciepts sr 
	on s.transaction_id = sr.transaction_id 
	)
select * 
from showcase

--10. Найдите разницу между максимальной и минимальной ценой
--    товара в категории
select product_category,product_type, product_name, 
	   SUBSTR(current_retail_price, 2)::numeric as retail_price,
       max(SUBSTR(current_retail_price, 2)::numeric) 
       	OVER (PARTITION by product_category) as max_price_category,
       min(SUBSTR(current_retail_price, 2)::numeric) 
		OVER (PARTITION by product_category) as min_price_category,
	   max(SUBSTR(current_retail_price, 2)::numeric) 
       	OVER (PARTITION by product_category) - 
       min(SUBSTR(current_retail_price, 2)::numeric) 
		OVER (PARTITION by product_category) as difference	
from coffe_shop.product 
order by product_category,product_type, product_name 

-- === ДОПОЛНИТЕЛЬНО ===

-- *1. Сделать справочник клиентов. Посчитать возраст клиентов,
--     разделить имя и фамилию на 2 отдельных поля

select c.customer_id, c.customer_name as customer_full_name, 
	   SPLIT_PART(c.customer_name , ' ', 1), SPLIT_PART(c.customer_name , ' ', 2),
	   date(c.birthdate),
	   age(date(now()), date(c.birthdate))  as customer_age
from coffe_shop.customer c 

-- *2. Используя витрину в качестве табличного выражения или
--     подзапроса, посчитайте количество транзакций по полю gender
with showcase as (
	select s.transaction_date, s.sales_outlet_id, s.store_address, s.product_id,
	       s.product_name, s.customer_id, s.customer_name, 
			case
				when s.gender = 'F' then 'Female'
				when s.gender = 'M' then 'Male'
				else 'Not Defined'
			end as gender,
			s.unit_price, s.quantity, sr.line_item_amount
	from coffe_shop.sales s 
	left join coffe_shop.sales_reciepts sr 
	on s.transaction_id = sr.transaction_id 
	)
select gender, count(gender)
from showcase
group by gender 
