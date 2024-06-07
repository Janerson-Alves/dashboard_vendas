#Importando as bibliotecas
import streamlit as st
import requests
import pandas as pd
import time

#Criando a função para converter os dados  para um csv
@st.cache_data #Armazenar caso nao seja  armazenado ou filtrado, ele nao precise converter novamente para csv
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8') #Não salva o index e converte para utf8

#Criando a função de mensagem de sucesso de download
def mensagem_sucesso():
    #Mostra a mensagem no app
    sucesso = st.success('Arquivo Baixado com sucesso!', icon="✅")
    time.sleep(5)
    #Remove  a mensagem apos 5 segundos do app
    sucesso.empty()

#Titulo da Pagina
st.title('DADOS BRUTOS')

#URL com os dados
url = 'https://labdados.com/produtos'

#Acessando os dados da API (ARMAZENA O RESULTADO DA REQUISIÇÃO DESSA URL)
response = requests.get(url)
#Transformando esses dados para um JSON e logo em seguida transformar em um DataFrame
dados = pd.DataFrame.from_dict(response.json())
#Alteração do formato da coluna  data da compra para datetime
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

#Selecionando as colunas que queremos no dataframe e descartando o  que nao vamos usar
with st.expander('Colunas'):
    #Usando multiselect para selecionar somente as colunas que queremos
    colunas = st.multiselect('Selecione as colunas', list(dados.columns))
    
#Criando os filtros das barras laterais
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    #Usando multiselect para selecionar somente as colunas que queremos
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000))

with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())

with st.sidebar.expander('Frete da venda'):
    frete = st.slider('Frete', 0,250, (0,250))

with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())

with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())

with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação da compra',1,5, value = (1,5))

with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())

with st.sidebar.expander('Quantidade de parcelas'):
    qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))


#Filtragem das colunas
query = '''
Produto in @produtos and \
`Categoria do Produto` in @categoria and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
@avaliacao[0]<= `Avaliação da compra` <= @avaliacao[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''
dados_filtrados = dados.query(query)
#Filtrando as colunas criadas no multiselect das colunas
dados_filtrados = dados_filtrados[colunas]


#mostrar a  tabela
st.dataframe(dados_filtrados)

#Colocando numero de linhas e coluna que ira aparecer na tela apartir de um texto
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

#Inserindo o botao de download no app
st.markdown('Escreva um nome para o arquivo')
#Colocando as colunas de nome do arquivo e  download
coluna1, coluna2 = st.columns(2)
#Criando a coluna 1 de nome do arquivo
with coluna1:
    nome_arquivo = st.text_input('', label_visibility= 'collapsed', value = 'dados') #Não mostra a label vazia
    #inserindo o nome do  arquivo.csv
    nome_arquivo += '.csv'

#COluna 2 de download
with coluna2:
    st.download_button('Fazer o download da tabela em csv', data = converte_csv(dados_filtrados), file_name= nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)
