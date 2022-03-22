import re
import csv
import os
import pdfplumber
import requests
from bs4 import BeautifulSoup
import json

def readpdf(file):
  with pdfplumber.open(file) as temp:
    first_page = temp.pages[0] #Exporta apenas a primeira página do arquivo (Ainda não sou o Luiz Barsi kkk)
    teste = first_page.extract_text() #Extrai o texto da pagina
    data_pregao = re.search("([0-9]{2}/[0-9]{2}/[0-9]{4})", teste) #Busca a primera ocorrência de data
    #print(data_pregao.group(1))

    #Extrai todas as tabelas da primeira página
    tables = first_page.extract_tables(table_settings={"vertical_strategy": "lines",
                                                      "horizontal_strategy": "lines"})
    operacoes = []
    #Itera as tabelas encontradas
    for table in tables:
      #print(table[0][0])
      #Aqui tem o pulo do gato pra identificar se a tabela é a tabela das operações kkk
      #Meu mestre de python chega tremer
      if table[0][0]== '':
        print(table[0])
        #Estrutura os dados encotrados na tabela
        operacao = {
          'tipo_operacao' : table[0][2],
          'mercado' : table[0][3],
          'nome_ativo' : table[0][5],
          'quantidade' : int(table[0][7]),
          'pm' : table[0][8],
          'valor_total' : table[0][9],
          'data' : data_pregao.group(1)
        }
        operacoes.append(operacao)
    return operacoes

def criar_csv(operacoes):
  keys = operacoes[0].keys()

  with open('arquivo.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(operacoes)

def nome_acoes():
  #Web Scrapping para identificar os códigos das ações, visto que as notas de negociação da clear são fornecidas com o nome da empresa.
  ativos_b3 = []
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
  for i in range(ord('a'), ord('z')+1):
    html = requests.get('https://br.advfn.com/bolsa-de-valores/bovespa/{}'.format(chr(i).upper()), headers=headers).content
    soup = BeautifulSoup(html, 'lxml')
    #print(soup)
    table = soup.find('table', {'class' : 'atoz-link-bov'})
    #print(table)
    ativos = table.find_all('tr')[1:]
    for ativo in ativos:
      nome_ativo = (ativo.find_all('a')[0]).string
      codigo_ativo = (ativo.find_all('td')[1]).string
      ativob3 = {
        'codigo' : codigo_ativo.string,
        'nome' : nome_ativo.string
      }
      ativos_b3.append(ativob3)
      with open('lista_ativos.json', 'w', ) as output_file:
        output_file.write(json.dumps(ativos_b3))

  print(ativos_b3)


if __name__ == '__main__':
    #nome_acoes()
    directory = 'PDFs'      #Informa o caminho do diretório contendo os arquivos PDF
    operacoes_geral = []
    #Itera o diretório em busca dos arquivos
    for filename in os.scandir(directory):
      operacoes_nota = readpdf(filename.path)
      for operacao in operacoes_nota:
        operacoes_geral.append(operacao)
    print(operacoes_geral)
    criar_csv(operacoes_geral)

