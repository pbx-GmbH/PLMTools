import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
from datetime import datetime


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('pbx PLM tools v0.1')
        self.geometry('200x600')

        self.button_load_bom = ttk.Button(self, text="Load BOM", command=self.load_bom)
        self.button_load_bom.pack(fill="x", padx='10', pady='5')

        self.button_export_summarybom = ttk.Button(self, text="Export summary BOM", command=self.export_summarybom)
        self.button_export_summarybom.pack(fill="x", padx='10', pady='5')

    def load_bom(self):
        bom_path = filedialog.askopenfile()
        self.bom = pd.read_excel(bom_path.name)

    def export_summarybom(self):
        # specify the fields to be exported (Future: configurable?)
        exported_fields = ['Item Number', 'Major Revision', 'Minor Revision', 'Item Name', 'Type', 'Quantity', 'Item Description', 'Cost', 'Currency Code', 'Material', 'Manufacturer', 'Manufacturer Item Number', 'Creation Date', 'DD-drawing-number', 'DD-ID-Number', 'Old-PBX-ID-Number', 'PBX-drawing number']

        # filter exported fields and drop "Assembly" entries, these are not part of a summary BOM
        filtered_bom = self.bom[exported_fields][self.bom['Type'] != 'Assembly']

        # group by Item Number and sum up the entries
        df_grouped = filtered_bom.groupby(['Item Number'])['Quantity'].agg('sum').to_frame()

        # create a second DataFrame to carry all the other information except "Quantity"
        df_dropduplicates = filtered_bom.drop_duplicates(subset=['Item Number'])
        df_dropduplicates = df_dropduplicates.drop(['Quantity'], axis=1)
        df_dropduplicates = df_dropduplicates.set_index(keys=['Item Number'])

        # concatenate the two DataFrames
        self.sum_bom = pd.concat([df_dropduplicates, df_grouped], axis=1)

        # save the summary BOM with a datetag
        timestamp = datetime.today().strftime('%y%m%d%H%M%S')
        self.sum_bom.to_excel(timestamp+'_Summary_BOM_Export.xlsx')


if __name__ == '__main__':
    app = App()
    app.mainloop()
