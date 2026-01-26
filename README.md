# Controle de Preços

Este aplicativo tem como objetivo criar um banco de dados com notas fiscais de compras (mais especificamente mercados) com o qual onde o usuário poderá explorar informações de gastos mais detalhadamente.

### Cadastro de notas

A aplicação permite cadastrar notas fiscais de duas formas:
 1. Manualmente. Cada item com sua quantidade, valor unitário e unidade deve ser preenchido em um formulário disponível na aba Notas.
 2. Através do arquivo html da nota fiscal obtido no site da Fazenda (https://sped.fazenda.pr.gov.br/NFCe/webservices/sped/nfce/completa). Notas Fiscais Eletrônicas podem ser acessadas através da Chave de Acesso no site indicado, ou através do QRCode na nota. Com a chave de acesso o usuário pode acessar a nota através do navegador pelo computador e baixar o conteúdo completo da página. Este arquivo pode ser passado como input na aplicação.


 ### Exploração de dados

 Para explorar os dados inseridos no banco o usuário pode acessar a parte da aplicação voltada para geração de gráficos interativos com os dados. 

 
> - Se der certo a ideia é fazer outra IA pra subcategorias de alimento (parte nutricional: carboidratos, proteínas, lipidios, fibras)


# Recuperação de banco

Para recuperar o banco de um backup, primeiro vc precisa ter um backup:

```
python3 manage.py dumpdata --indent 2 > backups/backup_$(date +%Y%m%d).json
```

A partir do backup vc pode reconstruir o banco

```
rm db.sqlite3

#Cria o banco zerado
python3 manage.py migrate

#Insere tudo, CASO não tenha mudanças significativas nos Models
python3 manage.py loaddata backups/backup_20260114.json
```

A sugestão é que em cada mudança siginificativa de algum Model seja feito um backup pois pode haver conflito na hora de recuperar backups de bancos com estruturas diferentes.