import frappe

@frappe.whitelist()
def item_warehouse_info(item, warehouse=None, posting_date=None, posting_time=None):
	"""
	Returns the item details for the specified item-warehouse pair
	if warehouse is not specified, it will bring back the data from all the warehouses
	Item A
		- Warehouse A val_rate, qty's--
		- Warehouse B val_rate, qty's
		
	!! Data is fetched from Bins
	Data is returned as dicts
	
	!! available_qty = actual_qty - reserved_qty - reserved_qty_for_production
	"""
	
	# doc : https://frappe.github.io/frappe/current/api/frappe.database#get_value
	# if is not stock item, return error
	if not frappe.db.get_value("Item", item, "is_stock_item"):
		return "not_stock_item"

	if not posting_date:
		# actualy_qty -- qty physically present at store (includes qty that is yet to be delivered)
		if not warehouse:
			return frappe.db.sql("select warehouse, valuation_rate, (actual_qty - reserved_qty - reserved_qty_for_production) as available_qty, actual_qty, planned_qty, indented_qty, ordered_qty, reserved_qty, reserved_qty_for_production, projected_qty from tabBin where item_code = '"+ item +"';", as_dict=True) or {}
		else:
			return frappe.db.sql("select valuation_rate, (actual_qty - reserved_qty - reserved_qty_for_production) as available_qty, actual_qty, planned_qty, indented_qty, ordered_qty, reserved_qty, reserved_qty_for_production, projected_qty from tabBin where item_code = '"+ item +"' and warehouse = '"+warehouse+"';", as_dict=True) or {}
	else:
		from erpnext.stock.stock_ledger import get_previous_sle
		previous_sle = get_previous_sle({
				"item_code": item,
				"warehouse": warehouse,
				"posting_date": posting_date,
				"posting_time": posting_time
			})

			# get actual stock at source warehouse
		return previous_sle.get("qty_after_transaction") or 0