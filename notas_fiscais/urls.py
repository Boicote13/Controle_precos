from django.urls import path
from . import views

# app_name = 'notas_fiscais'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('adicionar/', views.adicionar_nota, name='adicionar_nota'),
    path('supermercado/novo/', views.criar_supermercado, name='criar_supermercado'),
    path('lista/', views.lista_notas, name='lista_notas'),
    path('lista_mercado/', views.lista_supermercados, name='lista_mercado'),
]