# Create your views here.
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from .forms import NotaFiscalForm, ItemNotaFiscalForm, SupermercadoForm
from .models import NotaFiscal, Supermercado, ItemNotaFiscal

def adicionar_nota(request):

    supermercados = Supermercado.objects.filter().all()

    if request.method == 'POST':
        form = NotaFiscalForm(request.POST)
        if form.is_valid():
            nota_fiscal = form.save()
            return redirect('adicionar_itens', nota_id=nota_fiscal.id)
    else:
        form = NotaFiscalForm()

    
    return render(request, 'notas_fiscais/adicionar_nota.html', {
        'supermercados' : supermercados,
        'form': form,
    })

def adicionar_itens(request, nota_id):

    nota_fiscal = get_object_or_404(NotaFiscal, id=nota_id)

    num = int(nota_fiscal.total_items)

    ItemNotaFiscalFormSet = inlineformset_factory(
            NotaFiscal, 
            ItemNotaFiscal,
            form=ItemNotaFiscalForm,
            exclude=['supermercado'],
            extra=num,
            can_delete=False
       )

    if request.method == "POST":
        formset = ItemNotaFiscalFormSet(request.POST, instance=nota_fiscal)
        if formset.is_valid():
            formset.save()
            return redirect('detalhe_nota', nota_id=nota_fiscal.id)
        else:
            return redirect('lista_notas')
    else:
        formset = ItemNotaFiscalFormSet(instance=nota_fiscal)

    return render(request, 'notas_fiscais/adicionar_itens.html', {
        'nota_fiscal': nota_fiscal,
        'formset' : formset
        })

def detalhe_nota(request, nota_id):

    nota_fiscal = get_object_or_404(NotaFiscal, id=nota_id)

    items = ItemNotaFiscal.objects.filter(nota_fiscal=nota_fiscal).values()
    
    return render(request, 'notas_fiscais/detalhe_nota.html', {
        'nota_fiscal' : nota_fiscal,
        'items_queryset' : items,
    })

def criar_supermercado(request):

    if request.method == 'POST':
        form = SupermercadoForm(request.POST)
        
        if form.is_valid():
            supermercado = form.save()
            
            return_to_nota = request.GET.get('return_to_nota', 'false')
            if return_to_nota == 'true':
                return redirect(f"{reverse('adicionar_nota')}?supermercado={supermercado.id}")
            
            return redirect('lista_mercado') 
    else:
        form = SupermercadoForm()
    
    return render(request, 'notas_fiscais/criar_supermercado.html', {
        'form': form,
    })



def lista_notas(request):
    notas = NotaFiscal.objects.all()
    return render(request, 'notas_fiscais/lista_notas.html', {'notas': notas})

def lista_itens(request):
    items = ItemNotaFiscal.objects.filter().all()
    return render(request, 'notas_fiscais/lista_items.html', {'items': items })

def lista_supermercados(request):
    supermercados  = Supermercado.objects.filter().all()
    return render(request, 'notas_fiscais/lista_supermercado.html', {'supermercados': supermercados})

def home_page(request):

    notas = NotaFiscal.objects.select_related().filter()[:10]

    itens = ItemNotaFiscal.objects.all()[:10]

    supermercado = Supermercado.objects.all()[:10]

    return render(request, 'notas_fiscais/home.html', {'notas' : notas, 'itens' : itens, 'supermercado' : supermercado })