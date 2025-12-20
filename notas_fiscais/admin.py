from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Supermercado, NotaFiscal, CategoriaProduto, Produto, ItemNotaFiscal

class ItemNotaFiscalInline(admin.TabularInline):
    model = ItemNotaFiscal
    extra = 1

@admin.register(NotaFiscal)
class NotaFiscalAdmin(admin.ModelAdmin):
    inlines = [ItemNotaFiscalInline]
    list_display = ('numero', 'supermercado', 'data_emissao', 'valor_total')
    list_filter = ('supermercado', 'data_emissao')
    search_fields = ('numero', 'supermercado__nome')

admin.site.register(Supermercado)
admin.site.register(CategoriaProduto)
admin.site.register(Produto)