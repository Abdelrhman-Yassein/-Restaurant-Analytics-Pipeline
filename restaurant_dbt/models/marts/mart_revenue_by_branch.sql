SELECT  branch
       ,ROUND(SUM(total_amount)::numeric,2) AS total_revenue
       ,COUNT(distinct order_id)            AS total_orders
       ,SUM(quantity)                       AS total_quantity
       ,ROUND(AVG(rating::numeric),2)       AS avg_rating
FROM {{ ref('stg_orders')}}
GROUP BY  branch
ORDER BY  total_revenue desc