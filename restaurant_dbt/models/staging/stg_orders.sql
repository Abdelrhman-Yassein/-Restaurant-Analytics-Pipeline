SELECT  order_id
       ,CAST(order_date AS DATE) AS order_date
       ,hour
       ,category
       ,item_name
       ,price
       ,quantity
       ,discount
       ,total_amount
       ,branch
       ,payment_method
       ,order_type
       ,customer_id
       ,rating
       ,is_weekend
FROM raw.orders