#!/usr/bin/env python3

import datetime
from typing import Dict, List

from peewee import *
import altair as alt
import streamlit as st
import pandas as pd
from playhouse.reflection import generate_models
import matplotlib.pyplot as plt

from settings import DELTA


class DataFrameOperations:
    def __init__(self, data: Dict[str, List[str]]):
        for _, v in data.items():
            if not v:
                raise "Dicionário vazio"
        self.df = data

    @property
    def df(self) -> pd.DataFrame:
        return self._df
    
    @df.setter
    def df(self, values) -> None:
        self._df = pd.DataFrame.from_dict(values)

    def fix_data(self, data_collumn: str = None) -> None:
        if data_collumn:
            self._df[data_collumn] = self._df[data_collumn].apply(lambda x: x.strftime('%B-%y'))

    def group_by_column(self, collumn: str) -> None:
        # print(self._df)
        """
        Só vai funcionar Com um dataframde de 2 colunas
        Se sobrar colunas vai gerar uma coluna a mais que vai desconfigurar o DF
        O streamlit não vai conseguir ler direito
        """
        self._df = self._df.groupby(by=[collumn], as_index=False, sort=False).sum()

def database_operations(db_path: str) -> SqliteDatabase:
    db = SqliteDatabase(db_path)
    db.connect()
    models = generate_models(db)
    globals().update(models)
    return db

# @st.cache_data
def reais_per_month(inicio, fim) -> Dict[str, List[str]]:

    valor_por_data = {'data': [], 'total': []}

    for notinha in (notas_fiscais_notafiscal.
                    select().
                    join(notas_fiscais_supermercado)
                    .where(notas_fiscais_notafiscal.data_emissao < inicio,
                           notas_fiscais_notafiscal.data_emissao > fim)):
                    
        valor_por_data['data'].append(notinha.data_emissao)
        valor_por_data['total'].append(int(notinha.valor_total))

    return valor_por_data

def reais_per_mercado():

    valor_por_mercado = {'mercado': [], 'total': []}

    for notinha in (notas_fiscais_notafiscal.
                    select().
                    join(notas_fiscais_supermercado)):
                    # .where(notas_fiscais_notafiscal.total_items > 5)):
        valor_por_mercado['mercado'].append(notinha.supermercado.nome)
        valor_por_mercado['total'].append(int(notinha.valor_total))
    
    return valor_por_mercado

def reais_per_item():

    item_history = {
        'item': [],
        'data_compra': [],
        'preco_unidade': [],
        'preco_total': [],
        'local': [],
    }

    for item in (notas_fiscais_itemnotafiscal.
                 select().
                 join(notas_fiscais_notafiscal)):
        item_history['item'].append(item.produto)
        item_history['data_compra'].append(item.nota_fiscal.data_emissao)
        item_history['preco_unidade'].append(float(item.preco_unitario))
        item_history['preco_total'].append((float(item.preco_unitario) * float(item.quantidade)))
        item_history['local'].append(notas_fiscais_supermercado.get(notas_fiscais_supermercado.id == item.nota_fiscal.supermercado_id).nome)
        #print(q)
        #item_history['local'].append()

    return item_history

def valor_mes_personalizado() -> None:

    st.markdown("#### Gasto por mês (default: últimos 6 meses)")

    inicio = st.date_input("De:", value=datetime.date.today())

    fim = st.date_input("Até:", value=datetime.date.today() - DELTA)

    valor_per_data = reais_per_month(inicio, fim)
    
    db_df = DataFrameOperations(valor_per_data)

    db_df.df['month_year'] = db_df.df['data'].apply(lambda x: x.strftime('%B-%y'))

    db_df.df.sort_values(by=['data'], inplace=True)

    alt_fig = alt.Chart(db_df.df).mark_bar().encode(
        y=alt.Y('sum(total):Q', title='Total Gasto R$'),
        x=alt.X('month_year', sort=None, title='Mês - Ano',
                axis=alt.Axis(labelAngle=45)
        ),
        color='sum(total)',
    ).interactive()

    st.altair_chart(alt_fig)


def valor_mercado_personalizado():

    st.markdown("#### Grafico indicando valor gasto por supermercado.")

    valor_per_mercado = reais_per_mercado()

    mercados = DataFrameOperations(valor_per_mercado)

    mercados.group_by_column('mercado')

    sizes = mercados.df['total'].to_list()

    total = 0
    for i in sizes:
        total = total + i

    option = st.multiselect(
        "Selecione os supermercados:",
        mercados.df['mercado'].to_list(),
        default=mercados.df['mercado'].to_list()
    )

    if option:
        # Quando muda as seleções ele roda daqui pra baixo tudo de novo
        index2drop = []
        for nomes in mercados.df['mercado'].to_list():
            if nomes not in option:
                index2drop.append(mercados.df.loc[mercados.df['mercado'] == nomes].index[0])
        
        newdf = mercados.df.drop(index=index2drop, inplace=False)

        pie = alt.Chart(newdf).mark_arc(innerRadius=100, tooltip=True).encode(
            theta="total:Q",
            color="mercado:N"
        )
        #.configure(tooltipFormat={"numberFormat": "R$.2f"}, customFormatTypes=True)
        st.altair_chart(pie)
    else:
        st.write("Escolha algum supermercado da lista")

def historia_item():

    st.markdown("#### Histórico de preços.")
    st.markdown("Escolha produtos para verificar seus preços ao longo do tempo")

    valor_por_item = reais_per_item()

    item_df = DataFrameOperations(valor_por_item)

    option = st.multiselect(
        "Selecione os items:",
        item_df.df['item'].str.lower().unique().tolist(),
    )

    if option:

        filtered_data = pd.DataFrame(columns=["item", "data_compra", "preco_unidade", "preco_total", "local"])

        for itens in option:
            newdf = item_df.df.loc[item_df.df["item"].str.lower() == itens.lower()]
            filtered_data = pd.concat([filtered_data, newdf])
        
        filtered_data.sort_values(by=["data_compra"], inplace=True)


        history = alt.Chart(filtered_data).mark_point(tooltip=True, size=200, filled=True).encode(
            alt.X('data_compra'),
            alt.Y('preco_unidade'),
            color='local',
        ).interactive()
            # #.configure(tooltipFormat={"numberFormat": "R$.2f"}, customFormatTypes=True)

        st.altair_chart(history)



if __name__ == "__main__":

    data_op = database_operations('/home/gustavo/controle_precos/backend/db.sqlite3')

    st.title("Explorador de Notas Fiscais")

    valor_mes_personalizado()
    valor_mercado_personalizado() 
    historia_item()

    data_op.close()