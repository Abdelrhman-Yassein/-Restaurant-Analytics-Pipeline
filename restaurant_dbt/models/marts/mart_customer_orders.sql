SELECT  customer_id
       ,COUNT(order_id)                     AS total_orders
       ,ROUND(SUM(total_amount)::numeric,2) AS total_spent
       ,ROUND(AVG(rating)::numeric,2)       AS avg_rating
       ,MIN(order_date)                     AS first_order
       ,MAX(order_date)                     AS last_ordere
FROM {{ ref('stg_orders')}}
GROUP BY  customer_id
ORDER BY  total_spent DESC