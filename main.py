import tkinter as tk
from tkinter import ttk, filedialog

import numpy as np
import pandas as pd
from datetime import datetime
import os
from math import isnan


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.sum_bom = None
        self.mainpart_ID = None
        self.mainpart_name = None
        self.root_path = os.getcwd()
        self.bom_loaded = False


        self.title('pbx PLM tools v0.1')
        # self.geometry('300x300')

        self.button_load_bom = ttk.Button(self, text="Load BOM", command=self.load_bom)
        self.button_load_bom.pack(fill="x", padx='10', pady='5')

        self.button_load_prices = ttk.Button(self, text="Load part prices", command=self.load_prices)
        self.button_load_prices.pack(fill="x", padx='10', pady='5')

        self.button_export_summarybom = ttk.Button(self, text="Export summary BOM", command=self.export_summarybom)
        self.button_export_summarybom.pack(fill="x", padx='10', pady='5')

        self.button_export_summarybom_wo_ass = ttk.Button(self, text="Export sum BOM w/o assemblies", command=self.export_summary_bom_without_assemblies)
        self.button_export_summarybom_wo_ass.pack(fill="x", padx='10', pady='5')

        self.button_write_assembly_bom = ttk.Button(self, text="Write assembly partial BOMs", command=self.write_assembly_bom)
        self.button_write_assembly_bom.pack(fill="x", padx='10', pady='5')

        self.button_open_rename_dialog = ttk.Button(self, text='Rename drawings', command=self.rename_files)
        self.button_open_rename_dialog.pack(fill='x', padx='10', pady='5')

    def load_bom(self):
        bom_path = filedialog.askopenfile()
        self.bom = pd.read_excel(bom_path.name)
        self.bom.reset_index(inplace=True)

        # retract the main part and get info from it
        mainpart = self.bom[self.bom['ID'] == "1"]
        self.mainpart_name = mainpart['Item Name'][0]
        self.mainpart_ID = mainpart['Item Number'][0]
        major_revision = mainpart['Major Revision'][0]
        minor_revision = mainpart['Minor Revision'][0]
        if np.issubdtype(minor_revision, np.integer):
            minor_revision = str(minor_revision).zfill(2)
        self.mainpart_revision = '_'.join([major_revision, minor_revision])

        # replace '-' with np.nan in DD-drawing-number and DD-ID-Number
        self.bom['DD-drawing-number'].replace('-', np.nan, inplace=True)
        self.bom['DD-ID-Number'].replace('-', np.nan, inplace=True)

        print('BOM loaded!')

        self.create_summarybom()

    def create_summarybom(self):
        # specify the fields to be exported (Future: configurable?)
        exported_fields = ['Item Number', 'Major Revision', 'Minor Revision', 'Item Name', 'Type', 'Quantity',
                           'Item Description', 'Cost', 'Currency Code', 'Material', 'Manufacturer',
                           'Manufacturer Item Number', 'Creation Date', 'DD-drawing-number', 'DD-ID-Number',
                           'Old-PBX-ID-Number', 'PBX-drawing number', 'Pre-cut-size(m,m2)']

        # filter exported fields and drop "Assembly" entries, these are not part of a summary BOM
        #filtered_bom = self.bom[exported_fields][self.bom['Type'] != 'Assembly']
        filtered_bom = self.bom[exported_fields]

        # group by Item Number and sum up the entries
        df_grouped = filtered_bom.groupby(['Item Number'])['Quantity'].agg('sum').to_frame()
        df_grouped.reset_index(inplace=True)

        # create a second DataFrame to carry all the other information except "Quantity"
        df_dropduplicates = filtered_bom.drop_duplicates(subset=['Item Number'])
        df_dropduplicates = df_dropduplicates.drop(['Quantity'], axis=1)
        df_dropduplicates = df_dropduplicates.set_index(keys=['Item Number'])

        # concatenate the two DataFrames
        self.sum_bom = pd.merge(left=df_dropduplicates, left_on="Item Number",
                                right=df_grouped, right_on="Item Number", how="left")
        print('Summary BOM created!')

    def export_summarybom(self):
        if not isinstance(self.sum_bom, pd.DataFrame):
            print('Failed! No BOM loaded yet.')
            return
        # save the summary BOM with a datetag
        timestamp = datetime.today().strftime('%y%m%d%H%M%S')
        filename = "+".join(["sumBOM", str(self.mainpart_ID), self.mainpart_name, self.mainpart_revision, timestamp])
        self.sum_bom.to_excel(filename+'.xlsx')
        self.sum_bom.to_csv(filename+'.csv')
        print('Summary BOM exported.')

    def load_prices(self):
        # check if a summary BOM is already created
        if not isinstance(self.sum_bom, pd.DataFrame):
            print('Failed! No BOM loaded yet.')
            return

        # get a dialog to open the current prices file
        invoices_path = filedialog.askopenfile()
        invoices = pd.read_excel(invoices_path.name, skiprows=4)

        # convert invoice date to date type
        invoices['invoice date'] = pd.to_datetime(invoices['invoice date'], format="%d.%m.%Y")

        # sort by invoice date
        invoices.sort_values(by='invoice date')

        # generate the list of prices
        prices_group = invoices.groupby('Item ID')['price invoice', 'Supplier']
        prices = prices_group.last()
        # prices = invoices.groupby('Item ID')['price invoice'].agg('mean').to_frame()

        # reset index
        prices.reset_index(inplace=True)

        # merge the price list into the summary BOM
        self.sum_bom = pd.merge(left=self.sum_bom, right=prices, left_on='DD-ID-Number', right_on='Item ID', how='left')

        # calculate prize of pre-cut parts
        self.sum_bom['part price'] = self.sum_bom['price invoice'] * self.sum_bom['Pre-cut-size(m,m2)'].fillna(value=1)

        # calculate the total system price
        self.sum_bom['unit price'] = self.sum_bom['Quantity'] * self.sum_bom['part price']

        print('Successfully added costs to summary BOM.')

    def export_summary_bom_without_assemblies(self):
        if not isinstance(self.sum_bom, pd.DataFrame):
            print('Failed! No BOM loaded yet.')
            return
        # save the summary BOM with a datetag
        timestamp = datetime.today().strftime('%y%m%d%H%M%S')
        filename = "+".join(["sumBOM", str(self.mainpart_ID), self.mainpart_name, self.mainpart_revision, timestamp])
        export_bom = self.sum_bom[self.bom['Type'] != 'Assembly']
        export_bom.to_excel(filename+'.xlsx')
        export_bom.to_csv(filename+'.csv')
        print('Summary BOM exported.')

    def write_assembly_bom(self):
        '''
        Write the assembly BOMs. This is a list of parts that have the same parent ID. Write the assembly BOMs into a new folder.

        :return:
        '''
        if not isinstance(self.sum_bom, pd.DataFrame):
            print('Failed! No BOM loaded yet.')
            return
        exported_params = ['Item Number', 'Major Revision', 'Minor Revision', 'Item Name', 'Item Description',
                           'Quantity', 'Type', 'DD-drawing-number', 'DD-ID-Number', 'Old-PBX-ID-Number', 'PBX-drawing number']
        today = datetime.now().strftime('%y%m%d_%H%M%S')
        folder_name = '-'.join(['AssemblyBOMs', str(self.mainpart_ID), self.mainpart_name, self.mainpart_revision, 'createdAt', today])
        folder_path = os.path.join(self.root_path, folder_name)
        os.mkdir(folder_path)
        grouped_bom = self.bom.groupby('Parent ID')
        for k, v in grouped_bom:
            parent_part = self.bom[self.bom['ID']==k]
            dd_drawing_number = parent_part['DD-drawing-number'].values[0]
            if dd_drawing_number != dd_drawing_number:
                filename = '-'.join(['AssemblyBOM', str(parent_part['Item Number'].values[0]), parent_part['Item Name'].values[0], parent_part['Major Revision'].values[0], parent_part['Minor Revision'].values[0]])+'.xlsx'
            else:
                filename = str(parent_part['DD-drawing-number'].values[0])+'.xlsx'
            export_df = v[exported_params]
            filepath = os.path.join(folder_path, filename)
            export_df.to_excel(filepath)

        print('Assembly BOMs successfully written in folder: {}'.format(folder_path))

    def rename_files(self):
        if not isinstance(self.sum_bom, pd.DataFrame):
            print('Failed! No BOM loaded yet.')
            return
        folder = os.path.join(self.root_path, 'drawings')
        file_list = os.listdir(folder)

        for file in file_list:
            id = int(file.split('-')[0])
            filetype = file.split('.')[-1]
            if not id in self.bom['Item Number'].values:
                continue
            part = self.bom[self.bom['Item Number'] == id]
            dd_drawing_number = part['DD-drawing-number'].values[0]
            dd_id_number = part['DD-ID-Number'].values[0]

            if isinstance(dd_drawing_number, str):
                filename = '.'.join([str(dd_drawing_number), filetype])
            elif isinstance(dd_id_number, str):
                filename = '.'.join([str(dd_id_number), filetype])
            else:
                continue

            old_filename = os.path.join(folder, file)
            new_filename = os.path.join(folder, filename)
            if os.path.isfile(new_filename):
                print('Cannot rename {}, because {} already exists. Maybe the DD drawing number is used twice.'.format(id, new_filename))
                continue
            os.rename(old_filename, new_filename)

        print('File renaming completed.')
if __name__ == '__main__':
    app = App()
    app.mainloop()
