# Create your views here.
from django.shortcuts import render, redirect
from .forms import NotaFiscalForm, ItemNotaFiscalFormSet
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

def lista_notas(request):
    notas = NotaFiscal.objects.all().order_by('-data_emissao')
    return render(request, 'notas_fiscais/lista_notas.html', {'notas': notas})

def home_page(request):
    return render(request, 'notas_fiscais/home.html')