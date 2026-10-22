C1
SELECT *FROM parts
WHERE category = 'Mechanical';
 C2
SELECT * FROM parts
WHERE unit_price > 1000
ORDER BY unit_price DESC;


C3
SELECT category, AVG(unit_price) AS average_price
FROM parts
GROUP BY category;


C4
SELECT category, SUM(stock_qty) AS total_stock
FROM parts
GROUP BY category;


C5
SELECT po.po_id, s.supplier_name, po.order_date, po.status
FROM purchase_orders po
JOIN suppliers s ON po.supplier_id = s.supplier_id;


C6
SELECT poi.po_id, p.part_name, poi.quantity, p.unit_price
FROM purchase_orders po
JOIN purchase_order_items poi ON po.po_id = poi.po_id
JOIN parts p ON poi.part_id = p.part_id;


C7
SELECT poi.po_id, p.part_name, poi.quantity, p.unit_price,
poi.quantity * p.unit_price AS line_total
FROM purchase_orders po
JOIN purchase_order_items poi ON po.po_id = poi.po_id
JOIN parts p ON poi.part_id = p.part_id;


C8
SELECT s.supplier_id, s.supplier_name, s.city,
po.po_id, po.order_date, po.status
FROM suppliers s
LEFT JOIN purchase_orders po ON s.supplier_id = po.supplier_id;


C9
SELECT s.* FROM suppliers s
LEFT JOIN purchase_orders po ON s.supplier_id = po.supplier_id
WHERE po.po_id IS NULL;
C10

CREATE OR REPLACE VIEW purchase_order_summary AS
SELECT po.po_id, s.supplier_name, p.part_name,
      poi.quantity, p.unit_price,
      poi.quantity * p.unit_price AS line_total,
      po.status
FROM purchase_orders po
JOIN suppliers s
ON po.supplier_id = s.supplier_id
JOIN purchase_order_items poi
ON po.po_id = poi.po_id
JOIN parts p
ON poi.part_id = p.part_id;

2nd part question
SELECT *
FROM purchase_order_summary
WHERE status = 'Pending';

C11

CREATE OR REPLACE FUNCTION calculate_part_discount(amount NUMERIC)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
BEGIN
   IF amount >= 2000 THEN
       RETURN amount * 0.10;
   ELSE
       RETURN 0;
   END IF;
END;
$$;


SELECT part_name, unit_price, calculate_part_discount(unit_price) AS discount
FROM parts;

C12

CREATE OR REPLACE FUNCTION final_part_price(amount NUMERIC)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
BEGIN
   RETURN amount - calculate_part_discount(amount);
END;
$$;

SELECT part_name, unit_price,
      calculate_part_discount(unit_price) AS discount,
      final_part_price(unit_price) AS final_price
FROM parts;

C13

CREATE OR REPLACE PROCEDURE update_po_status(
   p_po_id INT,
   p_new_status VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
   UPDATE purchase_orders
   SET status = p_new_status
   WHERE po_id = p_po_id;
END;
$$;

CALL update_po_status(1004, 'Received');

SELECT *
FROM purchase_orders
WHERE po_id = 1004;

C14

CREATE OR REPLACE PROCEDURE mark_old_pending_orders()
LANGUAGE plpgsql
AS $$
BEGIN
   UPDATE purchase_orders
   SET status = 'Received'
   WHERE status = 'Pending'
     AND order_date < DATE '2026-10-04';
END;
$$;


CALL mark_old_pending_orders();

SELECT *
FROM purchase_orders
ORDER BY po_id;
