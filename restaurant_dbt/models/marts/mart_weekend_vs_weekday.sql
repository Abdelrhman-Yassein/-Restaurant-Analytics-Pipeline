SELECT  is_weekend
       ,COUNT(order_id)                     AS total_order
       ,ROUND(SUM(total_amount)::numeric,2) AS total_revenue
       ,ROUND(AVG(total_amount)::numeric,2) AS avg_order_value
FROM {{ ref('stg_orders')}}
GROUP BY  is_weekend
ORDER BY  total_order DESC