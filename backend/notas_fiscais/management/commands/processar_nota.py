from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from notas_fiscais.scripts.arquivoPdatabase import HtmlAnalyser, DatabaseOperations


class Command(BaseCommand):
    help = "Processa um arquivo HTML de nota fiscal e insere os dados no banco"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Caminho do arquivo HTML da nota fiscal")

    def handle(self, *args, **options):
        file_path = options["file_path"]

        db_ops = DatabaseOperations(settings.DATABASES["default"]["NAME"])
        soup = HtmlAnalyser(htmlfile=file_path)

        if not soup.validate_content():
            raise CommandError("Conteúdo do arquivo não é uma nota fiscal válida")

        dados_nota = soup.obtain_notas_data()

        if not db_ops.check_datatypes(**dados_nota):
            raise CommandError("Tipos de dados da nota inválidos")

        mercado = db_ops.get_or_create_supermercado(
            name_adress=dados_nota["supermercado_id"]
        )
        nota_id = db_ops.insert_nota2db(
            nota_infos=dados_nota, mercado_id=mercado
        )

        dados_items = soup.obtain_items_data(nota=nota_id)

        if not db_ops.check_datatypes(*dados_items):
            raise CommandError("Tipos de dados dos itens inválidos")

        db_ops.insert_items2db(dados_items)

        db_ops.db.close()

        self.stdout.write(self.style.SUCCESS(f"Nota fiscal {nota_id} processada com sucesso!"))
