import os 
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeiro.settings')
django.setup() 

from django.core.exceptions import ObjectDoesNotExist
from core.models import Conta, Historico, Banco, Status, Tipos, Categoria
from django.contrib.auth.models import User
from decimal import Decimal


class Interface:
    def __init__(self):
        self.usuario_atual = None
        self.menu_options = {
            1: self._criar_conta,
            2: self._desativar_conta,
            3: self._transferir_saldo,
            4: self._movimentar_dinheiro,
            5: self._total_contas,
            6: self._filtrar_movimentacoes,
            7: self._criar_grafico,
            8: self._gerar_relatorio,
            9: self._deletar_usuario,
            0: self._display_help,
        }

    def login(self):
        while True:
            nome = input('Nome de usuário: ')
            senha = input('Senha: ')
            
            try:
                usuario = User.objects.get(username=nome)
                if usuario.check_password(senha):
                    self.usuario_atual = usuario
                    print(f'Bem vindo, {nome}!')
                    break
                else:
                    print('Senha incorreta. Tente novamente.')
            except ObjectDoesNotExist:
                print('Usuário não encontrado. Deseja criar um novo? (s/n)')
                if input().lower() == 's':
                    self.usuario_atual = User.objects.create_user(
                        username=nome,
                        password=senha
                    )
                    self.usuario_atual.save()
                    print(f'Usuário {nome} criado com sucesso!')
                    break

    def start(self):
        self.login()
        while True:
            self._display_menu()
            try:
                choice = int(input('Escolha uma opção: '))
                if choice in self.menu_options:
                    self.menu_options[choice]()
                elif choice == 9:
                    print('Saindo...')
                    break
                else:
                    print('Opção inválida. Tente novamente.')
            except ValueError:
                print('Opção inválida. Digite um número.')
                return


    def _listar_contas(self):
        print('Contas disponíveis:')
        for conta in Conta.objects.filter(usuario=self.usuario_atual):
            print(f'{conta.id} - {conta.get_banco_display()} - R$ {conta.valor:.2f} - ({conta.get_status_display()})')

    def _criar_conta(self):
        print('Escolha um banco:')
        for banco in Banco:
            print(f'-- {banco.label} --') 
        banco = input('Banco: ').title() 
        valor = Decimal(input('Valor inicial: '))
        
        bancos_validos = [banco.value for banco in Banco]
        if banco not in bancos_validos:
            print('Banco inválido.')
            return
        
        try:
            conta = Conta.objects.create(
                usuario=self.usuario_atual,
                valor=valor,
                banco=banco,
                status = Status.ATIVO
            )
            print(f'Conta {conta.get_banco_display()} criada com sucesso!') 
        except:
            print(f'Erro: Conta {banco} já existe para o usuário {self.usuario_atual.username}')

    def _desativar_conta(self):
        self._listar_contas()
        id_conta = int(input('ID da conta a desativar: '))
        
        try:
            conta = Conta.objects.get(id=id_conta, usuario=self.usuario_atual)
            if conta.valor > 0:
                print('A conta ainda possui saldo.')
                return
            conta.status = Status.INATIVO
            conta.save()
            print(f'Conta {conta.get_banco_display()} desativada com sucesso!')
        except ObjectDoesNotExist:
            print('Conta não encontrada.')
            return

    def _transferir_saldo(self):
        self._listar_contas()
        id_conta_origem = int(input('ID da conta de origem: '))
        id_conta_destino = int(input('ID da conta de destino: '))
        valor = Decimal(input('Valor a transferir: '))
        
        try:
            conta_origem = Conta.objects.get(id=id_conta_origem, usuario=self.usuario_atual)
            conta_destino = Conta.objects.get(id=id_conta_destino, usuario=self.usuario_atual)
            
            if conta_origem.valor < valor:
                raise ValueError('Saldo insuficiente na conta de origem!')
            
            conta_origem.valor -= valor
            conta_destino.valor += valor
            
            conta_origem.save()
            conta_destino.save()
            
            Historico.objects.create(
                conta=conta_origem,
                tipo=Tipos.SAIDA.value,
                categoria='Transferência',
                valor=valor
            )
            Historico.objects.create(
                conta=conta_destino,
                tipo=Tipos.ENTRADA.value,
                categoria='Transferência',
                valor=valor
            )
            
            print('Transferência realizada com sucesso!')
        except ObjectDoesNotExist:
            print('Conta não encontrada.')
            return

    def _total_contas(self):
        contas = Conta.objects.filter(usuario=self.usuario_atual, status=Status.ATIVO)
        total = sum(conta.valor for conta in contas)
        print(f'Total de contas ativas: R$ {total:.2f}')

    def _filtrar_movimentacoes(self):
        self._listar_contas()
        id_conta = int(input('ID da conta: '))
        data_inicio = input('Data de início (YYYY-MM-DD): ')
        data_fim = input('Data de fim (YYYY-MM-DD): ')
        
        try:
            conta = Conta.objects.get(id=id_conta, usuario=self.usuario_atual)
            movimentacoes = Historico.objects.filter(
                conta=conta,
                data__range=(data_inicio, data_fim)
            )
            
            if not movimentacoes:
                print('Nenhuma movimentação encontrada nesse período.')
                return
            
            print(f'Movimentações da conta {conta.get_banco_display()}:')
            for mov in movimentacoes:
                print(f'{mov.data} - {mov.get_tipo_display()} - {mov.categoria} - R$ {mov.valor:.2f}')
        except ObjectDoesNotExist:
            print('Data inválida ou conta não encontrada.')
            return

    def _gerar_relatorio(self):
        contas = Conta.objects.filter(usuario=self.usuario_atual, status=Status.ATIVO)
        if not contas:
            print('Nenhuma conta ativa encontrada.')
            return
        
        print('Relatório Financeiro:')
        for conta in contas:
            print(f'Banco: {conta.get_banco_display()}')
            print(f'Saldo: R$ {conta.valor:.2f}')
            movimentacoes = Historico.objects.filter(conta=conta)
            if movimentacoes:
                print('Movimentações:')
                for mov in movimentacoes:
                    print(f'{mov.data} - {mov.get_tipo_display()} - {mov.categoria} - R$ {mov.valor:.2f}')
            else:
                print('Nenhuma movimentação registrada.')
            print('-' * 30)

    def _display_menu(self):
        print('\nMenu:')
        print('1. Criar conta')
        print('2. Desativar conta')
        print('3. Transferir saldo entre contas')
        print('4. Movimentar dinheiro')
        print('5. Total de contas ativas')
        print('6. Filtrar movimentações por data')
        print('7. Gerar relatório financeiro')
        print('8. Criar gráfico de contas ativas')
        print('9. Deletar usuário')
        print('0. Exibir ajuda')
        print('sair')

    def _display_help(self):
        print('\nAjuda:')
        print('1. Criar conta: Cria uma nova conta bancária.')
        print('2. Desativar conta: Desativa uma conta existente.')
        print('3. Transferir saldo: Transfere saldo entre contas.')
        print('4. Movimentar dinheiro: Registra uma movimentação de entrada ou saída.')
        print('5. Total de contas ativas: Exibe o total de todas as contas ativas.')
        print('6. Filtrar movimentações por data: Filtra movimentações de uma conta por período.')
        print('7. Gerar relatório financeiro: Gera um relatório detalhado das contas e movimentações.')
        print('8. Criar gráfico de contas ativas: Cria um gráfico com os valores das contas ativas.')
        print('0. Exibir ajuda: Mostra este menu de ajuda.')

    def _movimentar_dinheiro(self):
        self._listar_contas()
        id_conta = int(input('ID da conta: '))
        valor = Decimal(input('Valor movimentado: '))
        print('Tipos de movimentação:')

        for tipo in Tipos:
            print(f'--- {tipo.label} ({tipo.value}) ---')
        tipo_input = input('Tipo: ').upper().strip()

        if tipo_input not in [t.value for t in Tipos]:
            print('Tipo inválido.')
            return
        tipo = tipo_input
        
        if tipo == Tipos.SAIDA.value and valor <= 0:
            print('Valor de saída deve ser positivo.')
            return
        
        if tipo == Tipos.ENTRADA.value and valor <= 0:
            print('Valor de entrada deve ser positivo.')
            return
        
        print('Categorias:')
        for cat in Categoria:
            print(f'--- {cat.label} ---')
        categoria = input('Categoria: ').title().strip()
        
        try:
            conta = Conta.objects.get(id=id_conta, usuario=self.usuario_atual)
            
            if tipo == Tipos.SAIDA.value and conta.valor < valor:
                raise ValueError('Saldo insuficiente')
            
            Historico.objects.create(
                conta=conta,
                tipo=tipo,
                categoria=categoria,
                valor=valor
            )
            
            if tipo == Tipos.ENTRADA.value:
                conta.valor += valor
            else:
                conta.valor -= valor
            conta.save()
            
            print('Movimentação registrada com sucesso!')
        except:
            print(f"Erro: Conta não encontrada ou saldo insuficiente.")
            return

    def _criar_grafico(self):
        import matplotlib.pyplot as plt
        
        contas = Conta.objects.filter(usuario=self.usuario_atual, status=Status.ATIVO)
        if not contas:
            print('Nenhuma conta ativa encontrada.')
            return
        
        bancos = [conta.get_banco_display() for conta in contas]
        valores = [conta.valor for conta in contas]
        
        plt.bar(bancos, valores)
        plt.xlabel('Bancos')
        plt.ylabel('Valores (R$)')
        plt.title('Valores das Contas Ativas por Banco')
        plt.show()

    def _deletar_usuario(self):
        contas_ativas = Conta.objects.filter(usuario=self.usuario_atual, status=Status.ATIVO)
        contas_com_saldo = [conta for conta in contas_ativas if conta.valor > 0]
        if contas_com_saldo:
            print("Não é possível deletar o usuário: existem contas ativas com saldo.")
            for conta in contas_com_saldo:
                print(f"- {conta.get_banco_display()}: R$ {conta.valor:.2f}")
            return

        confirm = input(f"Tem certeza que deseja deletar sua conta de usuário ({self.usuario_atual.username})? Isso apagará todas as suas contas e movimentações. (s/n): ").lower().strip()
        if confirm != 's':
            print("Operação cancelada.")
            return
        try:
            self.usuario_atual.delete()
            print("Conta de usuário deletada com sucesso!")
            exit()
        except:
            print(f"Erro ao deletar usuário: {self.usuario_atual.username}")
            return

if __name__ == "__main__":
    Interface().start()