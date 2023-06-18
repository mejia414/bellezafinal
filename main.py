import streamlit as st

import pandas as pd
import numpy as np

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

import base64
from io import BytesIO

class Template():
    def __init__(self, *args,**kwargs):
        self.calculate_example()
        self.calculate_excel()

    def calculate_example(self,*args,**kwargs):
        reocrds=[
            {"client": "client_1", "product": "pan"},
            {"client": "client_1", "product": "leche"},
            {"client": "client_1", "product": "azucar"},
            {"client": "client_2", "product": "pan"},
            {"client": "client_2", "product": "cafe"},
            {"client": "client_2", "product": "cereal"},
            {"client": "client_3", "product": "leche"},
            {"client": "client_3", "product": "azucar"},
            {"client": "client_3", "product": "cafe"},
            {"client": "client_4", "product": "pan"},
            {"client": "client_4", "product": "leche"},
            {"client": "client_4", "product": "azucar"},
            {"client": "client_4", "product": "cafe"},
            {"client": "client_5", "product": "pan"},
            {"client": "client_5", "product": "leche"},
            {"client": "client_5", "product": "cafe"},
            {"client": "client_1", "product": "carne"},
            {"client": "client_2", "product": "carne"},
            {"client": "client_3", "product": "carne"},
            {"client": "client_4", "product": "carne"},
            {"client": "client_5", "product": "carne"},
        ]

        products=[
            {"product": "pan", "product_line": "panaderia", "state_product": 1},
            {"product": "leche", "product_line": "lacteo", "state_product": 1},
            {"product": "azucar", "product_line": "endulsante", "state_product": 1},
            {"product": "cafe", "product_line": "cafe", "state_product": 1},
            {"product": "cereal", "product_line": "cereal", "state_product": 1},
            {"product": "carne", "product_line": "carnico", "state_product": 1},
        ]

        self.df_example_records=pd.DataFrame(reocrds)
        self.df_example_products=pd.DataFrame(products)

    def calculate_excel(self,*args,**kwargs):
            buffer = BytesIO()
            writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
            
            self.df_example_records.to_excel(writer, index=False, sheet_name='record')
            self.df_example_products.to_excel(writer, index=False, sheet_name='product')
            
            writer.close()
            buffer.seek(0)

            self.excel_file = base64.b64encode(buffer.read()).decode()        

class Info:
    def __init__(self, *args,**kwargs):
        self.df_records=kwargs.get('df_records')
        self.df_products = kwargs.get('df_products')

        self.calculate_frequent_itemsets()
        self.calculate_rules()
        self.calculate_excel()

    def calculate_frequent_itemsets(self,*args,**kwargs):
        df=self.df_records.copy()
        df_tmp=self.df_products.copy()

        state_product=1
        df_tmp.query(f"state_product == {state_product}", engine='python',inplace=True)

        df = pd.merge(df_tmp, df).reset_index(drop=True)

        groups = [
            "client"
        ]

        aggs = {
            "product_line": [
                "unique"
            ]
        }

        df = df.groupby(groups).agg(aggs).reset_index()
        df.columns = df.columns.map("_".join).str.strip("_")

        df.sort_values(['client'], ascending=[False],inplace=True)

        transactions=df['product_line_unique'].to_list()

        te = TransactionEncoder()
        te_ary = te.fit_transform(transactions)
        df = pd.DataFrame(te_ary, columns=te.columns_)

        self.df_frequent_itemsets = apriori(df, min_support=0.3, use_colnames=True)

    def calculate_rules(self,*args,**kwargs):
        df=self.df_frequent_itemsets.copy()

        self.df_rules = association_rules(df, metric="confidence", min_threshold=0.8, support_only=True)
    
    def calculate_excel(self,*args,**kwargs):
            buffer = BytesIO()
            writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
            
            self.df_rules.to_excel(writer, index=False, sheet_name='rule')
            self.df_frequent_itemsets.to_excel(writer, index=False, sheet_name='frequent_itemset')
            self.df_products.to_excel(writer, index=False, sheet_name='product')
            self.df_records.to_excel(writer, index=False, sheet_name='record')
            
            writer.close()
            buffer.seek(0)

            self.excel_file = base64.b64encode(buffer.read()).decode()        

def main():
    st.set_page_config(layout='wide')

    df_records_load=False
    df_products_load=False
    df_rules_load=False
    df_frequent_itemsets_load=False

    st.title("calculadora reglas de asociacion de clientes & productos")
    
    # Descargar la plantilla
    if st.button("Descargar plantilla Excel"):
        template=Template()
        href = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{template.excel_file}"
        st.markdown(f'<a href="{href}" download="plantilla_producto_cliente.xlsx">Haz clic aquí para descargar la plantilla</a>', unsafe_allow_html=True)


    # Cargar archivo de Excel
    file = st.file_uploader("Cargar plantilla de Excel historial & producto", type=["xlsx", "xls"])

    # Mostrar dataset records
    if file is not None:
        try:
            df_records = pd.read_excel(io=file,sheet_name='record')  # Leer el archivo de Excel
            st.info("historial productos & cliente")
            st.dataframe(df_records, use_container_width=True)  # Mostrar los datos en una tabla
            st.success("historial productos & cliente cargado correctamente")
            df_records_load=True

        except Exception as e:
            st.error("Ocurrió un error al cargar el archivo records. Detalles: {}".format(str(e)))

    # Mostrar dataset products
    if file is not None:
        try:
            df_products = pd.read_excel(io=file,sheet_name='product')  # Leer el archivo de Excel
            st.info("productos & linea producto")
            st.dataframe(df_products, use_container_width=True)  # Mostrar los datos en una tabla
            st.success("historial productos & linea producto cargado correctamente")
            df_products_load=True

        except Exception as e:
            st.error("Ocurrió un error al cargar el archivo product. Detalles: {}".format(str(e)))

    if df_products_load and df_records_load:
        st.info("items & reglas de asocociacion")
        info=Info(**dict(df_records=df_records,df_products=df_products))
        st.success("informe calculado correctamente")
        df_rules_load=True
        df_frequent_itemsets_load=True

    if df_frequent_itemsets_load and df_rules_load:
        df_frequent_itemsets=info.df_frequent_itemsets.copy()
        df_rules=info.df_rules.copy()
        st.info("informe frecuencia productos")
        st.dataframe(df_frequent_itemsets, use_container_width=True)
        st.info("informe reglas productos")
        st.dataframe(df_rules, use_container_width=True)


    # Descargar el archivo Excel cuando se hace clic en el botón
    if file is not None:
        if st.button("Descargar informe Excel"):
            href = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{info.excel_file}"
            st.markdown(f'<a href="{href}" download="informe_producto_cliente.xlsx">Haz clic aquí para descargar el informe</a>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
