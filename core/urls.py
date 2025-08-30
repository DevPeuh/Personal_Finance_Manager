from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_usuario, name='login'),
    path('cadastro/', views.cadastrar_usuario, name='cadastro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('contas/criar/', views.criar_conta, name='criar_conta'),
    path('contas/listar/', views.listar_contas, name='listar_contas'),
    path('contas/desativar/<int:conta_id>/', views.desativar_conta, name='desativar_conta'),
    path('contas/transferir/', views.tranferir_saldo, name='transferir_saldo'),
    path('contas/movimentar/', views.movimentar_dinheiro, name='movimentar_dinheiro'),
    path('contas/total/', views.total_contas, name='total_contas'),
    path('historicos/filtrar/', views.filtrar_movimentacoes, name='filtrar_movimentacoes'),
    path('relatorio/', views.relatorio_financeiro, name='relatorio_financeiro'),
    path('grafico/', views.criar_grafico, name='criar_grafico'),
    path('logout/', views.logout_usuario, name='logout'),
]
