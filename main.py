import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import PyPDF2
import re
import pandas as pd


def ler_tranformar_pdftotexto(pdf):
    pdffile = open(pdf, 'rb')
    pdfreader = PyPDF2.PdfReader(pdffile)
    num_pages = len(pdfreader.pages)
    count = 2067
    text = ""

    while count < 3269:
        pageObj = pdfreader.pages[count]
        count += 1
        print(str(count))
        text += pageObj.extract_text()
        textoseparado = text.split('\n')
    return textoseparado


def pegar_padroes(texto):
    substring = []
    padrao = re.compile(r'(AUTOR|ADVOGADO|RÉU|TESTEMUNHA|CUSTOS LEGIS|REQUERENTES|PERITO|INTERESSADO)')
    resultado = list(re.finditer(padrao, texto))
    for i, match in enumerate(resultado):
        start = match.end()
        try:
            next_match = resultado[i+1]
            end = next_match.start()
            substring.append([match.group() + texto[start:end]])
        except:
            try:
                substring.append([match.group() + texto[start:texto.find('Intimado')]])
            except:
                try:
                    substring.append([match.group() + texto[start:texto.find('Código')]])
                except:
                    substring.append([match.group() + texto[start:]])

    return (substring)


def transformar_texto_dict_processos_partes(texto):
    lista_linhas = []
    dict_processo = {}
    i = 0
    processo = ''
    for j, lines in enumerate(texto):
        if 'Processo Nº ATOrd' in lines and i == 0:
            processo = lines + ' $$ ' + str(j)
            i = 1
        elif i == 1:
            lista_linhas.append(lines)
            if 'PODER JUDICIÁRIO' in lines:
                lista_linhas.pop()
                texto = ' '. join(lista_linhas)
                lista_linhas= []
                lista_linhas.append(pegar_padroes(texto))
                dict_processo[processo] = lista_linhas[0]
                i = 0
                lista_linhas =[]
    return dict_processo


def pegar_processos_um_adv(dicionario):
    keys_to_remove = []
    for key, value in dicionario.items():
        count = 0
        for item in value:
            if "ADVOGADO" in item[0]:
                count += 1
        if count > 1:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del dicionario[key]

    return dicionario


# executando as funções
# textopdf = ler_tranformar_pdftotexto('Diario_3681__13_3_2023.pdf')
# dicionario_processos = transformar_texto_dict_processos_partes(textopdf)
# dicionario_processos = pegar_processos_um_adv(dicionario_processos)
#
#
# lista_valores = []
# for key, values in dicionario_processos.items():
#     for val in values:
#         tupla_valores = (key, *val)
#         lista_valores.append(tupla_valores)
#     lista_valores.append(('Processo' + '-' * 70, 'Participantes'+ '-' * 70))
#
# df = pd.DataFrame(lista_valores, columns= ['Processo', 'Participantes'])
# df.to_excel('Processos.xlsx', index=False)
#
# #pegando somente os reús
# reu = df[df['Participantes'].str.contains('RÉU')]
#
# lista_reus = reu['Participantes'].values + ' && ' + reu['Processo'].values
#
# for reu in lista_reus:
#     print(reu.strip('RÉU')[:reu.find('&&') - 3])

def pegando_info_webAPI_nome(lista_nomes):

    servico = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servico)

    navegador.get(r'https://www.apinformacao.net.br/access/acesso.php')
    navegador.find_element('id' , 'login-codigo').send_keys('4645a')
    navegador.find_element('id', 'login-senha').send_keys('jmadv')
    navegador.find_element('id', 'btn-login').click()
    time.sleep(5)
    navegador.get(r'https://www.apinformacao.net/apinformacao/endtel/index2.php')
    navegador.find_element('id', 'nome').send_keys('MARCO AURELIO FLORES CARONE')
    navegador.find_element('name', 'Submit2').click()
    num_registros = navegador.find_element('xpath', '//*[@id="grid-footer"]/div/div[2]/div/strong/h6').text
    if '2' not in num_registros:
        navegador.get(navegador.find_element('xpath', '//*[@id="grid"]/tbody/tr/td[1]/a').get_attribute('href'))
        time.sleep(5)
        documento  = navegador.find_element('xpath', '//*[@id="return_1"]/div/div/div[1]/div[2]').text
        nome = navegador.find_element('xpath', '//*[@id="return_1"]/div/div/div[2]/div[2]').text
        pai = navegador.find_element('xpath', '//*[@id="return_1"]/div/div/div[5]/div[2]').text
        mae = navegador.find_element('xpath', '//*[@id="return_1"]/div/div/div[4]/div[2]').text
        titulo = navegador.find_element('xpath', '//*[@id="return_1"]/div/div/div[2]/div[4]').text
        sexo = navegador.find_element('xpath', '//*[@id="return_1"]/div/div/div[3]/div[4]').text
        telefones = navegador.find_elements('class name', 'mr-2')
        for tel in telefones:
            print(tel.text)
        div_emails = navegador.find_elements('xpath' , '//*[@id="consulta_4"]/div[2]')
        for elementos in div_emails:
            emails = elementos.find_elements('class name','my-1')
            for email in emails:
                print(email.text)
        div_enderecos = navegador.find_elements('xpath', '//*[@id="return_6"]/div/div')
        for elementos in div_enderecos:
            enderecos = elementos.find_elements('class name', 'my-1')
            for endereco in enderecos:
                print (endereco.text)

    else:
        print ('not ok')
    time.sleep(100)
    return

pegando_info_webAPI_nome('teste')