import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Color Palette
EMERALD = "10B981"
EMERALD_DARK = "065F46"
EMERALD_LIGHT = "D1FAE5"
DANIEL_COLOR = "2563EB"
DANIEL_LIGHT = "DBEAFE"
SILVIA_COLOR = "E11D48"
SILVIA_LIGHT = "FFE4E6"
DARK_GRAY = "1E293B"
GRAY_TEXT = "475569"
LIGHT_GRAY = "F8FAFC"
BORDER_GRAY = "CBD5E1"
WHITE = "FFFFFF"
GOLD = "D97706"
GOLD_LIGHT = "FEF3C7"

# Styles helper
thin_side = Side(border_style="thin", color=BORDER_GRAY)
thick_bottom = Side(border_style="medium", color=DARK_GRAY)
border_cell = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
border_header = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thick_bottom)

font_title = Font(name="Calibri", size=16, bold=True, color=WHITE)
font_subtitle = Font(name="Calibri", size=10, italic=True, color="E2E8F0")
font_sec_hdr = Font(name="Calibri", size=12, bold=True, color=DARK_GRAY)
font_tbl_hdr = Font(name="Calibri", size=11, bold=True, color=WHITE)
font_data = Font(name="Calibri", size=11, color=DARK_GRAY)
font_bold = Font(name="Calibri", size=11, bold=True, color=DARK_GRAY)
font_highlight = Font(name="Calibri", size=12, bold=True, color=EMERALD_DARK)
font_alert = Font(name="Calibri", size=12, bold=True, color=SILVIA_COLOR)

fill_emerald_hdr = PatternFill(start_color=EMERALD, end_color=EMERALD, fill_type="solid")
fill_emerald_dark = PatternFill(start_color=EMERALD_DARK, end_color=EMERALD_DARK, fill_type="solid")
fill_daniel_hdr = PatternFill(start_color=DANIEL_COLOR, end_color=DANIEL_COLOR, fill_type="solid")
fill_silvia_hdr = PatternFill(start_color=SILVIA_COLOR, end_color=SILVIA_COLOR, fill_type="solid")
fill_dark_hdr = PatternFill(start_color=DARK_GRAY, end_color=DARK_GRAY, fill_type="solid")
fill_light_row = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")
fill_emerald_light = PatternFill(start_color=EMERALD_LIGHT, end_color=EMERALD_LIGHT, fill_type="solid")
fill_daniel_light = PatternFill(start_color=DANIEL_LIGHT, end_color=DANIEL_LIGHT, fill_type="solid")
fill_silvia_light = PatternFill(start_color=SILVIA_LIGHT, end_color=SILVIA_LIGHT, fill_type="solid")
fill_gold_light = PatternFill(start_color=GOLD_LIGHT, end_color=GOLD_LIGHT, fill_type="solid")

align_center = Alignment(horizontal="center", vertical="center")
align_left = Alignment(horizontal="left", vertical="center")
align_right = Alignment(horizontal="right", vertical="center")
align_wrap = Alignment(horizontal="left", vertical="center", wrap_text=True)

CURRENCY_FORMAT = '"$"#,##0'
PERCENT_FORMAT = '0.0%'
DATE_FORMAT = 'yyyy-mm-dd'

# ==========================================================
# 1. HOJA: PANEL DE CONTROL Y BALANCE
# ==========================================================
ws1 = wb.create_sheet(title="Panel de Control")
ws1.views.sheetView[0].showGridLines = True

# Banner
ws1.merge_cells("B2:G2")
banner = ws1["B2"]
banner.value = "CUENTAS CLARAS — DANIEL & SILVIA"
banner.font = font_title
banner.fill = fill_dark_hdr
banner.alignment = align_center

ws1.merge_cells("B3:G3")
sub = ws1["B3"]
sub.value = "Sistema Financiero Compartido · Calculadora Proporcional · Balance de Deudas en Tiempo Real"
sub.font = font_subtitle
sub.fill = fill_dark_hdr
sub.alignment = align_center

# Section 1: Calculadora Proporcional por Ingresos
ws1.merge_cells("B5:G5")
s1_hdr = ws1["B5"]
s1_hdr.value = "1. CALCULADORA DE DIVISIÓN PROPORCIONAL POR INGRESOS"
s1_hdr.font = Font(name="Calibri", size=12, bold=True, color=WHITE)
s1_hdr.fill = fill_emerald_dark
s1_hdr.alignment = align_left

headers_s1 = ["Concepto / Variable", "Daniel", "Silvia", "Total Combinado", "Proporción Daniel (%)", "Proporción Silvia (%)"]
for col_idx, h in enumerate(headers_s1, start=2):
    cell = ws1.cell(row=6, column=col_idx, value=h)
    cell.font = font_tbl_hdr
    cell.fill = fill_emerald_hdr
    cell.alignment = align_center
    cell.border = border_header

# Row 7: Ingresos Mensuales
ws1.cell(row=7, column=2, value="Ingresos Mensuales Netos").font = font_bold
ws1.cell(row=7, column=3, value=1993000).number_format = CURRENCY_FORMAT # Daniel
ws1.cell(row=7, column=4, value=0).number_format = CURRENCY_FORMAT       # Silvia (editable)
ws1.cell(row=7, column=5, value="=C7+D7").number_format = CURRENCY_FORMAT
ws1.cell(row=7, column=6, value="=IF(E7>0, C7/E7, 0.5)").number_format = PERCENT_FORMAT
ws1.cell(row=7, column=7, value="=IF(E7>0, D7/E7, 0.5)").number_format = PERCENT_FORMAT

# Row 8: Gastos Personales Ineludibles
ws1.cell(row=8, column=2, value="Gastos Personales Ineludibles (Moto, Deudas, Estudio)").font = font_bold
ws1.cell(row=8, column=3, value=747350).number_format = CURRENCY_FORMAT
ws1.cell(row=8, column=4, value=0).number_format = CURRENCY_FORMAT
ws1.cell(row=8, column=5, value="=C8+D8").number_format = CURRENCY_FORMAT
ws1.cell(row=8, column=6, value="-").alignment = align_center
ws1.cell(row=8, column=7, value="-").alignment = align_center

# Row 9: Capacidad Libre Real
ws1.cell(row=9, column=2, value="Capacidad Real Libre (Ingreso - Gastos Personales)").font = font_bold
ws1.cell(row=9, column=3, value="=MAX(0, C7-C8)").number_format = CURRENCY_FORMAT
ws1.cell(row=9, column=4, value="=MAX(0, D7-D8)").number_format = CURRENCY_FORMAT
ws1.cell(row=9, column=5, value="=C9+D9").number_format = CURRENCY_FORMAT
ws1.cell(row=9, column=6, value="=IF(E9>0, C9/E9, 0.5)").number_format = PERCENT_FORMAT
ws1.cell(row=9, column=7, value="=IF(E9>0, D9/E9, 0.5)").number_format = PERCENT_FORMAT

# Formatting rows 7-9
for r in range(7, 10):
    for c in range(2, 8):
        cell = ws1.cell(row=r, column=c)
        cell.border = border_cell
        if c in [3, 4, 5]:
            cell.alignment = align_right
        elif c in [6, 7] and cell.value != "-":
            cell.alignment = align_center

# Active Ratio Box
ws1.merge_cells("B11:D11")
ws1.cell(row=11, column=2, value="PROPORCIÓN ACTIVA ELEGIDA PARA EL HOGAR:").font = font_bold
ws1.cell(row=11, column=2).alignment = align_right

cell_ratio_d = ws1.cell(row=11, column=5, value="=F7") # Defaults to gross income proportion
cell_ratio_d.font = Font(name="Calibri", size=13, bold=True, color=DANIEL_COLOR)
cell_ratio_d.fill = fill_daniel_light
cell_ratio_d.number_format = PERCENT_FORMAT
cell_ratio_d.alignment = align_center
cell_ratio_d.border = border_cell

cell_ratio_s = ws1.cell(row=11, column=6, value="=1-E11")
cell_ratio_s.font = Font(name="Calibri", size=13, bold=True, color=SILVIA_COLOR)
cell_ratio_s.fill = fill_silvia_light
cell_ratio_s.number_format = PERCENT_FORMAT
cell_ratio_s.alignment = align_center
cell_ratio_s.border = border_cell

ws1.cell(row=11, column=7, value="Daniel % / Silvia %").font = Font(name="Calibri", size=9, italic=True, color=GRAY_TEXT)

# Simulation example
ws1.merge_cells("B13:C13")
ws1.cell(row=13, column=2, value="Ejemplo con Arriendo Total ($700.000):").font = font_bold
ws1.cell(row=13, column=4, value=700000).number_format = CURRENCY_FORMAT
ws1.cell(row=13, column=5, value='="Daniel aporta: " & TEXT(D13*E11, "$#,##0")').font = Font(name="Calibri", size=11, bold=True, color=DANIEL_COLOR)
ws1.cell(row=13, column=6, value='="Silvia aporta: " & TEXT(D13*F11, "$#,##0")').font = Font(name="Calibri", size=11, bold=True, color=SILVIA_COLOR)
ws1.merge_cells("F13:G13")

# Section 2: Estado de Deudas y Balance en Vivo
ws1.merge_cells("B15:G15")
s2_hdr = ws1["B15"]
s2_hdr.value = "2. BALANCE ENTRE PAREJA — ¿QUIÉN LE DEBE A QUIÉN EN TIEMPO REAL?"
s2_hdr.font = Font(name="Calibri", size=12, bold=True, color=WHITE)
s2_hdr.fill = fill_dark_hdr
s2_hdr.alignment = align_left

bal_rows = [
    ("Total pagado por Daniel (Salió de su dinero)", "='Registro Gastos'!L35", DANIEL_COLOR),
    ("Total que le correspondía asumir a Daniel", "='Registro Gastos'!J35", DANIEL_COLOR),
    ("Balance Neto Daniel (Aportado - Su Cuota)", "=C16-C17", DANIEL_COLOR),
    ("Total pagado por Silvia (Salió de su dinero)", "='Registro Gastos'!M35", SILVIA_COLOR),
    ("Total que le correspondía asumir a Silvia", "='Registro Gastos'!K35", SILVIA_COLOR),
    ("Balance Neto Silvia (Aportado - Su Cuota)", "=C19-C20", SILVIA_COLOR),
    ("Abonos / Deudas Saldadas Registradas", "=SUM(C28:C35)", GRAY_TEXT),
]

for idx, (label, formula, col_color) in enumerate(bal_rows, start=16):
    ws1.cell(row=idx, column=2, value=label).font = font_bold
    c_val = ws1.cell(row=idx, column=3, value=formula)
    c_val.number_format = CURRENCY_FORMAT
    c_val.alignment = align_right
    c_val.font = Font(name="Calibri", size=11, bold=True, color=col_color)
    c_val.border = border_cell
    ws1.cell(row=idx, column=2).border = border_cell

# Big Status Callout
ws1.merge_cells("E16:G17")
status_title = ws1["E16"]
status_title.value = '=IF(ROUND(C18-C22,0)>0, "SILVIA LE DEBE A DANIEL", IF(ROUND(C18-C22,0)<0, "DANIEL LE DEBE A SILVIA", "¡CUENTAS EN PAZ! ($0)"))'
status_title.font = Font(name="Calibri", size=13, bold=True, color=WHITE)
status_title.fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
status_title.alignment = align_center

ws1.merge_cells("E18:G21")
status_val = ws1["E18"]
status_val.value = '=ABS(C18-C22)'
status_val.font = Font(name="Calibri", size=22, bold=True, color=WHITE)
status_val.fill = fill_emerald_dark
status_val.number_format = CURRENCY_FORMAT
status_val.alignment = align_center

ws1.merge_cells("E22:G22")
ws1["E22"].value = "Monto exacto para transferir y quedar en ceros"
ws1["E22"].font = Font(name="Calibri", size=9, italic=True, color=GRAY_TEXT)
ws1["E22"].alignment = align_center

# Section 3: Registro de Abonos (Saldar Cuentas)
ws1.merge_cells("B24:G24")
s3_hdr = ws1["B24"]
s3_hdr.value = "3. REGISTRO DE TRANSFERENCIAS PARA SALDAR DEUDAS (ABONOS)"
s3_hdr.font = Font(name="Calibri", size=11, bold=True, color=WHITE)
s3_hdr.fill = fill_emerald_hdr
s3_hdr.alignment = align_left

settle_headers = ["Fecha", "Monto Abonado ($)", "Quién Transfirió", "Quién Recibió", "Cuenta / Método", "Comentarios"]
for c_idx, h in enumerate(settle_headers, start=2):
    cell = ws1.cell(row=25, column=c_idx, value=h)
    cell.font = font_tbl_hdr
    cell.fill = fill_dark_hdr
    cell.alignment = align_center
    cell.border = border_header

# Empty rows for user to log debt payments
for r in range(26, 32):
    for c in range(2, 8):
        cell = ws1.cell(row=r, column=c)
        cell.border = border_cell
        if c == 2:
            cell.number_format = DATE_FORMAT
            cell.alignment = align_center
        elif c == 3:
            cell.number_format = CURRENCY_FORMAT
            cell.alignment = align_right
        else:
            cell.alignment = align_left

ws1.cell(row=26, column=2, value="2026-11-01")
ws1.cell(row=26, column=3, value=0)
ws1.cell(row=26, column=4, value="Silvia")
ws1.cell(row=26, column=5, value="Daniel")
ws1.cell(row=26, column=6, value="Nequi -> Nequi")
ws1.cell(row=26, column=7, value="Ejemplo de abono registrado")


# ==========================================================
# 2. HOJA: GASTOS FIJOS DEL HOGAR
# ==========================================================
ws2 = wb.create_sheet(title="Gastos Fijos")
ws2.views.sheetView[0].showGridLines = True

ws2.merge_cells("B2:I2")
ws2["B2"].value = "GASTOS FIJOS RECURRENTES DEL HOGAR (MENSUALES)"
ws2["B2"].font = font_title
ws2["B2"].fill = fill_emerald_dark
ws2["B2"].alignment = align_center

ws2.merge_cells("B3:I3")
ws2["B3"].value = "Presupuesto mensual fijo, días de vencimiento y distribución de cuotas"
ws2["B3"].font = font_subtitle
ws2["B3"].fill = fill_emerald_dark
ws2["B3"].alignment = align_center

headers_fijos = [
    "Concepto / Gasto Fijo",
    "Monto Mensual ($)",
    "Día de Pago",
    "Quién Paga",
    "Tipo de División",
    "Cuota Daniel ($)",
    "Cuota Silvia ($)",
    "Estado Mes",
]

for col_idx, h in enumerate(headers_fijos, start=2):
    cell = ws2.cell(row=5, column=col_idx, value=h)
    cell.font = font_tbl_hdr
    cell.fill = fill_emerald_hdr
    cell.alignment = align_center
    cell.border = border_header

recurring_data = [
    ("Arriendo Apartamento", 700000, 1, "Daniel", "% Proporcional", "Pagado"),
    ("Internet Hogar (Fibra)", 95000, 5, "Daniel", "% Proporcional", "Pendiente"),
    ("Servicios Públicos (Luz y Agua)", 180000, 15, "Silvia", "% Proporcional", "Pendiente"),
    ("Aseo Hogar", 35000, 1, "Daniel", "Mitad (50/50)", "Pendiente"),
]

for idx, (title, amt, day, payer, split, status) in enumerate(recurring_data, start=6):
    ws2.cell(row=idx, column=2, value=title).font = font_bold
    ws2.cell(row=idx, column=3, value=amt).number_format = CURRENCY_FORMAT
    ws2.cell(row=idx, column=4, value=day).alignment = align_center
    ws2.cell(row=idx, column=5, value=payer).alignment = align_center
    ws2.cell(row=idx, column=6, value=split).alignment = align_center
    
    # Cuota Daniel formula
    ws2.cell(row=idx, column=7, value=f'=IF(F{idx}="Mitad (50/50)", C{idx}*0.5, IF(F{idx}="% Proporcional", C{idx}*\'Panel de Control\'!$E$11, IF(F{idx}="Todo Daniel", C{idx}, 0)))').number_format = CURRENCY_FORMAT
    # Cuota Silvia formula
    ws2.cell(row=idx, column=8, value=f'=C{idx}-G{idx}').number_format = CURRENCY_FORMAT
    
    st_cell = ws2.cell(row=idx, column=9, value=status)
    st_cell.alignment = align_center
    if status == "Pagado":
        st_cell.fill = fill_emerald_light
        st_cell.font = Font(name="Calibri", size=11, bold=True, color=EMERALD_DARK)
    else:
        st_cell.fill = fill_gold_light
        st_cell.font = Font(name="Calibri", size=11, bold=True, color=GOLD)

    for c in range(2, 10):
        ws2.cell(row=idx, column=c).border = border_cell

# Total Row
tot_r = len(recurring_data) + 6
ws2.cell(row=tot_r, column=2, value="TOTAL GASTOS FIJOS DEL HOGAR:").font = font_bold
ws2.cell(row=tot_r, column=3, value=f"=SUM(C6:C{tot_r-1})").number_format = CURRENCY_FORMAT
ws2.cell(row=tot_r, column=3).font = font_bold
ws2.cell(row=tot_r, column=7, value=f"=SUM(G6:G{tot_r-1})").number_format = CURRENCY_FORMAT
ws2.cell(row=tot_r, column=7).font = Font(name="Calibri", size=11, bold=True, color=DANIEL_COLOR)
ws2.cell(row=tot_r, column=8, value=f"=SUM(H6:H{tot_r-1})").number_format = CURRENCY_FORMAT
ws2.cell(row=tot_r, column=8).font = Font(name="Calibri", size=11, bold=True, color=SILVIA_COLOR)

for c in range(2, 10):
    ws2.cell(row=tot_r, column=c).border = border_header


# ==========================================================
# 3. HOJA: REGISTRO DIARIO DE GASTOS
# ==========================================================
ws3 = wb.create_sheet(title="Registro Gastos")
ws3.views.sheetView[0].showGridLines = True

ws3.merge_cells("A2:N2")
ws3["A2"].value = "REGISTRO DETALLADO DE GASTOS DIARIOS Y COMPARTIDOS"
ws3["A2"].font = font_title
ws3["A2"].fill = fill_dark_hdr
ws3["A2"].alignment = align_center

headers_gastos = [
    "#",
    "Fecha",
    "Descripción / Establecimiento",
    "Categoría",
    "Pagado Por",
    "Cuenta / Medio",
    "Monto Base ($)",
    "Recargo 3%?",
    "Monto Total ($)",
    "Tipo División",
    "Cuota Daniel ($)",
    "Cuota Silvia ($)",
    "Aporte Daniel ($)",
    "Aporte Silvia ($)",
]

for col_idx, h in enumerate(headers_gastos, start=1):
    cell = ws3.cell(row=4, column=col_idx, value=h)
    cell.font = font_tbl_hdr
    cell.fill = fill_dark_hdr
    cell.alignment = align_center
    cell.border = border_header

# Initial real sample expenses from the system
gastos_iniciales = [
    (1, "2026-11-01", "ARRIENDO APARTAMENTO", "Vivienda", "Daniel", "Nequi", 700000, "NO", "% Proporcional"),
    (2, "2026-11-03", "Pollo de cacareo", "Alimentacion", "Daniel", "Nequi", 19000, "NO", "Mitad (50/50)"),
    (3, "2026-11-04", "Discoteca / Salida", "Ocio", "Daniel", "Nequi", 176000, "NO", "Mitad (50/50)"),
    (4, "2026-11-04", "Casa china pesos", "Alimentacion", "Daniel", "Nequi", 54000, "NO", "Mitad (50/50)"),
    (5, "2026-11-04", "Frugger pesos (Mercado)", "Alimentacion", "Daniel", "Nequi", 36400, "NO", "Mitad (50/50)"),
    (6, "2026-11-05", "Internet Hogar Fibra", "Servicios", "Daniel", "Nu Debito", 95000, "NO", "% Proporcional"),
]

for idx, (num, f_date, desc, cat, payer, acc, base_amt, recargo, split) in enumerate(gastos_iniciales, start=5):
    ws3.cell(row=idx, column=1, value=num).alignment = align_center
    ws3.cell(row=idx, column=2, value=f_date).alignment = align_center
    ws3.cell(row=idx, column=3, value=desc).font = font_bold
    ws3.cell(row=idx, column=4, value=cat).alignment = align_center
    
    p_cell = ws3.cell(row=idx, column=5, value=payer)
    p_cell.alignment = align_center
    p_cell.font = Font(name="Calibri", size=11, bold=True, color=DANIEL_COLOR if payer=="Daniel" else SILVIA_COLOR)
    
    ws3.cell(row=idx, column=6, value=acc).alignment = align_center
    ws3.cell(row=idx, column=7, value=base_amt).number_format = CURRENCY_FORMAT
    ws3.cell(row=idx, column=8, value=recargo).alignment = align_center
    
    # Total with surcharge
    ws3.cell(row=idx, column=9, value=f'=G{idx}*IF(H{idx}="SÍ", 1.03, 1)').number_format = CURRENCY_FORMAT
    ws3.cell(row=idx, column=9).font = font_bold
    
    ws3.cell(row=idx, column=10, value=split).alignment = align_center
    
    # Cuota Daniel
    ws3.cell(row=idx, column=11, value=f'=IF(J{idx}="Mitad (50/50)", I{idx}*0.5, IF(J{idx}="% Proporcional", I{idx}*\'Panel de Control\'!$E$11, IF(J{idx}="Todo Daniel", I{idx}, 0)))').number_format = CURRENCY_FORMAT
    # Cuota Silvia
    ws3.cell(row=idx, column=12, value=f'=I{idx}-K{idx}').number_format = CURRENCY_FORMAT
    
    # Aporte real pagado por cada uno
    ws3.cell(row=idx, column=13, value=f'=IF(E{idx}="Daniel", I{idx}, 0)').number_format = CURRENCY_FORMAT
    ws3.cell(row=idx, column=14, value=f'=IF(E{idx}="Silvia", I{idx}, 0)').number_format = CURRENCY_FORMAT

    for c in range(1, 15):
        ws3.cell(row=idx, column=c).border = border_cell

# Extra empty rows ready to be filled
for r in range(11, 35):
    ws3.cell(row=r, column=1, value=r-4).alignment = align_center
    ws3.cell(row=r, column=8, value="NO").alignment = align_center
    ws3.cell(row=r, column=10, value="Mitad (50/50)").alignment = align_center
    ws3.cell(row=r, column=9, value=f'=IF(G{r}>0, G{r}*IF(H{r}="SÍ", 1.03, 1), 0)').number_format = CURRENCY_FORMAT
    ws3.cell(row=r, column=11, value=f'=IF(J{r}="Mitad (50/50)", I{r}*0.5, IF(J{r}="% Proporcional", I{r}*\'Panel de Control\'!$E$11, IF(J{r}="Todo Daniel", I{r}, 0)))').number_format = CURRENCY_FORMAT
    ws3.cell(row=r, column=12, value=f'=I{r}-K{r}').number_format = CURRENCY_FORMAT
    ws3.cell(row=r, column=13, value=f'=IF(E{r}="Daniel", I{r}, 0)').number_format = CURRENCY_FORMAT
    ws3.cell(row=r, column=14, value=f'=IF(E{r}="Silvia", I{r}, 0)').number_format = CURRENCY_FORMAT
    for c in range(1, 15):
        cell = ws3.cell(row=r, column=c)
        cell.border = border_cell
        if c in [7, 9, 11, 12, 13, 14]:
            cell.number_format = CURRENCY_FORMAT

# Total Row at Row 35
tot_row_gastos = 35
ws3.cell(row=tot_row_gastos, column=3, value="TOTALES DEL MES:").font = font_bold
ws3.cell(row=tot_row_gastos, column=9, value=f"=SUM(I5:I{tot_row_gastos-1})").number_format = CURRENCY_FORMAT
ws3.cell(row=tot_row_gastos, column=9).font = font_bold

ws3.cell(row=tot_row_gastos, column=11, value=f"=SUM(K5:K{tot_row_gastos-1})").number_format = CURRENCY_FORMAT
ws3.cell(row=tot_row_gastos, column=11).font = Font(name="Calibri", size=11, bold=True, color=DANIEL_COLOR)

ws3.cell(row=tot_row_gastos, column=12, value=f"=SUM(L5:L{tot_row_gastos-1})").number_format = CURRENCY_FORMAT
ws3.cell(row=tot_row_gastos, column=12).font = Font(name="Calibri", size=11, bold=True, color=SILVIA_COLOR)

ws3.cell(row=tot_row_gastos, column=13, value=f"=SUM(M5:M{tot_row_gastos-1})").number_format = CURRENCY_FORMAT
ws3.cell(row=tot_row_gastos, column=13).font = Font(name="Calibri", size=11, bold=True, color=DANIEL_COLOR)

ws3.cell(row=tot_row_gastos, column=14, value=f"=SUM(N5:N{tot_row_gastos-1})").number_format = CURRENCY_FORMAT
ws3.cell(row=tot_row_gastos, column=14).font = Font(name="Calibri", size=11, bold=True, color=SILVIA_COLOR)

for c in range(1, 15):
    ws3.cell(row=tot_row_gastos, column=c).border = border_header


# ==========================================================
# 4. HOJA: PRESUPUESTO Y METAS DE AHORRO
# ==========================================================
ws4 = wb.create_sheet(title="Presupuesto y Metas")
ws4.views.sheetView[0].showGridLines = True

ws4.merge_cells("B2:G2")
ws4["B2"].value = "PRESUPUESTO POR CATEGORÍA Y METAS DE AHORRO"
ws4["B2"].font = font_title
ws4["B2"].fill = fill_emerald_dark
ws4["B2"].alignment = align_center

# Table 1: Presupuesto vs Real
ws4.merge_cells("B4:G4")
ws4["B4"].value = "1. GASTO REAL VS. PRESUPUESTO MENSUAL (POR CATEGORÍA)"
ws4["B4"].font = font_sec_hdr
ws4["B4"].fill = fill_emerald_light

headers_cat = ["Categoría", "Presupuesto Mensual ($)", "Gasto Real ($)", "Diferencia / Disponible ($)", "% Ejecución", "Estado"]
for c_idx, h in enumerate(headers_cat, start=2):
    cell = ws4.cell(row=5, column=c_idx, value=h)
    cell.font = font_tbl_hdr
    cell.fill = fill_emerald_hdr
    cell.alignment = align_center
    cell.border = border_header

categories = [
    ("Vivienda (Arriendo / Aseo)", 735000),
    ("Alimentación (Mercado / Comidas)", 600000),
    ("Servicios (Internet / Luz / Agua)", 275000),
    ("Transporte (Gasolina / Pasajes)", 150000),
    ("Ocio y Salidas", 250000),
    ("Otros / Imprevistos", 100000),
]

for idx, (cat_name, budget) in enumerate(categories, start=6):
    ws4.cell(row=idx, column=2, value=cat_name).font = font_bold
    ws4.cell(row=idx, column=3, value=budget).number_format = CURRENCY_FORMAT
    
    # Real expense sum from Registro Gastos
    # We match substring or category name
    clean_cat = cat_name.split()[0]
    ws4.cell(row=idx, column=4, value=f'=SUMIF(\'Registro Gastos\'!$D$5:$D$34, "*{clean_cat}*", \'Registro Gastos\'!$I$5:$I$34)').number_format = CURRENCY_FORMAT
    
    # Difference (Budget - Real)
    ws4.cell(row=idx, column=5, value=f'=C{idx}-D{idx}').number_format = CURRENCY_FORMAT
    # % Execution
    ws4.cell(row=idx, column=6, value=f'=IF(C{idx}>0, D{idx}/C{idx}, 0)').number_format = PERCENT_FORMAT
    ws4.cell(row=idx, column=6).alignment = align_center
    # Status
    ws4.cell(row=idx, column=7, value=f'=IF(E{idx}>=0, "DENTRO DE PRESUPUESTO", "EXCEDIDO ⚠️")').alignment = align_center

    for c in range(2, 8):
        ws4.cell(row=idx, column=c).border = border_cell

tot_cat_r = len(categories) + 6
ws4.cell(row=tot_cat_r, column=2, value="TOTAL PRESUPUESTO HOGAR:").font = font_bold
ws4.cell(row=tot_cat_r, column=3, value=f"=SUM(C6:C{tot_cat_r-1})").number_format = CURRENCY_FORMAT
ws4.cell(row=tot_cat_r, column=4, value=f"=SUM(D6:D{tot_cat_r-1})").number_format = CURRENCY_FORMAT
ws4.cell(row=tot_cat_r, column=5, value=f"=C{tot_cat_r}-D{tot_cat_r}").number_format = CURRENCY_FORMAT
ws4.cell(row=tot_cat_r, column=6, value=f"=D{tot_cat_r}/C{tot_cat_r}").number_format = PERCENT_FORMAT
for c in range(2, 8):
    ws4.cell(row=tot_cat_r, column=c).border = border_header

# Table 2: Metas de Ahorro
ws4.merge_cells("B15:G15")
ws4["B15"].value = "2. METAS DE AHORRO COMPARTIDAS (OBJETIVOS Y AVANCE)"
ws4["B15"].font = font_sec_hdr
ws4["B15"].fill = fill_daniel_light

headers_metas = ["Objetivo / Meta", "Monto Meta ($)", "Ahorrado a la Fecha ($)", "Falta por Ahorrar ($)", "% Cumplimiento", "Aporte Mensual Sugerido ($)"]
for c_idx, h in enumerate(headers_metas, start=2):
    cell = ws4.cell(row=16, column=c_idx, value=h)
    cell.font = font_tbl_hdr
    cell.fill = fill_daniel_hdr
    cell.alignment = align_center
    cell.border = border_header

metas_data = [
    ("Fondo de Emergencia Familiar", 2000000, 500000, 150000),
    ("Viaje / Vacaciones", 1500000, 300000, 100000),
    ("Mantenimiento y Llantas Moto", 800000, 200000, 66666),
]

for idx, (m_name, m_target, m_saved, m_monthly) in enumerate(metas_data, start=17):
    ws4.cell(row=idx, column=2, value=m_name).font = font_bold
    ws4.cell(row=idx, column=3, value=m_target).number_format = CURRENCY_FORMAT
    ws4.cell(row=idx, column=4, value=m_saved).number_format = CURRENCY_FORMAT
    ws4.cell(row=idx, column=5, value=f'=C{idx}-D{idx}').number_format = CURRENCY_FORMAT
    ws4.cell(row=idx, column=6, value=f'=IF(C{idx}>0, D{idx}/C{idx}, 0)').number_format = PERCENT_FORMAT
    ws4.cell(row=idx, column=6).alignment = align_center
    ws4.cell(row=idx, column=7, value=m_monthly).number_format = CURRENCY_FORMAT

    for c in range(2, 8):
        ws4.cell(row=idx, column=c).border = border_cell


# ==========================================================
# 5. HOJA: CUENTAS PERSONALES DANIEL (EXCEL ORIGINAL)
# ==========================================================
ws5 = wb.create_sheet(title="Personal Daniel")
ws5.views.sheetView[0].showGridLines = True

ws5.merge_cells("B2:G2")
ws5["B2"].value = "PLANILLA PERSONAL DE DANIEL (EXTRAÍDA DE TU EXCEL)"
ws5["B2"].font = font_title
ws5["B2"].fill = fill_daniel_hdr
ws5["B2"].alignment = align_center

# Ingresos Daniel
ws5.merge_cells("B4:D4")
ws5["B4"].value = "INGRESOS MENSUALES DE DANIEL"
ws5["B4"].font = font_sec_hdr
ws5["B4"].fill = fill_daniel_light

ingresos_daniel = [
    ("Pago Maral", 1643000),
    ("Pago IA", 150000),
    ("Trabajo Adicional", 200000),
]
ws5.cell(row=5, column=2, value="Fuente de Ingreso").font = font_tbl_hdr
ws5.cell(row=5, column=2).fill = fill_dark_hdr
ws5.cell(row=5, column=3, value="Monto ($)").font = font_tbl_hdr
ws5.cell(row=5, column=3).fill = fill_dark_hdr

for idx, (src, amt) in enumerate(ingresos_daniel, start=6):
    ws5.cell(row=idx, column=2, value=src)
    ws5.cell(row=idx, column=3, value=amt).number_format = CURRENCY_FORMAT
    ws5.cell(row=idx, column=2).border = border_cell
    ws5.cell(row=idx, column=3).border = border_cell

ws5.cell(row=9, column=2, value="TOTAL INGRESOS DANIEL:").font = font_bold
ws5.cell(row=9, column=3, value="=SUM(C6:C8)").number_format = CURRENCY_FORMAT
ws5.cell(row=9, column=3).font = Font(name="Calibri", size=11, bold=True, color=DANIEL_COLOR)
ws5.cell(row=9, column=2).border = border_header
ws5.cell(row=9, column=3).border = border_header

# Gastos Personales Daniel
ws5.merge_cells("B11:D11")
ws5["B11"].value = "GASTOS MENSUALES PERSONALES DE DANIEL"
ws5["B11"].font = font_sec_hdr
ws5["B11"].fill = fill_daniel_light

gastos_d = [
    ("Cuota Moto", 410350, 16),
    ("Seguro Moto (Prorrateado)", 33333, 1),
    ("Llantas Moto (Prorrateado)", 33333, 1),
    ("GPS Moto", 32000, 1),
    ("Mantenimiento Moto", 27000, 1),
    ("Plan Movistar", 28000, 5),
    ("Parqueadero Universidad", 90000, 5),
    ("Gasolina Moto", 50000, "Varios"),
    ("Universidad", 40000, "Varios"),
    ("Varios / Imprevistos", 50000, "Varios"),
    ("Lavandería", 30000, "Varios"),
    ("Corte de Pelo", 30000, "Varios"),
    ("Aseo Personal", 35000, 1),
    ("Gastos Diarios Presupuestados (Almuerzo / Comida)", 705000, "Diario"),
]

ws5.cell(row=12, column=2, value="Concepto Personal").font = font_tbl_hdr
ws5.cell(row=12, column=2).fill = fill_dark_hdr
ws5.cell(row=12, column=3, value="Monto Mensual ($)").font = font_tbl_hdr
ws5.cell(row=12, column=3).fill = fill_dark_hdr
ws5.cell(row=12, column=4, value="Día / Frecuencia").font = font_tbl_hdr
ws5.cell(row=12, column=4).fill = fill_dark_hdr

for idx, (c_name, c_amt, c_day) in enumerate(gastos_d, start=13):
    ws5.cell(row=idx, column=2, value=c_name)
    ws5.cell(row=idx, column=3, value=c_amt).number_format = CURRENCY_FORMAT
    ws5.cell(row=idx, column=4, value=c_day).alignment = align_center
    for c in range(2, 5):
        ws5.cell(row=idx, column=c).border = border_cell

tot_gd_r = len(gastos_d) + 13
ws5.cell(row=tot_gd_r, column=2, value="TOTAL GASTOS PERSONALES DANIEL:").font = font_bold
ws5.cell(row=tot_gd_r, column=3, value=f"=SUM(C13:C{tot_gd_r-1})").number_format = CURRENCY_FORMAT
ws5.cell(row=tot_gd_r, column=3).font = font_bold
for c in range(2, 5):
    ws5.cell(row=tot_gd_r, column=c).border = border_header

# Resumen Libre Daniel
ws5.merge_cells("B29:D29")
ws5["B29"].value = "BALANCE RESIDUAL DE DANIEL"
ws5["B29"].font = font_sec_hdr
ws5["B29"].fill = fill_emerald_light

ws5.cell(row=30, column=2, value="Ingresos Totales Daniel:").font = font_bold
ws5.cell(row=30, column=3, value="=C9").number_format = CURRENCY_FORMAT
ws5.cell(row=31, column=2, value="Menos Gastos Personales:").font = font_bold
ws5.cell(row=31, column=3, value=f"=C{tot_gd_r}").number_format = CURRENCY_FORMAT
ws5.cell(row=32, column=2, value="Menos Cuota del Hogar (Arriendo + Servicios):").font = font_bold
ws5.cell(row=32, column=3, value="='Gastos Fijos'!G10").number_format = CURRENCY_FORMAT
ws5.cell(row=33, column=2, value="SALDO DISPONIBLE FINAL DE DANIEL:").font = Font(name="Calibri", size=12, bold=True, color=EMERALD_DARK)
ws5.cell(row=33, column=3, value="=C30-C31-C32").number_format = CURRENCY_FORMAT
ws5.cell(row=33, column=3).font = Font(name="Calibri", size=13, bold=True, color=EMERALD_DARK)
ws5.cell(row=33, column=3).fill = fill_emerald_light

for r in range(30, 34):
    for c in range(2, 4):
        ws5.cell(row=r, column=c).border = border_cell


# ==========================================================
# AUTO-FIT COLUMN WIDTHS ACROSS ALL SHEETS
# ==========================================================
for sheet in wb.worksheets:
    for col in sheet.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            # Ignore merged cells in width calculation if they are too long
            if cell.coordinate in sheet.merged_cells:
                continue
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

# Specific tweaks
ws1.column_dimensions["A"].width = 4
ws1.column_dimensions["B"].width = 38
ws1.column_dimensions["C"].width = 20
ws1.column_dimensions["D"].width = 20
ws1.column_dimensions["E"].width = 22
ws1.column_dimensions["F"].width = 22
ws1.column_dimensions["G"].width = 22

ws2.column_dimensions["A"].width = 4
ws2.column_dimensions["B"].width = 34
ws2.column_dimensions["C"].width = 18
ws2.column_dimensions["D"].width = 14
ws2.column_dimensions["E"].width = 14
ws2.column_dimensions["F"].width = 18
ws2.column_dimensions["G"].width = 18
ws2.column_dimensions["H"].width = 18
ws2.column_dimensions["I"].width = 16

ws3.column_dimensions["A"].width = 5
ws3.column_dimensions["B"].width = 13
ws3.column_dimensions["C"].width = 28
ws3.column_dimensions["D"].width = 16
ws3.column_dimensions["E"].width = 14
ws3.column_dimensions["F"].width = 16
ws3.column_dimensions["G"].width = 16
ws3.column_dimensions["H"].width = 14
ws3.column_dimensions["I"].width = 16
ws3.column_dimensions["J"].width = 18
ws3.column_dimensions["K"].width = 16
ws3.column_dimensions["L"].width = 16
ws3.column_dimensions["M"].width = 16
ws3.column_dimensions["N"].width = 16

ws4.column_dimensions["A"].width = 4
ws4.column_dimensions["B"].width = 32
ws4.column_dimensions["C"].width = 24
ws4.column_dimensions["D"].width = 20
ws4.column_dimensions["E"].width = 24
ws4.column_dimensions["F"].width = 16
ws4.column_dimensions["G"].width = 26

ws5.column_dimensions["A"].width = 4
ws5.column_dimensions["B"].width = 35
ws5.column_dimensions["C"].width = 22
ws5.column_dimensions["D"].width = 18

output_path = r"C:\Users\lady\.gemini\antigravity\scratch\cuentas-claras\Cuentas_Claras_Daniel_y_Silvia.xlsx"
wb.save(output_path)
print(f"Workbook successfully created at: {output_path}")
