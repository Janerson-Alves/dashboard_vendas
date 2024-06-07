#Importando as bibliotecas
import streamlit as st
import pandas as pd
import requests
import plotly.express as px


#Colocando widemode como padrão
st.set_page_config(layout='wide')


#criando função para formatação de numero
def formata_numero(valor, prefixo = ''):
    #Laço para passar nada caso seja menor que mil
    for unidade in ['', 'mil']:
        #Verifica se o valor e menor que 1000
        if valor < 1000:
            #Faz a condição, retorna o prefixo, o valor formatado e a unidade
            return f'{prefixo} {valor:.2f} {unidade}'
        #Caso sea maior que 1000 ele pega o valor e divide por 1000
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


#Adicionando um titulo a página e passsando um emoji de carrinho
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

#Fazendo leitura de dados a partir de uma API GET
url = 'https://labdados.com/produtos'

#Lista de opções para o select box
regioes =  ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
#Criando a  barra lateral
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)
#Se a filtragem for brasil ela não faz nenhuma filtragem
if regiao == 'Brasil':
    regiao = ''

#Filtragem dos anos
todos_anos = st.sidebar.checkbox('Dados de todo o periodo', value= True)
if todos_anos:
    ano = ''
else:
    #Criando slider
    ano = st.sidebar.slider('Ano', 2020, 2023)

#Dicionario para identificar o valor região para regiões do selectbox
query_string = {'regiao': regiao.lower(), 'ano': ano}


#Acessando os dados da API (ARMAZENA O RESULTADO DA REQUISIÇÃO DESSA URL)
response = requests.get(url, params=query_string)

#Transformando esses dados para um JSON e logo em seguida transformar em um DataFrame
dados = pd.DataFrame.from_dict(response.json())
#Alteração do formato da coluna  data da compra para datetime
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= "%d/%m/%Y")

#Filtro dos vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
#Caso não selecione nenhum vendedor
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

#Construindo gráfico de mapa usando o plotly
##Tabelas
#criando a tabela de receita Somando a receita de cada um dos estados
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
#Criando  a tabela de latitude e longitude e agrupar as tabelas
receita_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)


#Criando uma datela com index, e agrupando por meses
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'M'))['Preço'].sum().reset_index()
#criando uma coluna com a informação do mês e outra com a informação do ano
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

#Criando uma tabela com as informações da receita para cada uma das categorias e ordenando os valores
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)


#Tabelas de quantidade de vendas
#vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

#Tabela de quantidade de vendas por estado
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)
#Tabela de quantidade de vendas mensal
vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

#Tabela de quantidade de vendas por categoria de produtos
vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

##Construindo  gráficos
fig_mapa_receita = px.scatter_geo(receita_estados, #Nome da tabela que vai ser usada
                                  lat = 'lat', #Coluna latitude da tabela
                                  lon= 'lon', #Coluna  Longitude da tabela
                                  scope= 'south america', #Mostrar so a america do sul
                                  size = 'Preço', #Tamanho do circulo do gráfico com base no valor do preço
                                  template= 'seaborn', #Template do formato do gráfico
                                  hover_name= 'Local da compra', #Animação para quando passar o mouse em cima do estado trazer as informações
                                  hover_data= {'lat': False, 'lon': False}, #Removendo latitude e longitude do padrão quando trazer as informações do estado
                                  title = 'Receita por estado', #Titulo do gráfico
                                  )


#Grafico de linhas
fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes', #Valor do X
                             y = 'Preço', #Valor do Y
                             markers= True, #Marcador por pontos por mês 
                             range_y=(0, receita_mensal.max()),#Fazendo o grafico começar do zero e indo ate o maximo da receita mensal
                             color= 'Ano', #Alterando a cor  com base na informação do ano
                             line_dash= 'Ano', #Alterando formato da linha conforme o ano
                             title= 'Receita mensal', #Titulo do gráfico
                             )

#Alterando o nome do eixo x
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

#Grafico de barras com 5  primeiros estados
fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto=True, #Valor da receita em cima de cada uma das colunas
                             title='Top estados (receita)'
                             )


#Alterando o nome do eixo y
fig_receita_estados.update_layout(yaxis_title = 'Receita')

#Gráfico de  barras ccom as categorias
fig_receita_categorias = px.bar(receita_categorias,
                                text_auto=True,
                                title='Receita por categoria'
                                )

#Gráfico d e mapa com as vendas
fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )


#Grafico de  linhas com a venda mensal
fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')

fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')


#Grafico de barras com a vendas de cada estado
fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados'
)

fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

#Alterando o nome do eixo y
fig_receita_estados.update_layout(yaxis_title = 'Receita')

#Criando as abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    #Construindo as colunas para colocar as metricas
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        #Construindo a metrica com a soma total das vendas e a quantidade total de vendas
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        #Chamando a figura para mostra na tela do app
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        #Chamando a figura para mostra na tela do app
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

with aba3:
    #Mostrando quantidade de vendedores no app
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    #Construindo as colunas para colocar as metricas
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        #Construindo a metrica com a soma total das vendas e a quantidade total de vendas
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        #Criando o gráfico dentro da aba
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x = 'sum', #Soma total da receita
                                        y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto= True,
                                        title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
                #Criando o gráfico dentro da aba
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x = 'count', #Soma total da receita
                                        y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto= True,
                                        title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores)

