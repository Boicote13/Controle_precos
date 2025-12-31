# Create your views here.
from django.shortcuts import render, redirect
from .forms import NotaFiscalForm, ItemNotaFiscalFormSet, SupermercadoForm
from .models import NotaFiscal

def adicionar_nota(request):
    if request.method == 'POST':
        form = NotaFiscalForm(request.POST, request.FILES)
        formset = ItemNotaFiscalFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            nota = form.save()
            formset.instance = nota
            formset.save()
            return redirect('lista_notas')  # Vamos criar esta view depois
    else:
        form = NotaFiscalForm()
        formset = ItemNotaFiscalFormSet()
    
    return render(request, 'notas_fiscais/adicionar_nota.html', {
        'form': form,
        'formset': formset,
    })

def criar_supermercado(request):
    """
    View for creating new supermarket (standalone)
    """
    if request.method == 'POST':
        form = SupermercadoForm(request.POST)
        
        if form.is_valid():
            supermercado = form.save()
            
            # Check if we should return to invoice form
            return_to_nota = request.GET.get('return_to_nota', 'false')
            if return_to_nota == 'true':
                # Return to add invoice form with the new supermarket pre-selected
                return redirect(f"{reverse('adicionar_nota')}?supermercado={supermercado.id}")
            
            return redirect('lista_notas')  # Or wherever you list supermarkets
    else:
        form = SupermercadoForm()
    
    return render(request, 'notas_fiscais/criar_supermercado.html', {
        'form': form,
    })

def lista_notas(request):
    notas = NotaFiscal.objects.all().order_by('-data_emissao')
    return render(request, 'notas_fiscais/lista_notas.html', {'notas': notas})

def home_page(request):
    return render(request, 'notas_fiscais/home.html')