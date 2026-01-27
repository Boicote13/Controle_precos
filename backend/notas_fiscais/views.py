# Create your views here.
from django.core.files.storage import FileSystemStorage
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import (
    FileFieldForm,
    NotaFiscalForm,
    ItemNotaFiscalForm,
    SupermercadoForm,
)
from .models import NotaFiscal, Supermercado, ItemNotaFiscal
from .scripts.arquivoPdatabase import *

from controle_precos.settings import NOTA_TITLE, MODEL


def adicionar_nota(request):

    supermercados = Supermercado.objects.filter().all()

    if request.method == 'POST':
        form = NotaFiscalForm(request.POST)
        if form.is_valid():
            nota_fiscal = form.save()
            return redirect('adicionar_itens', nota_id=nota_fiscal.id)
    else:
        form = NotaFiscalForm()

    return render(
        request,
        'notas_fiscais/adicionar_nota.html',
        {
            'supermercados': supermercados,
            'form': form,
        },
    )


class AdicionarNotaArquivo(FormView):
    form_class = FileFieldForm
    template_name = 'notas_fiscais/adicionar_nota_arquivo.html'
    success_url = reverse_lazy("lista_notas")

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = super().get_form()
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        notas_f = form.cleaned_data["file_field"]
        db_ops = DatabaseOperations(DATABASES["default"]["NAME"])
        soup = HtmlAnalyser()

        for file in notas_f:

            soup.htmlfile = file

            if soup.validate_content() == True:

                dados_nota = soup.obtain_notas_data()

                if db_ops.check_datatypes(**dados_nota):

                    mercado = db_ops.get_or_create_supermercado(
                        name_adress=dados_nota['supermercado_id']
                    )
                    nota_id = db_ops.insert_nota2db(
                        nota_infos=dados_nota, mercado_id=mercado
                    )

                dados_items = soup.obtain_items_data(nota=nota_id)

                if db_ops.check_datatypes(*dados_items):

                    db_ops.insert_items2db(dados_items)

            else:
                print(file)
                print('skipping file...')
        
        # db_ops.close()

        return super().form_valid(form)


def adicionar_itens(request, nota_id):

    nota_fiscal = get_object_or_404(NotaFiscal, id=nota_id)

    num = int(nota_fiscal.total_items)

    ItemNotaFiscalFormSet = inlineformset_factory(
        NotaFiscal,
        ItemNotaFiscal,
        form=ItemNotaFiscalForm,
        exclude=['supermercado'],
        extra=num,
        can_delete=False,
    )

    if request.method == 'POST':
        formset = ItemNotaFiscalFormSet(request.POST, instance=nota_fiscal)
        if formset.is_valid():
            formset.save()
            return redirect('detalhe_nota', nota_id=nota_fiscal.id)
        else:
            return redirect('lista_notas')
    else:
        formset = ItemNotaFiscalFormSet(instance=nota_fiscal)

    return render(
        request,
        'notas_fiscais/adicionar_itens.html',
        {'nota_fiscal': nota_fiscal, 'formset': formset},
    )


def detalhe_nota(request, nota_id):

    nota_fiscal = get_object_or_404(NotaFiscal, id=nota_id)

    items = ItemNotaFiscal.objects.filter(nota_fiscal=nota_fiscal)

    return render(
        request,
        'notas_fiscais/detalhe_nota.html',
        {
            'nota_fiscal': nota_fiscal,
            'items_queryset': items,
        },
    )


def criar_supermercado(request):

    if request.method == 'POST':
        form = SupermercadoForm(request.POST)

        if form.is_valid():
            supermercado = form.save()

            return_to_nota = request.GET.get('return_to_nota', 'false')
            if return_to_nota == 'true':
                return redirect(
                    f"{reverse('adicionar_nota')}?supermercado={supermercado.id}"
                )

            return redirect('lista_mercado')
    else:
        form = SupermercadoForm()

    # print(form)

    return render(
        request,
        'notas_fiscais/criar_supermercado.html',
        {
            'form': form,
        },
    )


class ListaNotas(ListView):
    template_name = "notas_fiscais/lista_notas.html"
    paginate_by = 30
    model = NotaFiscal


class ListaItens(ListView):
    template_name = "notas_fiscais/lista_items.html"
    paginate_by = 30
    model = ItemNotaFiscal


class ListaSupermercados(ListView):
    template_name = "notas_fiscais/lista_supermercado.html"
    paginate_by = 30
    model = Supermercado


def home_page(request):

    notas = NotaFiscal.objects.select_related().filter()[:10]

    items = ItemNotaFiscal.objects.order_by('nota_fiscal__data_emissao')[:10]

    mercado_data = {}

    for mercado in Supermercado.objects.all()[:10]:

        # qs_notas_mercadoX = NotaFiscal.objects.filter(supermercado=mercado.id)
        # print(f'mercado -> {mercado}')
        # print(
        #     f'mercado.id -> {mercado.id}\ntype(mercado.id) -> {type(mercado.id)}'
        # )

        # print(len(NotaFiscal.objects.filter(supermercado=mercado.id)))

        # print(qs_notas_mercadoX)

        mercado_data[mercado.nome] = len(
            NotaFiscal.objects.filter(supermercado=mercado.id)
        )

    return render(
        request,
        'notas_fiscais/home.html',
        {'notas': notas, 'items': items, 'data': mercado_data},
    )
