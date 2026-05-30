#! /usr/bin/env python3

from django.core.files.uploadedfile import InMemoryUploadedFile
from pathlib import Path
import datetime
from typing import Union, Dict, List

from decimal import Decimal, getcontext

from bs4 import BeautifulSoup
from peewee import PostgresqlDatabase, SqliteDatabase
from playhouse.reflection import generate_models

from controle_precos.settings import *
from .model4category import CategoryGuesser


getcontext().prec = 3


class DatabaseOperations:
    def __init__(self, db_name: str, use_postgres: bool = None):
        self._use_postgres = use_postgres
        self.db = db_name
        self.__models_globally()

    @property
    def db(self) -> None:
        return self._db

    @db.setter
    def db(self, name: str) -> None:
        if self._use_postgres is not None:
            use_pg = self._use_postgres
        elif os.environ.get("USE_POSTGRES", "false").lower() == "true":
            use_pg = True
        elif not DEBUG:
            use_pg = True
        else:
            use_pg = False

        if use_pg:
            self._db = PostgresqlDatabase(
                name,
                user="gustavo",
                password=os.environ["POSTGRES_PASSWORD"],
                host="localhost"
            )
            print(f'Entrei no banco Postgres {self._db}')
        else:
            self._db = SqliteDatabase(name)
            print(f'Entrei no banco sqlite3 {self._db}')

    def __models_globally(self) -> None:
        self._db.connect()
        self.models = generate_models(self._db)

    def check_datatypes(self, *args, **kwargs) -> bool:

        if kwargs:
            if (
                isinstance(kwargs['data_emissao'], datetime.date)
                and isinstance(kwargs['valor_total'], Decimal)
                and isinstance(kwargs['total_items'], int)
                and isinstance(kwargs['supermercado_id'], tuple)
            ):

                print('NotaFiscal data types OK.')
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
                print('Check datatypes for data_emissao and valor_total')

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
                    print('Error in data types for the ItemNotaFiscal Model')
                    return False

    def insert_nota2db(
        self,
        nota_infos: Dict[str, Union[float, str, Decimal]],
        mercado_id: int,
    ) -> int:

        nota_query = self.models['notas_fiscais_notafiscal'].insert(
            data_emissao=nota_infos['data_emissao'],
            valor_total=nota_infos['valor_total'],
            total_items=nota_infos['total_items'],
            supermercado_id=mercado_id,
        )

        nota_id = nota_query.execute()

        return nota_id

    def insert_items2db(
        self, items_infos: List[Dict[str, Union[str, int, Decimal]]]
    ) -> None:
        self.models['notas_fiscais_itemnotafiscal'].insert_many(items_infos).execute()

    def get_or_create_supermercado(self, name_adress: tuple[str, str]) -> int:

        name, adress = name_adress

        mercado, created = self.models['notas_fiscais_supermercado'].get_or_create(
            nome=name, endereco=adress
        )

        print(f'mercado -> {mercado}\ncreated -> {created}')

        return mercado


class HtmlAnalyser:
    def __init__(
        self, htmlfile: Union[str, InMemoryUploadedFile] = None
    ) -> None:
        self.htmlfile = htmlfile
        self.guesser = CategoryGuesser()

    @property
    def htmlfile(self):
        return self._htmlfile

    @htmlfile.setter
    def htmlfile(self, html_path) -> Union[BeautifulSoup, None]:
        if isinstance(html_path, str):
            with open(html_path, 'r') as file:
                self._htmlfile = BeautifulSoup(file, 'html.parser')
        elif isinstance(html_path, InMemoryUploadedFile):
            self._htmlfile = BeautifulSoup(
                html_path.open().read().decode('utf-8'), 'html.parser'
            )
        else:
            print("Check the type for the html element to be analyzed.")
            print(f'Type passed to the setter: -> {type(html_path)}')
            self._htmlfile = None

    @property
    def guesser(self):
        return self._guesser

    @guesser.setter
    def guesser(self, model):
        if MODEL == '':
            self._guesser = model
            self._guesser.train_model(TRAINING_SET)
        else:
            print('Model selected from...')
            pass

    def validate_content(self):
        if self._htmlfile.find('title').get_text(strip=True) in NOTA_TITLE:
            return True
        else:
            print(self._htmlfile)
            print('The HTML content of this file is not the expected...')
            print(self._htmlfile.find('title').get_text(strip=True))
            return False

    def obtain_notas_data(self) -> Dict[str, Union[float, str, Decimal]]:

        dados_nota = {
            'valor_total': Decimal(),
            'data_emissao': '',
            'supermercado_id': tuple(),
            'total_items': int,
        }

        spans = self._htmlfile.select('div.txtCenter')[0]
        for i in spans.find_all('div')[-1]:
            endereco_nota = i.replace('\n', '').replace('\t', '')

        supermercado_nome = self._htmlfile.find(id='u20').string
        print(supermercado_nome)

        dados_nota['supermercado_id'] = (supermercado_nome, endereco_nota)

        for div in self._htmlfile.find('div', id='totalNota'):
            try:
                if div.label.string == 'Valor a pagar R$:':
                    div.span.string.replace(',', '.')
                    dados_nota['valor_total'] = Decimal(
                        div.span.string.replace(',', '.')
                    )
                elif div.label.string == 'Qtd. total de itens:':
                    dados_nota['total_items'] = int(div.span.string)

            except AttributeError:
                continue

        for strong in self._htmlfile.find('li').find_all('strong'):
            if strong.string == ' Emissão: ':
                dados_nota['data_emissao'] = datetime.datetime.strptime(
                    strong.next_sibling.string.split(' ')[0], '%d/%m/%Y'
                ).date()

        return dados_nota

    def obtain_items_data(
        self, nota: int
    ) -> List[Dict[str, Union[str, int, Decimal]]]:
        lista_dados_nota = []

        for itens in self._htmlfile.find('table').find_all('tr'):
            itens_data = {
                'nota_fiscal': nota,
                'produto': '',
                'quantidade': Decimal(),
                'preco_unitario': Decimal(),
                'unidade_medida': '',
                'categoria': '',
            }
            itens_data['produto'] = itens.select('span.txtTit')[
                0
            ].string.lower()

            itens_data['categoria'] = self._guesser.predict_cat(
                itens_data['produto']
            )

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

        return lista_dados_nota


class FileManager:
    def __init__(self, path2notes):
        self.path2notes = path2notes

    @property
    def path2notes(self) -> Path:
        return self._path2notes

    @path2notes.setter
    def path2notes(self, path) -> None:
        if Path(path).is_dir():
            self._path2notes = Path(path)
        else:
            raise NotADirectoryError

    def list_files(self) -> List[Path]:

        files2read = []

        for html_file in self.path2notes.glob('*.html'):
            temp_name = datetime.datetime.now().isoformat().split('.')[-1]
            new = html_file.parent.joinpath(f'nota_{temp_name}.html')
            html_file.rename(new)
            files2read.append(new)

        self.path2notes.joinpath('notas_processadas').mkdir(exist_ok=True)
        self.path2notes.joinpath('notas_nao_processadas').mkdir(exist_ok=True)

        return files2read

    def move_file_after_parsing(self, file_path: Path, processed: bool = True):
        if processed:
            target_processed = self._path2notes.joinpath(
                'notas_processadas', f'pro_{file_path.name}'
            )
            file_path.rename(target_processed)
        else:
            target_nonprocessed = self._path2notes.joinpath(
                'notas_nao_processadas', f'pro_{file_path.name}'
            )
            file_path.rename(target_nonprocessed)


def main(local) -> None:
    # DATABASES["default"]["NAME"]
    db_ops = DatabaseOperations('/home/gustavo/controle_precos/db.sqlite3')

    manager = FileManager(local)

    files_list = manager.list_files()

    soup = HtmlAnalyser()

    for file in files_list:

        soup.htmlfile = file

        if soup.validate_content() == True:

            dados_nota = soup.obtain_notas_data()

            if db_ops.check_datatypes(**dados_nota):

                mercado = db_ops.get_or_create_supermercado(
                    name_adress=dados_nota['supermercado_id']
                )
                nota_id = db_ops.insert_nota2db(
                    nota_infos=dados_nota, mercado_id=mercado
                )

            dados_items = soup.obtain_items_data(nota=nota_id)

            if db_ops.check_datatypes(*dados_items):

                db_ops.insert_items2db(dados_items)

            manager.move_file_after_parsing(file)

        else:

            print(file)
            print('skipping file...')
            manager.move_file_after_parsing(file, processed=False)
            print('\n\n')

    db_ops.db.close()


if __name__ == '__main__':
    # main('/home/gustavo/Documentos/notas/')
    print('oi')
