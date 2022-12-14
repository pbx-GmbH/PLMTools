import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
from datetime import datetime


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.sum_bom = None

        self.title('pbx PLM tools v0.1')
        self.geometry('200x600')

        self.button_load_bom = ttk.Button(self, text="Load BOM", command=self.load_bom)
        self.button_load_bom.pack(fill="x", padx='10', pady='5')

        self.button_export_summarybom = ttk.Button(self, text="Export summary BOM", command=self.export_summarybom)
        self.button_export_summarybom.pack(fill="x", padx='10', pady='5')

        self.button_load_prices = ttk.Button(self, text="Add prices to summary BOM", command=self.load_prices)
        self.button_load_prices.pack(fill="x", padx='10', pady='5')

    def load_bom(self):
        bom_path = filedialog.askopenfile()
        self.bom = pd.read_excel(bom_path.name)
        self.bom.reset_index(inplace=True)
        self.bom.mainpart_name = self.bom[self.bom['ID'] == "1"]['Item Name'][0]
        self.bom.mainpart_ID = self.bom[self.bom['ID'] == "1"]['Item Number'][0]
        print('BOM loaded!')

    def create_summarybom(self):
        # specify the fields to be exported (Future: configurable?)
        exported_fields = ['Item Number', 'Major Revision', 'Minor Revision', 'Item Name', 'Type', 'Quantity', 'Item Description', 'Cost', 'Currency Code', 'Material', 'Manufacturer', 'Manufacturer Item Number', 'Creation Date', 'DD-drawing-number', 'DD-ID-Number', 'Old-PBX-ID-Number', 'PBX-drawing number']

        # filter exported fields and drop "Assembly" entries, these are not part of a summary BOM
        filtered_bom = self.bom[exported_fields][self.bom['Type'] != 'Assembly']

        # group by Item Number and sum up the entries
        df_grouped = filtered_bom.groupby(['Item Number'])['Quantity'].agg('sum').to_frame()
        df_grouped.reset_index(inplace=True)

        # create a second DataFrame to carry all the other information except "Quantity"
        df_dropduplicates = filtered_bom.drop_duplicates(subset=['Item Number'])
        df_dropduplicates = df_dropduplicates.drop(['Quantity'], axis=1)
        df_dropduplicates = df_dropduplicates.set_index(keys=['Item Number'])

        # concatenate the two DataFrames
        self.sum_bom = pd.merge(left=df_dropduplicates, left_on="Item Number", right=df_grouped, right_on="Item Number", how="left")
        self.sum_bom.mainpart_ID = self.bom.mainpart_ID
        self.sum_bom.mainpart_name = self.bom.mainpart_name
        print('created')

    def export_summarybom(self):
        # create a new summary BOM
        self.create_summarybom()
        # save the summary BOM with a datetag
        timestamp = datetime.today().strftime('%y%m%d%H%M%S')
        filename = "+".join(["sumBOM", str(self.sum_bom.mainpart_ID), self.sum_bom.mainpart_name, timestamp])
        self.sum_bom.to_excel(filename+'.xlsx')
        print('Summary BOM exported.')

    def load_prices(self):
        # get a dialog to open the current prices file
        invoices_path = filedialog.askopenfile()
        invoices = pd.read_excel(invoices_path.name)

        # generate the list of prices
        prices = invoices.groupby('Me nr')['invoice price'].agg('mean').to_frame()
        prices.reset_index(inplace=True)

        # check if a summary BOM is already created
        if not isinstance(self.sum_bom, pd.DataFrame):
            self.create_summarybom()

        # merge the price list into the summary BOM
        self.sum_bom = pd.merge(left=self.sum_bom, right=prices, left_on='DD-ID-Number', right_on='Me nr', how='left')

        # calculate the total system price
        self.sum_bom['unit price'] = self.sum_bom['Quantity'] * self.sum_bom['invoice price']

        # save the summary BOM with a datetag
        timestamp = datetime.today().strftime('%y%m%d%H%M%S')
        self.sum_bom.to_excel(timestamp + '_Summary_BOM_Export.xlsx')
        print('Summary BOM with prices exported.')

if __name__ == '__main__':
    app = App()
    app.mainloop()
