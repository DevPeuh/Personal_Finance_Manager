# Personal Finance

Sistema completo de controle financeiro pessoal, desenvolvido em Python com Django. Permite gerenciar contas bancárias, registrar movimentações, transferências, visualizar relatórios e gráficos, tanto via interface web quanto por terminal.

## Funcionalidades

- **Cadastro de contas bancárias** (Itau, Nubank, Bradesco, Caixa, Santander, Inter)
- **Movimentação de dinheiro** (entradas e saídas, com categorias)
- **Transferência de saldo entre contas**
- **Desativação de contas** (com validação de saldo)
- **Relatórios financeiros** (entradas, saídas, saldo por período)
- **Visualização de gráficos** (valores das contas ativas)
- **Filtragem de movimentações** (por data, tipo e categoria)
- **Interface web (Django)** e **interface de terminal**
- **Autenticação de usuários**

## Tecnologias Utilizadas

- Python 3.13+
- Django 5.2.1
- PostgreSQL
- Matplotlib
- HTML
- CSS

### Interface Web

**Ainda em processo**

### Interface de Terminal

1. Execute:
   ```bash
   python terminal_interface.py
   ```
2. Siga as instruções do menu para gerenciar suas contas e movimentações pelo terminal.

## Estrutura do Projeto

- `core/` — App principal, contém modelos, views, urls e templates.
- `financeiro/` — Configurações do projeto Django.
- `terminal_interface.py` — Interface de linha de comando para operações financeiras.
- `requirements.txt` — Dependências do projeto.

## Telas e Funcionalidades

- **Dashboard:** Visão geral das contas e movimentações.
- **Cadastro de contas:** Escolha banco, valor inicial e status.
- **Transferências:** Entre contas do mesmo usuário.
- **Movimentações:** Entradas e saídas categorizadas.
- **Relatórios:** Filtragem por período, tipo e categoria.
- **Gráficos:** Visualização dos saldos das contas ativas.
