from django.db import models

# Create your models here.


# Vai precisar de alguns dados separados
'''
- 1 Supermercados:
    -> nome
    -> endereço

- 2 Produto:
    -> categoria
    -> subcategoria
    -> preço unitário ou preço kg
    -> Data da compra (vem da nota fiscal)

- 3 Nota fiscal:
    -> Data da compra
    -> Local (supermercado)
    -> produtos
'''

class Supermercado(models.Model):
    nome = models.CharField(max_length=100)
    # cnpj = models.CharField(max_length=18, blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Supermercados"
    
    def __str__(self):
        return self.nome

class NotaFiscal(models.Model):
    supermercado = models.ForeignKey(Supermercado, on_delete=models.CASCADE)
    data_emissao = models.DateField()
    total_items = models.IntegerField(default=1)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2,  default=0.00)
    
    class Meta:
        verbose_name_plural = "Notas Fiscais"
        ordering = ["-data_emissao"]
    
    def __str__(self):
        return f"Nota {self.pk} - {self.supermercado} - {self.data_emissao}"

class CategoriaProduto(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome

class ItemNotaFiscal(models.Model):
    nota_fiscal = models.ForeignKey(NotaFiscal, on_delete=models.CASCADE, related_name='itens')
    produto = models.CharField(max_length=50)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3, default=0.00)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unidade_medida = models.CharField(max_length=20, default='un')
    
    @property
    def preco_total(self):
        return self.quantidade * self.preco_unitario
    
    @property
    def data_emissao(self):
        return self.nota_fiscal.data_emissao
    
    class Meta:
        ordering = ["-nota_fiscal__data_emissao"]
    
    #def __str__(self):
    #    return f"{self.quantidade} x {self.produto} - {self.nota_fiscal}"
    


