from django import forms
from .models import NotaFiscal, Supermercado, ItemNotaFiscal

"""
class NotaFiscalForm(forms.ModelForm):

    class Meta:
        model = NotaFiscal
        fields = ['supermercado', 'numero', 'data_emissao', 'valor_total']
        fields_classes = {
            'supermercado': Supermercado
        }
        widgets = {
            'data_emissao': forms.DateInput(attrs={'type': 'date'})
        }
"""

class ItemNotaFiscalForm(forms.ModelForm):
    class Meta:
        model = ItemNotaFiscal
        fields = ['produto', 'quantidade', 'preco_unitario', 'unidade_medida', 'categoria']

"""
Daqui pra baixo é deepseek
"""

class SupermercadoForm(forms.ModelForm):
    class Meta:
        model = Supermercado
        fields = ['nome', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do supermercado'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Endereço (Nome da rua, número. Cidade.)'
            }),
        }

class NotaFiscalForm(forms.ModelForm):
    supermercado_nome = forms.CharField(
        label='Supermercado',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome do supermercado...',
            'autocomplete': 'off',
            'id': 'supermercado-input'
        })
    )
    
    criar_novo_supermercado = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput(attrs={'id': 'criar-novo'})
    )
    
    class Meta:
        model = NotaFiscal
        fields = ['data_emissao', 'valor_total', 'total_items']
        exclude = ['supermercado']
        widgets = {
            'data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_items': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill supermarket name if editing existing instance
        if self.instance and self.instance.pk and self.instance.supermercado:
            self.fields['supermercado_nome'].initial = self.instance.supermercado.nome
    
    def clean(self):
        cleaned_data = super().clean()
        supermercado_nome = cleaned_data.get('supermercado_nome', '').strip()
        criar_novo = cleaned_data.get('criar_novo_supermercado', False)
        
        if not supermercado_nome:
            self.add_error('supermercado_nome', 'Este campo é obrigatório.')
            return cleaned_data
        
        try:
            # Try to get existing supermarket
            supermercado = Supermercado.objects.get(nome__iexact=supermercado_nome)
            cleaned_data['supermercado'] = supermercado
        except Supermercado.DoesNotExist:
            if criar_novo:
                # Create new supermarket
                supermercado = Supermercado.objects.create(nome=supermercado_nome)
                cleaned_data['supermercado'] = supermercado
            else:
                # Add error suggesting to create new
                self.add_error('supermercado_nome', 
                             f'Supermercado não encontrado. Marque a opção "Criar novo supermercado" se deseja adicionar.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.supermercado = self.cleaned_data.get('supermercado')
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance