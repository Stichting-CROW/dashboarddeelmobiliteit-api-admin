from yearly_cost_overview import db
from datetime import date
import xlsxwriter
from xlsxwriter import Workbook, worksheet
import io
from acl import acl
from fastapi import HTTPException

bold_format = None
currency_format = None

def is_allowed_to_create_yearly_cost_overview(acl: acl.ACL):
    return acl.is_admin == True

def calculate(acl: acl.ACL, reference_date: date):
    if not is_allowed_to_create_yearly_cost_overview(acl):
        raise HTTPException(status_code=403, detail="user not authorized to list yearly cost overview")
    rows = db.query_yearly_cost_overview(reference_date)
    return generate_excel_sheet(rows, reference_date.isoformat())

def generate_excel_sheet(rows, reference_date: str):
    global bold_format, currency_format
    sio = io.BytesIO()
    workbook = xlsxwriter.Workbook(sio, {'in_memory': True})
    bold_format = workbook.add_format({'bold': True}) 
    currency_format = workbook.add_format({'num_format': '€0.00'})
    worksheet = workbook.add_worksheet("Kostenoverzicht")
    add_content(worksheet, rows, reference_date)
    workbook.close()
    sio.seek(0)
    return sio

def add_content(sheet: worksheet, rows, reference_date: str):
    sheet.set_column('A:A', 30) 
    sheet.set_column('B:B', 25) 
    sheet.set_column('C:F', 15) 
    add_default_values(sheet, row_index=0, col_index=0)
    add_data(rows, sheet, 5, 0, reference_date)
    
def add_default_values(sheet: worksheet, row_index: int, col_index: int):
    sheet.write(row_index, col_index, "Instellingen", bold_format)
    row_index += 1
    sheet.write(row_index, col_index, "Basiskosten:")
    sheet.write(row_index, col_index + 1, 1250, currency_format)
    row_index += 1
    sheet.write(row_index, col_index, "Kosten per voertuig:")
    sheet.write(row_index, col_index + 1, 2.50, currency_format)
    row_index += 1
    sheet.write(row_index, col_index, "Max aantal voertuigen vrijstelling bijdrage:")
    sheet.write(row_index, col_index + 1, 50)

def add_data(rows, sheet: worksheet, row_index: int, col_index: int, reference_date: str):
    sheet.write(row_index, 0, "Peildatum: " + reference_date, bold_format)
    row_index += 1
    sheet.write(row_index, 0, "Organisatie", bold_format)
    sheet.write(row_index, 1, "Aantal voertuigen op peildatum",bold_format)
    sheet.write(row_index, 2, "Basiskosten",bold_format)
    sheet.write(row_index, 3, "Kosten voertuigen",bold_format)
    sheet.write(row_index, 4, "Totaal",bold_format)
    row_index += 1
    start_index = row_index
    for row in rows:
        sheet.write(row_index, col_index, row["name"])
        sheet.write(row_index, col_index + 1, row["number_of_vehicles"])
        sheet.write_formula(row_index, col_index + 2, "=IF(B{row}>$B$4, $B$2, 0)".format(row=row_index + 1), currency_format)
        sheet.write_formula(row_index, col_index + 3, "=IF(B{row}>$B$4, $B$3*B{row}, 0)".format(row=row_index + 1), currency_format)
        sheet.write_formula(row_index, col_index + 4, "=SUM(C{row}:D{row})".format(row=row_index + 1), currency_format)
        row_index += 1
    sheet.write_formula(row_index, col_index + 4, "=SUM(E{start_index}:E{end_index})".format(start_index=start_index+1, end_index=row_index), currency_format)
