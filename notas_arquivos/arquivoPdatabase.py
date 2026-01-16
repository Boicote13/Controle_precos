#! /usr/bin/env python3

import time
from pathlib import Path
import datetime
from typing import Union, Dict, List

from decimal import Decimal, getcontext

from bs4 import BeautifulSoup
from peewee import *
from playhouse.reflection import generate_models

# from settings import *

NOTA_TITLE = 'DOCUMENTO AUXILIAR DA NOTA FISCAL DE CONSUMIDOR ELETRÔNICA'
# import pandas as pd

getcontext().prec = 3


class DatabaseOperations:
    def __init__(self, db_path: str):
        self.db = db_path
        self.__models_globally()

    @property
    def db(self) -> None:
        return self._db

    @db.setter
    def db(self, db_path: str) -> None:
        self._db = SqliteDatabase(db_path)

    def __models_globally(self) -> None:
        self._db.connect()
        models = generate_models(self._db)
        globals().update(models)


    def check_datatypes(self, *args, **kwargs) -> bool:

        if kwargs:
            if isinstance(
                kwargs["data_emissao"], datetime.date
            ) and isinstance(kwargs["valor_total"], Decimal) and isinstance(
                kwargs["total_items"], int
            ) and isinstance(kwargs["supermercado_id"], int):
                
                print("NotaFiscal data types OK.")
                return True
                
            else:
                print(
                    f'data_emissao in memory: {kwargs["data_emissao"]} -> type: {type(kwargs["data_emissao"])}'
                )
                print(
                    f'valor_total in memory: {kwargs["valor_total"]} -> type: {type(kwargs["valor_total"])}'
                )
                print(
                    f'total_items in memory: {kwargs["total_items"]} -> type: {type(kwargs["total_items"])}'
                )
                print(
                    f'supermercado_id in memory: {kwargs["supermercado_id"]} -> type: {type(kwargs["supermercado_id"])}'
                )
                print("Check datatypes for data_emissao and valor_total")

                return False
        
        if args:
            for cada in args:

                if (
                    isinstance(cada['quantidade'], Decimal)
                    and isinstance(cada['preco_unitario'], Decimal)
                    and isinstance(cada['produto'], str)
                ):
                    
                    print('ItemNotaFiscal data types OK.')
                    return True

                else:
                    print(
                        'Check datatypes for quantidade, preco_unitario and produto'
                    )
                    print(
                        f'quantidade in memory: {cada["quantidade"]} -> type: {type(cada["quantidade"])}'
                    )
                    print(
                        f'preco_unitario in memory: {cada["preco_unitario"]} -> type: {type(cada["preco_unitario"])}'
                    )
                    print(
                        f'produto in memory: {cada["produto"]} -> type: {type(cada["produto"])}'
                    )
                    print("Error in data types for the ItemNotaFiscal Model")
                    return False
                
    def insert_nota2db(
            self,
            nota_infos: Dict[str, Union[float, str, Decimal]],
        ) -> int:

        nota_query = notas_fiscais_notafiscal.insert(
            data_emissao=nota_infos['data_emissao'],
            valor_total=nota_infos['valor_total'],
            total_items=nota_infos['total_items'],
            supermercado_id=nota_infos['supermercado_id'],
        )

        nota_id = nota_query.execute()

        return nota_id

    def insert_items2db(self, items_infos: List[Dict[str, Union[str, int, Decimal]]]) -> None:
        notas_fiscais_itemnotafiscal.insert_many(items_infos).execute()

def get_html(html_path) -> Union[BeautifulSoup, None]:
    with open(html_path, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')
        print(soup.find('title').get_text(strip=True))
        if soup.find('title').get_text(strip=True) == NOTA_TITLE:
            return soup
        else:
            print('The HTML content of this file is not the expected...')
            return None


def obtain_notas_data(hmtl_content: BeautifulSoup) -> Dict[str, Union[float, str, Decimal]]:

    dados_nota = {
        'valor_total': Decimal(),
        'data_emissao': '',
        'supermercado_id': int(),
        'total_items': int,
    }
    
    spans = hmtl_content.select('div.txtCenter')[0]
    for i in spans.find_all('div')[-1]:
        endereco_nota = i.replace('\n', '').replace('\t', '')

    supermercado_nome = hmtl_content.find(id='u20').string
    print(supermercado_nome)

    mercado, created = notas_fiscais_supermercado.get_or_create(
        nome=supermercado_nome, endereco=endereco_nota
    )

    print(f'mercado -> {mercado}\ncreated -> {created}')

    dados_nota['supermercado_id'] = int(mercado.id)

    for div in hmtl_content.find('div', id='totalNota'):
        try:
            if div.label.string == 'Valor a pagar R$:':
                div.span.string.replace(',', '.')
                dados_nota['valor_total'] = Decimal(
                    div.span.string.replace(',', '.')
                )
            elif div.label.string == 'Qtd. total de itens:':
                dados_nota['total_items'] = div.span.string

        except AttributeError:
            continue

    for strong in hmtl_content.find('li').find_all('strong'):
        if strong.string == ' Emissão: ':
            dados_nota['data_emissao'] = datetime.datetime.strptime(
                strong.next_sibling.string.split(' ')[0], '%d/%m/%Y'
            ).date()

    print(dados_nota)
    return dados_nota
    ...

def obtain_items_data(nota: int, html_content: BeautifulSoup) -> List[Dict[str, Union[str, int, Decimal]]]:
    lista_dados_nota = []

    for itens in html_content.find('table').find_all('tr'):
        itens_data = {
            'nota_fiscal': nota,
            'produto': '',
            'quantidade': Decimal(),
            'preco_unitario': Decimal(),
            'unidade_medida': '',
            'categoria': '',
        }
        itens_data['produto'] = itens.select('span.txtTit2')[
            0
        ].string.lower()
        itens_data['quantidade'] = Decimal(
            float(
                itens.select('span.Rqtd')[0]
                .get_text(strip=True)
                .split(':')[-1]
                .replace(',', '.')
            )
        )
        itens_data['unidade_medida'] = (
            itens.select('span.RUN')[0]
            .get_text(strip=True)
            .split(':')[-1]
            .lower()
        )
        itens_data['preco_unitario'] = Decimal(
            itens.select('span.RvlUnit')[0]
            .get_text(strip=True)
            .split(':')[-1]
            .replace(',', '.')
        )

        lista_dados_nota.append(itens_data)

    print(lista_dados_nota)
    return lista_dados_nota
    ...

def organize_files(path2files: Path) -> List[Path]:
    #path2files = Path('/home/gustavo/Documentos/notas/')
    files2read = []
    for html_file in path2files.glob('*.html'):
        temp_name = datetime.datetime.now().isoformat().split('.')[-1]
        new = html_file.parent.joinpath(f'nota_{temp_name}.html')
        html_file.rename(new)
        files2read.append(new)
        # print(html_file)
    path2files.joinpath('notas_processadas').mkdir(exist_ok=True)
    path2files.joinpath('notas_nao_processadas').mkdir(exist_ok=True)
    return files2read


def move_file_after_parsing(file_path: Path, processed: bool = True):
    if processed:
        target_processed = Path(
            f'/home/gustavo/Documentos/notas/notas_processadas/pro_{file_path.name}'
        )
        file_path.rename(target_processed)
    else:
        target_nonprocessed = Path(
            f'/home/gustavo/Documentos/notas/notas_processadas/pro_{file_path.name}'
        )
        file_path.rename(target_nonprocessed)



def main(local) -> None:
    db_ops = DatabaseOperations('/home/gustavo/controle_precos/db.sqlite3')

    files_list = organize_files(Path(local))

    for file in files_list:

        soup = get_html(file)

        print(type(soup))
        if soup:
            dados_nota = obtain_notas_data(hmtl_content=soup)
            if db_ops.check_datatypes(dados_nota):
                nota_id = db_ops.insert_nota2db(nota_infos=dados_nota)

            dados_items = obtain_items_data(nota=nota_id, html_content=soup)

            if db_ops.check_datatypes(dados_items):
                db_ops.insert_items2db(dados_items)
        
            db_ops.db.close()
        else:
            print("skipping file...")
            

    

        

        

        

        

        


if __name__ == '__main__':
    ...
    main("/home/gustavo/Documentos/notas/")
    
