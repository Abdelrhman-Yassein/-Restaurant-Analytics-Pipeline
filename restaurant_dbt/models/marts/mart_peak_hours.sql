SELECT  hour
       ,COUNT(order_id)                     AS total_orders
       ,ROUND(SUM(total_amount)::numeric,2) AS total_revenue
FROM {{ ref('stg_orders')}}
GROUP BY  hour