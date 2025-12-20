from django import forms
from .models import NotaFiscal, Supermercado, ItemNotaFiscal, Produto

class NotaFiscalForm(forms.ModelForm):
    class Meta:
        model = NotaFiscal
        fields = ['supermercado', 'numero', 'data_emissao', 'valor_total']
        widgets = {
            'data_emissao': forms.DateInput(attrs={'type': 'date'}),
        }

class ItemNotaFiscalForm(forms.ModelForm):
    class Meta:
        model = ItemNotaFiscal
        fields = ['produto', 'quantidade', 'preco_unitario', 'unidade_medida']
        
ItemNotaFiscalFormSet = forms.inlineformset_factory(
    NotaFiscal, 
    ItemNotaFiscal, 
    form=ItemNotaFiscalForm,
    extra=1,
    can_delete=False
)