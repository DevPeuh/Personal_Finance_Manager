import base64 
from io import BytesIO 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import *
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Sum
import matplotlib.pyplot as plt

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

def login_usuario(request):
    if request.method == 'POST':
        nome_usuario = request.POST.get('nome_usuario')
        senha = request.POST.get('senha')
        usuario = authenticate(request, nome_usuario=nome_usuario, senha=senha) 

        if usuario:
            login(request, usuario)
            return redirect('dashboard')
        else:
            return render(request, 'core/dashboard.html', {'error': 'Usuário ou senha inválidos.'})
                          
    return render(request, 'core/login.html') # caso não seja POST, renderiza o formulário de login

def cadastrar_usuario(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        nome_usuario = request.POST.get('nome_usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # Validações
        if senha != confirmar_senha:
            return render(request, 'core/cadastro.html', {'error': 'As senhas não coincidem!'})
        
        if User.objects.filter(nome_usuario=nome_usuario).exists(): # Verifica se o nome de usuário já existe
            return render(request, 'core/cadastro.html', {'error': 'Nome de usuário já existe!'} )
        
        if User.objects.filter(email=email).exists():
            return render(request, 'core/cadastro.html', {'error': 'Email já cadastrado!'})
        
        # Criar usuário
        usuario = User.objects.create_user(
            username=nome_usuario,
            email=email,
            password=senha,
            name=nome 
        )

        # Conta padrão para o usuário
        Conta.objects.create(
            usuario=usuario,
            valor=0,
            banco=Banco.NUBANK,
            status=Status.ATIVO
        )

        # Já fazer login após cadastrar
        login(request, usuario)
        return redirect('dashboard')
    
    return render(request, 'core/cadastro.html') # caso não seja POST, renderiza o formulário de cadastro

def logout_usuario(request):
    logout(request)
    return redirect('login')

@login_required
def criar_conta(request):
    if request.method == 'POST':
        banco = request.POST.get('banco')
        valor_str = request.POST.get('valor')
        status = request.POST.get('status')

        if not valor_str: # caso o campo valor esteja vazio
            return render(request, 'core/criar_conta.html', {
                'error': 'O campo é obrigátorio.',
                'bancos': Banco.choices,
                'status': Status.choices
            })
        
        try:
            valor = float(valor_str)
        except ValueError:
            return render(request, 'core/criar_conta.html', {
                'error': 'Informe um valor numérico válido.',
                'bancos': Banco.choices,
                'status': Status.choices
            })
        
        # Verifica se o usuário já tem uma conta nesse banco
        if Conta.objects.filter(usuario=request.user, banco=banco).exists():
            return render(request, 'core/criar_conta.html', {
                'error': 'Você já tem uma conta nesse banco',
                'bancos': Banco.choices,
                'status': Status.choices
            })
        
        Conta.objects.create(
            usuario=request.user, 
            valor=valor,
            banco=banco,
            status=status if status else Status.ATIVO # caso não selecione, padrão ATIVO
        )
        return redirect('listar_contas')
    
    # caso não seja POST, renderiza o formulário de criação de conta
    return render(request, 'core/criar_conta.html', {
        'bancos': Banco.choices, 
        'status': Status.choices
    })

@login_required
def listar_contas(request):
    total_contas = Conta.objects.filter(usuario=request.user)
    return render(request, 'core/listar_contas.html', {'contas': total_contas})

@login_required
def desativar_conta(request, conta_id):
    conta = Conta.objects.get(id=conta_id, usuario=request.user)

    if conta.status == Status.INATIVO:
        return render(request, 'core/listar_contas.html', {
            'error': 'Essa conta já está desativada',
            'contas': Conta.objects.filter(usuario=request.user) 
        })
    
    if conta.valor > 0:
        return render(request, 'core/listar_contas.html', {
            'error': 'Essa conta não pode ser desativada pois possui saldo positivo',
            'contas': Conta.objects.filter(usuario=request.user) 
        })
    
    conta.status = Status.INATIVO
    conta.save()
    return redirect('listar_contas')

@login_required
def tranferir_saldo(request):
    if request.method == 'POST':
        conta_saida_id = request.POST.get('conta_saída')
        conta_entrada_id = request.POST.get('conta_entrada')
        valor_str = request.POST.get('valor')

        if not valor_str:
            return render(request, 'core/transferir_saldo.html', {
                'error': 'O campo é obrigatório.',
                'contas': Conta.objects.filter(usuario=request.user, status=Status.ATIVO)
            })
        
        try:
            valor = float(valor_str)
        except ValueError:
            return render(request, 'core/transferir_saldo.html', {
                'error': 'Informe um valor numérico válido.',
                'contas': Conta.objects.filter(usuario=request.user, status=Status.ATIVO)
            })


        conta_saida = Conta.objects.get(id=conta_saida_id, usuario=request.user)
        conta_entrada = Conta.objects.get(id=conta_entrada_id, usuario=request.user)

        if conta_saida.status == Status.INATIVO:
            return render(request, 'core/tranferir_saldo.html', {
                'error': 'Conta de saída está INATIVA.',
                'contas': Conta.objects.filter(usuario=request.user, status=Status.ATIVO)
            })
        
        if conta_saida.valor < valor:
            return render(request, 'core/tranferir_saldo.html', {
                'error': 'Saldo insuficiente.',
                'contas': Conta.objects.filter(usuario=request.user, status=Status.ATIVO)
            })
        conta_saida.valor -= valor
        conta_entrada.valor += valor
        conta_saida.save()
        conta_entrada.save()

        return redirect('listar_contas')
    
    contas = Conta.objects.filter(usuario=request.user, status=Status.ATIVO)
    return render(request, 'core/tranferir_saldo.html', {'contas': contas})

@login_required
def movimentar_dinheiro(request):
    if request.method == 'POST':
        conta_id = request.POST.get('conta')
        valor_str = request.POST.get('valor')
        tipo = request.POST.get('tipo')
        categoria = request.POST.get('categoria')

        if not valor_str:
            return render(request, 'core/movimentar_dinheiro.html', {
                'error': 'O campo é obrigatório.',
                'contas': Conta.objects.filter(usuario=request.user, status=Status.ATIVO)
            })
        
        try:
            valor = float(valor_str)
        except ValueError:
            return render(request, 'core/movimentar_dinheiro.html', {
                'error': '?Informe um valor numérico válido.',
                'contas': Conta.objects.filter(usuario=request.user, status=Status.ATIVO)
            })
        
        conta = Conta.objects.get(id=conta_id, usuario=request.user)

        if conta.status == Status.INATIVO:
            return render(request, 'core/movimentar_dinheiro.html', {
                'error': 'Conta inativa.',
                'contas': Conta.objects.filter(usuario=request.user, status=Status.ATIVO)
            })
        if valor < 0 and conta.valor < abs(valor):
            return render(request, 'core/movimentar_dinheiro.html', {
                'error': 'Saldo insuficiente.',
                'contas': Conta.objects.filter(usuario=request.user, status=Status.ATIVO)
            })
        if tipo == Tipos.ENTRADA:
            conta.valor += valor
        else:
            if conta.valor < valor:
                return render(request, 'core/movimentar_dinheiro.html', {
                    'error': 'Saldo insuficiente.',
                    'contas': Conta.objects.filter(usuario=request.user, status=Status.ATIVO)
                })
            conta.valor -= valor

        conta.save()

        Historico.objects.create(
            conta=conta,
            tipo=tipo,
            categoria=categoria,
            valor=valor,
            data=datetime.now()
        )

        return redirect('listar_contas')
    contas = Conta.objects.filter(usuario=request.user, status=Status.ATIVO)
    return render(request, 'core/movimentar_dinheiro.html', {
        'contas': contas,
        'tipos': Tipos.choices,
        'categorias': Categoria.choices
    })

@login_required
def total_contas(request):
    total = Conta.objects.filter(usuario=request.user).aggregate(Sum('valor'))['total'] or 0
    return render(request, 'core/total_contas.html', {'total': total})

@login_required
def filtrar_movimentacoes(request):
    if request.method == 'POST':
        data_inicio_str = request.POST.get('data_inicio')
        data_fim_str = request.POST.get('data_fim')
        tipo = request.POST.get('tipo')
        categoria = request.POST.get('categoria')

        data_inicio = datetime.strptime(data_inicio_str, '%d/%m/%Y').date() if data_inicio_str else None
        data_fim = datetime.strptime(data_fim_str, '%d/%m/%Y').date() if data_fim_str else None

        historicos = Historico.objects.filter(conta__usuario=request.user)
        if data_inicio and data_fim:
            historicos = historicos.filter(data__range=(data_inicio, data_fim))
        if tipo:
            historicos = historicos.filter(tipo=tipo)
        if categoria:
            historicos = historicos.filter(categoria=categoria)
        historicos = historicos.select_related('conta')

        return render(request, 'core/filtrar_movimentacoes.html', {
            'historicos': historicos,
            'data_inicio': data_inicio_str,
            'data_fim': data_fim_str,
            'tipo': tipo,
            'categoria': categoria,
        })

    return render(request, 'core/filtrar_movimentacoes.html')

@login_required
def relatorio_financeiro(request):
    if request.method == 'POST':
        data_inicio = datetime.strptime(request.POST['data_inicio'], '%d/%m/%Y').date()
        data_fim = datetime.strptime(request.POST['data_fim'], '%d/%m/%Y').date()
        
        historicos = Historico.objects.filter(
            conta__usuario=request.user,
            data__range=(data_inicio, data_fim)
        )
        
        entradas = historicos.filter(tipo=Tipos.ENTRADA).aggregate(Sum('valor'))['total'] or 0
        saidas = historicos.filter(tipo=Tipos.SAIDA).aggregate(Sum('valor'))['total'] or 0
        saldo = entradas - saidas
        
        return render(request, 'core/relatorio_financeiro.html', {
            'entradas': entradas,
            'saidas': saidas,
            'saldo': saldo,
            'data_inicio': data_inicio.strftime('%d/%m/%Y'),
            'data_fim': data_fim.strftime('%d/%m/%Y')
        })
    
    return render(request, 'core/relatorio_financeiro.html')

@login_required
def criar_grafico(request):
    contas = Conta.objects.filter(usuario=request.user, status=Status.ATIVO)
    
    if not contas.exists():
        return render(request, 'core/criar_grafico.html', {
            'error': 'Nenhuma conta ativa encontrada.',
            'contas': contas
        })
    bancos = [conta.get_banco_display() for conta in contas]
    valores = [conta.valor for conta in contas]

    plt.figure(figsize=(10, 6))
    plt.bar(bancos, valores, color='skyblue')
    plt.xlabel('Bancos')
    plt.ylabel('Valores R$')
    plt.title('Valores por Banco')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png).decode('utf-8')
    plt.close()

    return render(request, 'core/grafico.html', {'graphic': graphic})