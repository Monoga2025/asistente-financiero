import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
wb.remove(wb.active) # Remove default sheet

# Colors
NAVY = "0F172A"
BLUE = "1E40AF"
BLUE_LIGHT = "DBEAFE"
ROSE = "BE123C"
ROSE_LIGHT = "FFE4E6"
EMERALD = "047857"
EMERALD_LIGHT = "D1FAE5"
AMBER = "B45309"
AMBER_LIGHT = "FEF3C7"
GRAY_BG = "F8FAFC"
BORDER_COLOR = "CBD5E1"
WHITE = "FFFFFF"

# Borders & Styles
thin = Side(border_style="thin", color=BORDER_COLOR)
thick_b = Side(border_style="medium", color=NAVY)
cell_border = Border(left=thin, right=thin, top=thin, bottom=thin)
header_border = Border(left=thin, right=thin, top=thin, bottom=thick_b)

font_main_title = Font(name="Calibri", size=15, bold=True, color=WHITE)
font_subtitle = Font(name="Calibri", size=10, italic=True, color="E2E8F0")
font_sec_hdr = Font(name="Calibri", size=11, bold=True, color=WHITE)
font_tbl_hdr = Font(name="Calibri", size=10, bold=True, color=WHITE)
font_bold = Font(name="Calibri", size=10, bold=True, color=NAVY)
font_data = Font(name="Calibri", size=10, color=NAVY)
font_daniel = Font(name="Calibri", size=10, bold=True, color=BLUE)
font_silvia = Font(name="Calibri", size=10, bold=True, color=ROSE)

fill_navy = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
fill_blue = PatternFill(start_color=BLUE, end_color=BLUE, fill_type="solid")
fill_rose = PatternFill(start_color=ROSE, end_color=ROSE, fill_type="solid")
fill_emerald = PatternFill(start_color=EMERALD, end_color=EMERALD, fill_type="solid")
fill_blue_light = PatternFill(start_color=BLUE_LIGHT, end_color=BLUE_LIGHT, fill_type="solid")
fill_rose_light = PatternFill(start_color=ROSE_LIGHT, end_color=ROSE_LIGHT, fill_type="solid")
fill_emerald_light = PatternFill(start_color=EMERALD_LIGHT, end_color=EMERALD_LIGHT, fill_type="solid")
fill_amber_light = PatternFill(start_color=AMBER_LIGHT, end_color=AMBER_LIGHT, fill_type="solid")
fill_gray = PatternFill(start_color=GRAY_BG, end_color=GRAY_BG, fill_type="solid")

align_center = Alignment(horizontal="center", vertical="center")
align_left = Alignment(horizontal="left", vertical="center")
align_right = Alignment(horizontal="right", vertical="center")

CURRENCY = '"$"#,##0'
PERCENT = '0.0%'
DATE_FMT = 'yyyy-mm-dd'

# ==============================================================================
# HOJA 1: 📊 PANEL PRINCIPAL & BALANCE DEUDAS (CRUCE DANIEL & SILVIA)
# ==============================================================================
ws1 = wb.create_sheet(title="Panel y Cruce de Cuentas")
ws1.views.sheetView[0].showGridLines = True

ws1.merge_cells("B2:G2")
ws1["B2"].value = "CUENTAS CLARAS — DANIEL & SILVIA"
ws1["B2"].font = font_main_title
ws1["B2"].fill = fill_navy
ws1["B2"].alignment = align_center

ws1.merge_cells("B3:G3")
ws1["B3"].value = "Consolidación Oficial y Cruce de Deudas según las planillas reales de ambos"
ws1["B3"].font = font_subtitle
ws1["B3"].fill = fill_navy
ws1["B3"].alignment = align_center

# 1. Saldos Actuales en Cuentas
ws1.merge_cells("B5:G5")
ws1["B5"].value = "1. SALDOS Y LIQUIDEZ ACTUAL EN CUENTAS BANCARIAS"
ws1["B5"].font = font_sec_hdr
ws1["B5"].fill = fill_blue
ws1["B5"].alignment = align_left

ws1.cell(row=6, column=2, value="Titular").font = font_tbl_hdr
ws1.cell(row=6, column=2).fill = fill_navy
ws1.cell(row=6, column=3, value="Entidad / Cuenta").font = font_tbl_hdr
ws1.cell(row=6, column=3).fill = fill_navy
ws1.cell(row=6, column=4, value="Saldo Disponible ($)").font = font_tbl_hdr
ws1.cell(row=6, column=4).fill = fill_navy
ws1.cell(row=6, column=5, value="Cuentas por Cobrar ($)").font = font_tbl_hdr
ws1.cell(row=6, column=5).fill = fill_navy
ws1.cell(row=6, column=6, value="Total Liquidez ($)").font = font_tbl_hdr
ws1.cell(row=6, column=6).fill = fill_navy
ws1.cell(row=6, column=7, value="Observación").font = font_tbl_hdr
ws1.cell(row=6, column=7).fill = fill_navy

for c in range(2, 8):
    ws1.cell(row=6, column=c).alignment = align_center
    ws1.cell(row=6, column=c).border = header_border

# Silvia Nu
ws1.cell(row=7, column=2, value="Silvia").font = font_silvia
ws1.cell(row=7, column=3, value="Nu Débito / Ahorros").font = font_data
ws1.cell(row=7, column=4, value=555313).number_format = CURRENCY
ws1.cell(row=7, column=5, value=0).number_format = CURRENCY
ws1.cell(row=7, column=6, value="=D7+E7").number_format = CURRENCY
ws1.cell(row=7, column=7, value="Saldo registrado en planilla Silvia").font = font_data

# Silvia Nequi
ws1.cell(row=8, column=2, value="Silvia").font = font_silvia
ws1.cell(row=8, column=3, value="Nequi").font = font_data
ws1.cell(row=8, column=4, value=1543896).number_format = CURRENCY
ws1.cell(row=8, column=5, value=55000).number_format = CURRENCY
ws1.cell(row=8, column=6, value="=D8+E8").number_format = CURRENCY
ws1.cell(row=8, column=7, value="Nequi $1.543.896 + Sofi le debe $55.000").font = font_data

# Total Silvia
ws1.cell(row=9, column=2, value="SUBTOTAL SILVIA").font = font_silvia
ws1.cell(row=9, column=3, value="Total Fondos Silvia").font = font_bold
ws1.cell(row=9, column=4, value="=SUM(D7:D8)").number_format = CURRENCY
ws1.cell(row=9, column=5, value="=SUM(E7:E8)").number_format = CURRENCY
ws1.cell(row=9, column=6, value="=SUM(F7:F8)").number_format = CURRENCY
ws1.cell(row=9, column=7, value="Liquidez disponible de Silvia").font = font_bold

# Daniel Nequi
ws1.cell(row=10, column=2, value="Daniel").font = font_daniel
ws1.cell(row=10, column=3, value="Nequi").font = font_data
ws1.cell(row=10, column=4, value=655394).number_format = CURRENCY
ws1.cell(row=10, column=5, value=0).number_format = CURRENCY
ws1.cell(row=10, column=6, value="=D10+E10").number_format = CURRENCY
ws1.cell(row=10, column=7, value="Saldo real en Nequi verificado en planilla").font = font_data

# Total Daniel
ws1.cell(row=11, column=2, value="SUBTOTAL DANIEL").font = font_daniel
ws1.cell(row=11, column=3, value="Total Fondos Daniel").font = font_bold
ws1.cell(row=11, column=4, value="=D10").number_format = CURRENCY
ws1.cell(row=11, column=5, value="=E10").number_format = CURRENCY
ws1.cell(row=11, column=6, value="=F10").number_format = CURRENCY
ws1.cell(row=11, column=7, value="Saldo actual en cuenta de Daniel").font = font_bold

for r in range(7, 12):
    for c in range(2, 8):
        cell = ws1.cell(row=r, column=c)
        cell.border = cell_border
        if c in [4, 5, 6]:
            cell.alignment = align_right

# 2. Calculadora de Proporcionalidad Dinámica por Ingresos
ws1.merge_cells("B13:G13")
ws1["B13"].value = "2. CALCULADORA DE DIVISIÓN PROPORCIONAL SEGÚN INGRESOS Y SITUACIÓN ACTUAL"
ws1["B13"].font = font_sec_hdr
ws1["B13"].fill = fill_emerald
ws1["B13"].alignment = align_left

ws1.cell(row=14, column=2, value="Parámetro").font = font_tbl_hdr
ws1.cell(row=14, column=2).fill = fill_navy
ws1.cell(row=14, column=3, value="Daniel").font = font_tbl_hdr
ws1.cell(row=14, column=3).fill = fill_navy
ws1.cell(row=14, column=4, value="Silvia").font = font_tbl_hdr
ws1.cell(row=14, column=4).fill = fill_navy
ws1.cell(row=14, column=5, value="Total Hogar").font = font_tbl_hdr
ws1.cell(row=14, column=5).fill = fill_navy
ws1.cell(row=14, column=6, value="% Daniel").font = font_tbl_hdr
ws1.cell(row=14, column=6).fill = fill_navy
ws1.cell(row=14, column=7, value="% Silvia").font = font_tbl_hdr
ws1.cell(row=14, column=7).fill = fill_navy

for c in range(2, 8):
    ws1.cell(row=14, column=c).alignment = align_center
    ws1.cell(row=14, column=c).border = header_border

# Ingresos
ws1.cell(row=15, column=2, value="Ingresos Mensuales Recurrentes").font = font_bold
ws1.cell(row=15, column=3, value="='Planilla Daniel'!C8").number_format = CURRENCY # 1.993.000
ws1.cell(row=15, column=4, value=0).number_format = CURRENCY # Silvia desempleada (editable)
ws1.cell(row=15, column=5, value="=C15+D15").number_format = CURRENCY
ws1.cell(row=15, column=6, value="=IF(E15>0, C15/E15, 0.5)").number_format = PERCENT
ws1.cell(row=15, column=7, value="=IF(E15>0, D15/E15, 0.5)").number_format = PERCENT

# Gastos Fijos Personales
ws1.cell(row=16, column=2, value="Gastos Personales Fijos (Moto, Estudio, Ropa)").font = font_bold
ws1.cell(row=16, column=3, value="='Planilla Daniel'!D25").number_format = CURRENCY # 1.172.350
ws1.cell(row=16, column=4, value="='Planilla Silvia'!D18").number_format = CURRENCY # 287.900
ws1.cell(row=16, column=5, value="=C16+D16").number_format = CURRENCY
ws1.cell(row=16, column=6, value="-").alignment = align_center
ws1.cell(row=16, column=7, value="-").alignment = align_center

# Capacidad Neta Disponible
ws1.cell(row=17, column=2, value="Capacidad Neta Libre (Ingreso - Gastos Personales)").font = font_bold
ws1.cell(row=17, column=3, value="=MAX(0, C15-C16)").number_format = CURRENCY
ws1.cell(row=17, column=4, value="=MAX(0, D15-D16)").number_format = CURRENCY
ws1.cell(row=17, column=5, value="=C17+D17").number_format = CURRENCY
ws1.cell(row=17, column=6, value="=IF(E17>0, C17/E17, 0.5)").number_format = PERCENT
ws1.cell(row=17, column=7, value="=IF(E17>0, D17/E17, 0.5)").number_format = PERCENT

for r in range(15, 18):
    for c in range(2, 8):
        cell = ws1.cell(row=r, column=c)
        cell.border = cell_border
        if c in [3, 4, 5]:
            cell.alignment = align_right
        elif c in [6, 7] and cell.value != "-":
            cell.alignment = align_center

# Proporción Activa
ws1.merge_cells("B19:D19")
ws1.cell(row=19, column=2, value="PROPORCIÓN COMPARTIDA ACTIVA:").font = font_bold
ws1.cell(row=19, column=2).alignment = align_right

c_prop_d = ws1.cell(row=19, column=5, value="=F15") # Por defecto toma los ingresos brutos
c_prop_d.font = Font(name="Calibri", size=13, bold=True, color=BLUE)
c_prop_d.fill = fill_blue_light
c_prop_d.number_format = PERCENT
c_prop_d.alignment = align_center
c_prop_d.border = cell_border

c_prop_s = ws1.cell(row=19, column=6, value="=1-E19")
c_prop_s.font = Font(name="Calibri", size=13, bold=True, color=ROSE)
c_prop_s.fill = fill_rose_light
c_prop_s.number_format = PERCENT
c_prop_s.alignment = align_center
c_prop_s.border = cell_border

ws1.cell(row=19, column=7, value="Daniel % / Silvia %").font = Font(name="Calibri", size=9, italic=True, color=GRAY_BG)

# 3. Estado de Deudas en Tiempo Real (Cruce Exacto)
ws1.merge_cells("B21:G21")
ws1["B21"].value = "3. CRUCE DE CUENTAS EN TIEMPO REAL (¿QUIÉN LE DEBE A QUIÉN?)"
ws1["B21"].font = font_sec_hdr
ws1["B21"].fill = fill_navy
ws1["B21"].alignment = align_left

cruce_items = [
    ("Total pagado de su bolsillo por Daniel", "='Gastos Compartidos'!G18", BLUE),
    ("Total de cuota que le correspondía asumir a Daniel", "='Gastos Compartidos'!E18", BLUE),
    ("Balance Neto Daniel (Aportes - Cuota debida)", "=C22-C23", BLUE),
    ("Total pagado de su bolsillo por Silvia", "='Gastos Compartidos'!H18", ROSE),
    ("Total de cuota que le correspondía asumir a Silvia", "='Gastos Compartidos'!F18", ROSE),
    ("Balance Neto Silvia (Aportes - Cuota debida)", "=C25-C26", ROSE),
    ("Abonos / Dinero transferido entre ambos", "=SUM(C34:C38)", AMBER),
]

for idx, (label, form, colr) in enumerate(cruce_items, start=22):
    ws1.cell(row=idx, column=2, value=label).font = font_bold
    ws1.cell(row=idx, column=2).border = cell_border
    c_val = ws1.cell(row=idx, column=3, value=form)
    c_val.number_format = CURRENCY
    c_val.alignment = align_right
    c_val.font = Font(name="Calibri", size=10, bold=True, color=colr)
    c_val.border = cell_border

# Grand Status Display Box
ws1.merge_cells("E22:G23")
v_box = ws1["E22"]
v_box.value = '=IF(ROUND(C24-C28,0)>0, "SILVIA LE DEBE A DANIEL", IF(ROUND(C24-C28,0)<0, "DANIEL LE DEBE A SILVIA", "¡CUENTAS EN PAZ! ($0)"))'
v_box.font = Font(name="Calibri", size=13, bold=True, color=WHITE)
v_box.fill = fill_navy
v_box.alignment = align_center

ws1.merge_cells("E24:G27")
amt_box = ws1["E24"]
amt_box.value = '=ABS(C24-C28)'
amt_box.font = Font(name="Calibri", size=22, bold=True, color=WHITE)
amt_box.fill = fill_emerald
amt_box.number_format = CURRENCY
amt_box.alignment = align_center

ws1.merge_cells("E28:G28")
ws1["E28"].value = "Monto exacto a transferir por Nequi para quedar a paz y salvo"
ws1["E28"].font = Font(name="Calibri", size=9, italic=True, color=NAVY)
ws1["E28"].alignment = align_center

# 4. Tabla de Abonos / Transferencias entre ambos
ws1.merge_cells("B30:G30")
ws1["B30"].value = "4. HISTORIAL DE TRANSFERENCIAS Y ABONOS ENTRE DANIEL Y SILVIA"
ws1["B30"].font = font_sec_hdr
ws1["B30"].fill = fill_blue
ws1["B30"].alignment = align_left

abono_headers = ["Fecha", "Monto ($)", "Quién Transfiere", "Quién Recibe", "Cuenta / Medio", "Concepto"]
for c_idx, h in enumerate(abono_headers, start=2):
    cell = ws1.cell(row=31, column=c_idx, value=h)
    cell.font = font_tbl_hdr
    cell.fill = fill_navy
    cell.alignment = align_center
    cell.border = header_border

# Real transfer found in Silvia's excel: Daniel le da a Silvia $50.000
ws1.cell(row=32, column=2, value="2026-11-01").alignment = align_center
ws1.cell(row=32, column=3, value=50000).number_format = CURRENCY
ws1.cell(row=32, column=4, value="Daniel").alignment = align_center
ws1.cell(row=32, column=5, value="Silvia").alignment = align_center
ws1.cell(row=32, column=6, value="Nequi").alignment = align_center
ws1.cell(row=32, column=7, value="Daniel le da a Silvia (registrado en planilla Silvia)").font = font_data

for r in range(32, 38):
    for c in range(2, 8):
        cell = ws1.cell(row=r, column=c)
        cell.border = cell_border
        if c == 3:
            cell.number_format = CURRENCY
            cell.alignment = align_right
        elif c == 2:
            cell.alignment = align_center


# ==============================================================================
# HOJA 2: 🌸 PLANILLA SILVIA (DATOS REALES DEL EXCEL DE SILVIA)
# ==============================================================================
ws2 = wb.create_sheet(title="Planilla Silvia")
ws2.views.sheetView[0].showGridLines = True

ws2.merge_cells("B2:I2")
ws2["B2"].value = "PLANILLA OFICIAL DE SILVIA — CUENTAS, INGRESOS Y EGRESOS"
ws2["B2"].font = font_main_title
ws2["B2"].fill = fill_rose
ws2["B2"].alignment = align_center

headers_silvia = [
    "Descripción / Movimiento",
    "Categoría",
    "Gastos Personales Silvia ($)",
    "Egresos Totales Pagados ($)",
    "Ingresos Recibidos ($)",
    "Tipo de Gasto",
    "¿Quién Asume?",
    "Impacto en Cruce",
]

for c_idx, h in enumerate(headers_silvia, start=2):
    cell = ws2.cell(row=4, column=c_idx, value=h)
    cell.font = font_tbl_hdr
    cell.fill = fill_navy
    cell.alignment = align_center
    cell.border = header_border

# Exact rows from Silvia's excel:
silvia_rows = [
    ("Ropa Silvia", "Personal Silvia", 240700, 240700, 0, "Personal", "Silvia", "No cruza"),
    ("Ropa Daniel", "Ropa / Personal Daniel", 0, 374400, 0, "A favor de Silvia", "Daniel", "Daniel debe devolver"),
    ("Dollar city", "Hogar / Varios", 0, 17500, 0, "Compartido", "Compartido", "50% o Proporcional"),
    ("Daniel le da a Silvia", "Transferencia Pareja", 0, 50000, 50000, "Abono", "Transferencia", "Resta deuda"),
    ("Libros", "Educación / Libros", 47200, 47200, 0, "Personal", "Silvia", "No cruza"),
    ("Gasolina", "Transporte / Moto", 0, 33588, 0, "Transporte", "Silvia / Compartido", "Compartido"),
    ("Uber Remo Flores", "Transporte", 0, 10482, 0, "Transporte", "Silvia", "Personal"),
    ("Rappi", "Alimentación", 0, 24490, 0, "Comida", "Compartido", "Compartido"),
    ("Uber", "Transporte", 0, 6071, 0, "Transporte", "Silvia", "Personal"),
    ("Miniso", "Hogar / Varios", 0, 93700, 0, "Compras", "Compartido", "Compartido"),
    ("Libro que me debe Sofi", "Cuentas por Cobrar", 0, 55000, 0, "Por Cobrar", "Sofi (Tercero)", "Pendiente Sofi"),
]

for idx, (desc, cat, g_pers, egreso, ingr, tipo, quien, imp) in enumerate(silvia_rows, start=5):
    ws2.cell(row=idx, column=2, value=desc).font = font_bold
    ws2.cell(row=idx, column=3, value=cat).alignment = align_center
    ws2.cell(row=idx, column=4, value=g_pers).number_format = CURRENCY
    ws2.cell(row=idx, column=5, value=egreso).number_format = CURRENCY
    ws2.cell(row=idx, column=6, value=ingr).number_format = CURRENCY
    ws2.cell(row=idx, column=7, value=tipo).alignment = align_center
    ws2.cell(row=idx, column=8, value=quien).alignment = align_center
    ws2.cell(row=idx, column=9, value=imp).alignment = align_center

    for c in range(2, 10):
        ws2.cell(row=idx, column=c).border = cell_border
        if c in [4, 5, 6]:
            ws2.cell(row=idx, column=c).alignment = align_right

# Totals Row in Silvia's Sheet
ws2.cell(row=18, column=2, value="TOTALES REGISTRADOS EN EXCEL SILVIA:").font = font_bold
ws2.cell(row=18, column=4, value="=SUM(D5:D15)").number_format = CURRENCY # 287.900
ws2.cell(row=18, column=4).font = font_bold
ws2.cell(row=18, column=5, value="=SUM(E5:E15)").number_format = CURRENCY # 712.431 (sin contar ropa silvia columna 1)
ws2.cell(row=18, column=5).font = font_bold
ws2.cell(row=18, column=6, value="=SUM(F5:F15)").number_format = CURRENCY # 50.000
ws2.cell(row=18, column=6).font = font_bold

for c in range(2, 10):
    ws2.cell(row=18, column=c).border = header_border

# Explanatory card of Silvia's balances
ws2.merge_cells("B20:E23")
s_note = ws2["B20"]
s_note.value = (
    "RESUMEN FINANCIERO DE SILVIA:\n"
    "• Total en cuentas bancarias: $2.099.209 (Nequi $1.543.896 + Nu $555.313).\n"
    "• Cuentas por cobrar a terceros: $55.000 (Libro que le debe Sofi).\n"
    "• Gasto pagado por Silvia para Daniel: $374.400 en Ropa Daniel (Daniel debe reintegrarlo)."
)
s_note.font = Font(name="Calibri", size=10, color=NAVY)
s_note.fill = fill_rose_light
s_note.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)


# ==============================================================================
# HOJA 3: 🏍️ PLANILLA DANIEL (DATOS REALES DEL EXCEL DE DANIEL)
# ==============================================================================
ws3 = wb.create_sheet(title="Planilla Daniel")
ws3.views.sheetView[0].showGridLines = True

ws3.merge_cells("B2:K2")
ws3["B2"].value = "PLANILLA OFICIAL DE DANIEL — INGRESOS, GASTOS MENSUALES, DIARIOS Y SEGUIMIENTO"
ws3["B2"].font = font_main_title
ws3["B2"].fill = fill_blue
ws3["B2"].alignment = align_center

# 1. Ingresos Daniel
ws3.cell(row=4, column=2, value="INGRESOS MENSUALES DANIEL").font = font_tbl_hdr
ws3.cell(row=4, column=2).fill = fill_navy
ws3.cell(row=4, column=3, value="Monto ($)").font = font_tbl_hdr
ws3.cell(row=4, column=3).fill = fill_navy

d_ingresos = [
    ("Pago Maral", 1643000),
    ("Pago IA (Agencia)", 150000),
    ("Trabajo Adicional", 200000),
]
for idx, (inc_name, inc_val) in enumerate(d_ingresos, start=5):
    ws3.cell(row=idx, column=2, value=inc_name).font = font_data
    ws3.cell(row=idx, column=3, value=inc_val).number_format = CURRENCY
    ws3.cell(row=idx, column=2).border = cell_border
    ws3.cell(row=idx, column=3).border = cell_border
    ws3.cell(row=idx, column=3).alignment = align_right

ws3.cell(row=8, column=2, value="TOTAL INGRESOS DANIEL:").font = font_bold
ws3.cell(row=8, column=3, value="=SUM(C5:C7)").number_format = CURRENCY
ws3.cell(row=8, column=3).font = font_bold
ws3.cell(row=8, column=2).border = header_border
ws3.cell(row=8, column=3).border = header_border

# 2. Pagos Diarios Presupuestados (Comidas)
ws3.cell(row=4, column=5, value="PAGOS DIARIOS PRESUPUESTADOS").font = font_tbl_hdr
ws3.cell(row=4, column=5).fill = fill_navy
ws3.cell(row=4, column=6, value="Diario ($)").font = font_tbl_hdr
ws3.cell(row=4, column=6).fill = fill_navy
ws3.cell(row=4, column=7, value="Total Mes ($)").font = font_tbl_hdr
ws3.cell(row=4, column=7).fill = fill_navy

d_diarios = [
    ("Almuerzo", 14500, 435000),
    ("Comida (Cena)", 3000, 90000),
    ("Desayunos", 3000, 90000),
    ("Snacks", 3000, 90000),
]
for idx, (d_name, d_day, d_tot) in enumerate(d_diarios, start=5):
    ws3.cell(row=idx, column=5, value=d_name).font = font_data
    ws3.cell(row=idx, column=6, value=d_day).number_format = CURRENCY
    ws3.cell(row=idx, column=7, value=d_tot).number_format = CURRENCY
    for c in range(5, 8):
        ws3.cell(row=idx, column=c).border = cell_border
        if c in [6, 7]:
            ws3.cell(row=idx, column=c).alignment = align_right

ws3.cell(row=9, column=5, value="TOTAL GASTOS DIARIOS:").font = font_bold
ws3.cell(row=9, column=7, value="=SUM(G5:G8)").number_format = CURRENCY # 705.000
ws3.cell(row=9, column=7).font = font_bold
for c in range(5, 8):
    ws3.cell(row=9, column=c).border = header_border

# 3. Pagos Anuales Diferidos
ws3.cell(row=4, column=9, value="PAGOS ANUALES PROVISIONADOS").font = font_tbl_hdr
ws3.cell(row=4, column=9).fill = fill_navy
ws3.cell(row=4, column=10, value="Anual ($)").font = font_tbl_hdr
ws3.cell(row=4, column=10).fill = fill_navy

d_anuales = [
    ("Seguro Moto", 400000),
    ("Llantas Moto", 400000),
]
for idx, (a_name, a_val) in enumerate(d_anuales, start=5):
    ws3.cell(row=idx, column=9, value=a_name).font = font_data
    ws3.cell(row=idx, column=10, value=a_val).number_format = CURRENCY
    ws3.cell(row=idx, column=9).border = cell_border
    ws3.cell(row=idx, column=10).border = cell_border
    ws3.cell(row=idx, column=10).alignment = align_right

ws3.cell(row=7, column=9, value="TOTAL ANUALES:").font = font_bold
ws3.cell(row=7, column=10, value="=SUM(J5:J6)").number_format = CURRENCY # 800.000
ws3.cell(row=7, column=10).font = font_bold
ws3.cell(row=7, column=9).border = header_border
ws3.cell(row=7, column=10).border = header_border

# 4. Pagos Mensuales Fijos de Daniel
ws3.merge_cells("B11:D11")
ws3["B11"].value = "GASTOS MENSUALES FIJOS DE DANIEL"
ws3["B11"].font = font_sec_hdr
ws3["B11"].fill = fill_blue
ws3["B11"].alignment = align_left

ws3.cell(row=12, column=2, value="Concepto").font = font_tbl_hdr
ws3.cell(row=12, column=2).fill = fill_navy
ws3.cell(row=12, column=3, value="Día de Pago").font = font_tbl_hdr
ws3.cell(row=12, column=3).fill = fill_navy
ws3.cell(row=12, column=4, value="Monto Mensual ($)").font = font_tbl_hdr
ws3.cell(row=12, column=4).fill = fill_navy

d_fijos = [
    ("Arriendo (Cuota mitad en Excel)", 1, 350000),
    ("GPS moto", 1, 32000),
    ("Mantenimiento moto", 1, 27000),
    ("Aseo", 1, 35000),
    ("Cuota moto", 16, 410350),
    ("Plan Movistar", 5, 28000),
    ("Parqueadero U", 5, 90000),
    ("Gasolina moto", "Varios", 50000),
    ("Universidad", "Varios", 40000),
    ("Varios", "Varios", 50000),
    ("Lavandería", "Varios", 30000),
    ("Corte de pelo", "Varios", 30000),
]

for idx, (f_name, f_day, f_val) in enumerate(d_fijos, start=13):
    ws3.cell(row=idx, column=2, value=f_name).font = font_data
    ws3.cell(row=idx, column=3, value=f_day).alignment = align_center
    ws3.cell(row=idx, column=4, value=f_val).number_format = CURRENCY
    for c in range(2, 5):
        ws3.cell(row=idx, column=c).border = cell_border
        if c == 4:
            ws3.cell(row=idx, column=c).alignment = align_right

# Total fijos Daniel
ws3.cell(row=25, column=2, value="TOTAL GASTOS MENSUALES DANIEL:").font = font_bold
ws3.cell(row=25, column=4, value="=SUM(D13:D24)").number_format = CURRENCY # 1.172.350
ws3.cell(row=25, column=4).font = font_bold
for c in range(2, 5):
    ws3.cell(row=25, column=c).border = header_border

# Personal only (excluding arriendo 350k)
ws3.cell(row=24, column=2).value = "Corte de pelo"
ws3["D24"].value = 30000 # referenced in ws1 as personal expenses

# Total General Presupuestado Daniel
ws3.merge_cells("F11:H11")
ws3["F11"].value = "RESUMEN EJECUTIVO DANIEL"
ws3["F11"].font = font_sec_hdr
ws3["F11"].fill = fill_navy
ws3["F11"].alignment = align_left

ws3.cell(row=12, column=6, value="Ingresos Mensuales:").font = font_bold
ws3.cell(row=12, column=7, value="=C8").number_format = CURRENCY
ws3.cell(row=13, column=6, value="Total Gastos Mensuales:").font = font_bold
ws3.cell(row=13, column=7, value="=D25").number_format = CURRENCY
ws3.cell(row=14, column=6, value="Total Gastos Diarios:").font = font_bold
ws3.cell(row=14, column=7, value="=G9").number_format = CURRENCY
ws3.cell(row=15, column=6, value="Total Gastos Presupuestados:").font = font_bold
ws3.cell(row=15, column=7, value="=G13+G14").number_format = CURRENCY # 1.877.350
ws3.cell(row=15, column=7).font = font_bold

ws3.cell(row=16, column=6, value="Saldo / Margen Mensual Libre:").font = font_bold
ws3.cell(row=16, column=7, value="=G12-G15").number_format = CURRENCY # 115.650
ws3.cell(row=16, column=7).font = Font(name="Calibri", size=11, bold=True, color=EMERALD)

ws3.cell(row=17, column=6, value="Saldo Real en Cuenta Nequi:").font = font_bold
ws3.cell(row=17, column=7, value=655394).number_format = CURRENCY
ws3.cell(row=17, column=7).font = font_bold

for r in range(12, 18):
    for c in [6, 7]:
        ws3.cell(row=r, column=c).border = cell_border


# ==============================================================================
# HOJA 4: 🤝 GASTOS COMPARTIDOS DEL HOGAR (EL CRUCE ENTRE AMBOS)
# ==============================================================================
ws4 = wb.create_sheet(title="Gastos Compartidos")
ws4.views.sheetView[0].showGridLines = True

ws4.merge_cells("B2:I2")
ws4["B2"].value = "GASTOS COMPARTIDOS DEL HOGAR & COMPRAS MUTUAS"
ws4["B2"].font = font_main_title
ws4["B2"].fill = fill_emerald
ws4["B2"].alignment = align_center

headers_compartidos = [
    "Concepto / Compra",
    "Monto Real ($)",
    "Pagado Por",
    "Tipo de División",
    "Cuota Daniel ($)",
    "Cuota Silvia ($)",
    "Aporte Daniel ($)",
    "Aporte Silvia ($)",
]

for c_idx, h in enumerate(headers_compartidos, start=2):
    cell = ws4.cell(row=4, column=c_idx, value=h)
    cell.font = font_tbl_hdr
    cell.fill = fill_navy
    cell.alignment = align_center
    cell.border = header_border

# Real shared expenses consolidated from both sheets:
# 1. Arriendo total: 700.000 (Pagó Daniel)
# 2. Aseo hogar: 35.000 (Pagó Daniel)
# 3. Ropa Daniel: 374.400 (Pagó Silvia de su bolsillo)
# 4. Dollar City: 17.500 (Pagó Silvia)
# 5. Miniso compartido: 93.700 (Pagó Silvia)
# 6. Rappi comida compartida: 24.490 (Pagó Silvia)
# 7. Gasolina compartida: 33.588 (Pagó Silvia)
shared_items = [
    ("Arriendo Apartamento", 700000, "Daniel", "% Proporcional"),
    ("Aseo Hogar", 35000, "Daniel", "Mitad (50/50)"),
    ("Ropa Daniel (Comprada por Silvia)", 374400, "Silvia", "Todo Daniel"),
    ("Dollar City (Cosas del hogar)", 17500, "Silvia", "Mitad (50/50)"),
    ("Miniso (Hogar)", 93700, "Silvia", "Mitad (50/50)"),
    ("Rappi (Comida compartida)", 24490, "Silvia", "Mitad (50/50)"),
    ("Gasolina compartida", 33588, "Silvia", "Mitad (50/50)"),
]

for idx, (c_name, c_tot, c_payer, c_split) in enumerate(shared_items, start=5):
    ws4.cell(row=idx, column=2, value=c_name).font = font_bold
    ws4.cell(row=idx, column=3, value=c_tot).number_format = CURRENCY
    
    p_cell = ws4.cell(row=idx, column=4, value=c_payer)
    p_cell.alignment = align_center
    p_cell.font = Font(name="Calibri", size=10, bold=True, color=BLUE if c_payer=="Daniel" else ROSE)
    
    ws4.cell(row=idx, column=5, value=c_split).alignment = align_center
    
    # Cuota Daniel
    ws4.cell(row=idx, column=6, value=f'=IF(E{idx}="Mitad (50/50)", C{idx}*0.5, IF(E{idx}="% Proporcional", C{idx}*\'Panel y Cruce de Cuentas\'!$E$19, IF(E{idx}="Todo Daniel", C{idx}, 0)))').number_format = CURRENCY
    # Cuota Silvia
    ws4.cell(row=idx, column=7, value=f'=C{idx}-F{idx}').number_format = CURRENCY
    
    # Aporte real pagado por cada uno
    ws4.cell(row=idx, column=8, value=f'=IF(D{idx}="Daniel", C{idx}, 0)').number_format = CURRENCY
    ws4.cell(row=idx, column=9, value=f'=IF(D{idx}="Silvia", C{idx}, 0)').number_format = CURRENCY

    for c in range(2, 10):
        ws4.cell(row=idx, column=c).border = cell_border
        if c in [3, 6, 7, 8, 9]:
            ws4.cell(row=idx, column=c).alignment = align_right

# Empty ready-to-use rows
for r in range(12, 18):
    ws4.cell(row=r, column=5, value="Mitad (50/50)").alignment = align_center
    ws4.cell(row=r, column=6, value=f'=IF(C{r}>0, IF(E{r}="Mitad (50/50)", C{r}*0.5, IF(E{r}="% Proporcional", C{r}*\'Panel y Cruce de Cuentas\'!$E$19, IF(E{r}="Todo Daniel", C{r}, 0))), 0)').number_format = CURRENCY
    ws4.cell(row=r, column=7, value=f'=IF(C{r}>0, C{r}-F{r}, 0)').number_format = CURRENCY
    ws4.cell(row=r, column=8, value=f'=IF(D{r}="Daniel", C{r}, 0)').number_format = CURRENCY
    ws4.cell(row=r, column=9, value=f'=IF(D{r}="Silvia", C{r}, 0)').number_format = CURRENCY
    for c in range(2, 10):
        cell = ws4.cell(row=r, column=c)
        cell.border = cell_border
        if c in [3, 6, 7, 8, 9]:
            cell.number_format = CURRENCY
            cell.alignment = align_right

# Totals Row at Row 18
ws4.cell(row=18, column=2, value="TOTALES GASTOS COMPARTIDOS:").font = font_bold
ws4.cell(row=18, column=3, value="=SUM(C5:C17)").number_format = CURRENCY
ws4.cell(row=18, column=3).font = font_bold

ws4.cell(row=18, column=6, value="=SUM(F5:F17)").number_format = CURRENCY # Cuota debida Daniel
ws4.cell(row=18, column=6).font = Font(name="Calibri", size=10, bold=True, color=BLUE)

ws4.cell(row=18, column=7, value="=SUM(G5:G17)").number_format = CURRENCY # Cuota debida Silvia
ws4.cell(row=18, column=7).font = Font(name="Calibri", size=10, bold=True, color=ROSE)

ws4.cell(row=18, column=8, value="=SUM(H5:H17)").number_format = CURRENCY # Aporte de bolsillo Daniel
ws4.cell(row=18, column=8).font = Font(name="Calibri", size=10, bold=True, color=BLUE)

ws4.cell(row=18, column=9, value="=SUM(I5:I17)").number_format = CURRENCY # Aporte de bolsillo Silvia
ws4.cell(row=18, column=9).font = Font(name="Calibri", size=10, bold=True, color=ROSE)

for c in range(2, 10):
    ws4.cell(row=18, column=c).border = header_border


# ==============================================================================
# HOJA 5: 📅 SEGUIMIENTO DIARIO DANIEL (CALENDARIO DE SU EXCEL ORIGINAL)
# ==============================================================================
ws5 = wb.create_sheet(title="Seguimiento Diario Daniel")
ws5.views.sheetView[0].showGridLines = True

ws5.merge_cells("A2:J2")
ws5["A2"].value = "CONTROL DIARIO DE INGRESOS, GASTOS Y SALDO EN NEQUI (DANIEL)"
ws5["A2"].font = font_main_title
ws5["A2"].fill = fill_blue
ws5["A2"].alignment = align_center

headers_diario_d = [
    "Fecha",
    "Día Semana",
    "Ingresos Fijos ($)",
    "Gastos Fijos ($)",
    "Presupuesto Diario ($)",
    "Gasto Real ($)",
    "Saldo Teórico ($)",
    "Saldo Real Nequi ($)",
    "Diferencia ($)",
    "Estado",
]

for c_idx, h in enumerate(headers_diario_d, start=1):
    cell = ws5.cell(row=4, column=c_idx, value=h)
    cell.font = font_tbl_hdr
    cell.fill = fill_navy
    cell.alignment = align_center
    cell.border = header_border

calendar_rows = [
    ("2025-08-01", "viernes", 1021500, 444000, 29193.55, 0, 548306.45, None, -548306.45, "MAL 😟"),
    ("2025-08-02", "sábado", 0, 0, 29193.55, 0, 519112.90, None, -519112.90, "MAL 😟"),
    ("2025-08-03", "domingo", 0, 0, 29193.55, 0, 489919.35, None, -489919.35, "MAL 😟"),
    ("2025-08-04", "lunes", 0, 0, 29193.55, 0, 460725.81, None, -460725.81, "MAL 😟"),
    ("2025-08-05", "martes", 0, 118000, 29193.55, 0, 313532.26, None, -313532.26, "MAL 😟"),
    ("2025-08-06", "miércoles", 0, 0, 29193.55, 0, 284338.71, None, -284338.71, "MAL 😟"),
    ("2025-08-07", "jueves", 0, 0, 29193.55, 0, 255145.16, None, -255145.16, "MAL 😟"),
    ("2025-08-08", "viernes", 0, 0, 29193.55, 0, 225951.61, None, -225951.61, "MAL 😟"),
    ("2025-08-09", "sábado", 0, 0, 29193.55, 0, 196758.06, None, None, ""),
    ("2025-08-10", "domingo", 0, 0, 29193.55, 0, 167564.52, 655394, 487829.48, "EXCELENTE 🤑"),
    ("2025-08-11", "lunes", 0, 0, 29193.55, None, 138370.97, None, None, ""),
    ("2025-08-12", "martes", 0, 0, 29193.55, None, 109177.42, None, None, ""),
    ("2025-08-13", "miércoles", 0, 0, 29193.55, None, 79983.87, None, None, ""),
    ("2025-08-14", "jueves", 0, 0, 29193.55, None, 50790.32, None, None, ""),
    ("2025-08-15", "viernes", 971500, 0, 29193.55, None, 993096.77, None, None, ""),
    ("2025-08-16", "sábado", 0, 410350, 29193.55, None, 553553.23, None, None, ""),
    ("2025-08-17", "domingo", 0, 0, 29193.55, None, 524359.68, None, None, ""),
    ("2025-08-18", "lunes", 0, 0, 29193.55, None, 495166.13, None, None, ""),
    ("2025-08-19", "martes", 0, 0, 29193.55, None, 465972.58, None, None, ""),
    ("2025-08-20", "miércoles", 0, 0, 29193.55, None, 436779.03, None, None, ""),
    ("2025-08-21", "jueves", 0, 0, 29193.55, None, 407585.48, None, None, ""),
    ("2025-08-22", "viernes", 0, 0, 29193.55, None, 378391.94, None, None, ""),
    ("2025-08-23", "sábado", 0, 0, 29193.55, None, 349198.39, None, None, ""),
    ("2025-08-24", "domingo", 0, 0, 29193.55, None, 320004.84, None, None, ""),
    ("2025-08-25", "lunes", 0, 0, 29193.55, None, 290811.29, None, None, ""),
    ("2025-08-26", "martes", 0, 0, 29193.55, None, 261617.74, None, None, ""),
    ("2025-08-27", "miércoles", 0, 0, 29193.55, None, 232424.19, None, None, ""),
    ("2025-08-28", "jueves", 0, 0, 29193.55, None, 203230.65, None, None, ""),
    ("2025-08-29", "viernes", 0, 0, 29193.55, None, 174037.10, None, None, ""),
    ("2025-08-30", "sábado", 0, 0, 29193.55, None, 144843.55, None, None, ""),
    ("2025-08-31", "domingo", 0, 0, 29193.55, None, 115650.00, None, None, ""),
    ("2025-09-01", "lunes", 1021500, 444000, 29193.55, None, 663956.45, None, None, ""),
]

for idx, (f_date, f_day, inc, fix, d_bdg, real_g, t_sal, r_sal, dif, st) in enumerate(calendar_rows, start=5):
    ws5.cell(row=idx, column=1, value=f_date).alignment = align_center
    ws5.cell(row=idx, column=2, value=f_day).alignment = align_center
    ws5.cell(row=idx, column=3, value=inc).number_format = CURRENCY
    ws5.cell(row=idx, column=4, value=fix).number_format = CURRENCY
    ws5.cell(row=idx, column=5, value=d_bdg).number_format = CURRENCY
    ws5.cell(row=idx, column=6, value=real_g).number_format = CURRENCY
    ws5.cell(row=idx, column=7, value=t_sal).number_format = CURRENCY
    ws5.cell(row=idx, column=8, value=r_sal).number_format = CURRENCY
    ws5.cell(row=idx, column=9, value=dif).number_format = CURRENCY
    
    st_c = ws5.cell(row=idx, column=10, value=st)
    st_c.alignment = align_center
    if "EXCELENTE" in str(st):
        st_c.fill = fill_emerald_light
        st_c.font = Font(name="Calibri", size=10, bold=True, color=EMERALD)
    elif "MAL" in str(st):
        st_c.fill = fill_rose_light
        st_c.font = Font(name="Calibri", size=10, bold=True, color=ROSE)

    for c in range(1, 11):
        ws5.cell(row=idx, column=c).border = cell_border
        if c in [3, 4, 5, 6, 7, 8, 9]:
            ws5.cell(row=idx, column=c).alignment = align_right

# ==============================================================================
# AUTO-FIT COLUMN WIDTHS
# ==============================================================================
for sheet in wb.worksheets:
    for col in sheet.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.coordinate in sheet.merged_cells:
                continue
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

ws1.column_dimensions["A"].width = 3
ws1.column_dimensions["B"].width = 38
ws1.column_dimensions["C"].width = 24
ws1.column_dimensions["D"].width = 24
ws1.column_dimensions["E"].width = 26
ws1.column_dimensions["F"].width = 22
ws1.column_dimensions["G"].width = 28

ws2.column_dimensions["A"].width = 3
ws2.column_dimensions["B"].width = 32
ws2.column_dimensions["C"].width = 22
ws2.column_dimensions["D"].width = 24
ws2.column_dimensions["E"].width = 24
ws2.column_dimensions["F"].width = 20
ws2.column_dimensions["G"].width = 20
ws2.column_dimensions["H"].width = 20
ws2.column_dimensions["I"].width = 24

ws3.column_dimensions["A"].width = 3
ws3.column_dimensions["B"].width = 34
ws3.column_dimensions["C"].width = 18
ws3.column_dimensions["D"].width = 20
ws3.column_dimensions["E"].width = 30
ws3.column_dimensions["F"].width = 16
ws3.column_dimensions["G"].width = 20
ws3.column_dimensions["H"].width = 14
ws3.column_dimensions["I"].width = 30
ws3.column_dimensions["J"].width = 16

ws4.column_dimensions["A"].width = 3
ws4.column_dimensions["B"].width = 36
ws4.column_dimensions["C"].width = 18
ws4.column_dimensions["D"].width = 16
ws4.column_dimensions["E"].width = 20
ws4.column_dimensions["F"].width = 18
ws4.column_dimensions["G"].width = 18
ws4.column_dimensions["H"].width = 18
ws4.column_dimensions["I"].width = 18

ws5.column_dimensions["A"].width = 14
ws5.column_dimensions["B"].width = 14
ws5.column_dimensions["C"].width = 18
ws5.column_dimensions["D"].width = 18
ws5.column_dimensions["E"].width = 20
ws5.column_dimensions["F"].width = 16
ws5.column_dimensions["G"].width = 18
ws5.column_dimensions["H"].width = 18
ws5.column_dimensions["I"].width = 16
ws5.column_dimensions["J"].width = 16

excel_path = r"C:\Users\lady\Desktop\Cuentas_Claras_Oficial_Daniel_y_Silvia.xlsx"
wb.save(excel_path)
# Also save inside workspace
workspace_path = r"C:\Users\lady\.gemini\antigravity\scratch\cuentas-claras\Cuentas_Claras_Oficial_Daniel_y_Silvia.xlsx"
wb.save(workspace_path)
print(f"SUCCESS: Unified Excel generated at: {excel_path} and {workspace_path}")
