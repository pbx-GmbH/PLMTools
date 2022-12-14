import pandas as pd

invoices = pd.read_excel('2022 purchase prices.xlsm')

prices = invoices.groupby('Me nr')['invoice price'].agg('mean').to_frame()
prices.reset_index(inplace=True)

sum_bom = pd.read_excel('221213122919_Summary_BOM_Export.xlsx')

sum_bom = pd.merge(left=sum_bom, right=prices, left_on='DD-ID-Number', right_on='Me nr')