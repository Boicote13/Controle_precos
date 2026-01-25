from django.urls import path
from . import views
from .views import AdicionarNotaArquivo, ListaItens, ListaNotas, ListaSupermercados

# app_name = 'notas_fiscais'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('adicionar/', views.adicionar_nota, name='adicionar_nota'),
    path('adicionar_arquivo/', AdicionarNotaArquivo.as_view(), name='adicionar_nota_arquivo'),
    path('<int:nota_id>/adicionar-itens', views.adicionar_itens, name='adicionar_itens'),
    path('<int:nota_id>/detalhes', views.detalhe_nota, name='detalhe_nota'),
    path('supermercado/novo/', views.criar_supermercado, name='criar_supermercado'),
    path('lista/', ListaNotas.as_view(), name='lista_notas'),
    path('lista_mercado/', ListaSupermercados.as_view(), name='lista_mercado'),
    path('lista_itens/', ListaItens.as_view(), name='lista_itens')
]