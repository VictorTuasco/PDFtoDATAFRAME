import pprint
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
    count = 1
    text = ""

    while count < num_pages:
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


def pegando_info_webAPI_nome(lista_nomes, lista_processo):
    dict_info_pessoa = {}
    servico = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servico)

    navegador.get(r'https://www.apinformacao.net.br/access/acesso.php')
    navegador.find_element('id' , 'login-codigo').send_keys('4645a')
    navegador.find_element('id', 'login-senha').send_keys('jmadv')
    time.sleep(5)
    navegador.find_element('id', 'btn-login').click()
    time.sleep(5)
    for i, nome in enumerate(lista_nomes):
        nome = nome[4:44]
        navegador.get(r'https://www.apinformacao.net/apinformacao/endtel/index2.php')
        navegador.find_element('id', 'nome').send_keys(nome)
        navegador.find_element('name', 'Submit2').click()
        try:
            num_registros = navegador.find_element('xpath', '//*[@id="grid"]/tbody')
            num_registros = num_registros.find_elements('tag name', 'tr')
        except:
            continue
        if len(num_registros) == 1:
            try:
                navegador.get(navegador.find_element('xpath', '//*[@id="grid"]/tbody/tr/td[1]/a').get_attribute('href'))
                time.sleep(3)
                documento  = navegador.find_element('xpath', '//*[@id="return_1"]/div/div/div[1]/div[2]').text
                if '/0' in documento:
                    continue
                dict_info_pessoa[nome] = {'Nome': nome}
                dict_info_pessoa[nome]['Documento'] = documento
                # nome = navegador.find_element('xpath', '//*[@id="return_1"]/div/div/div[2]/div[2]').text
                # pai = navegador.find_element('xpath', '//*[@id="return_1"]/div/div/div[5]/div[2]').text
                # dict_info_pessoa[nome]['Nome do Pai'] = pai
                # mae = navegador.find_element('xpath', '//*[@id="return_1"]/div/div/div[4]/div[2]').text
                # dict_info_pessoa[nome]['Nome da Mãe'] = mae
                titulo = navegador.find_element('xpath', '//*[@id="return_1"]/div/div/div[2]/div[4]').text
                dict_info_pessoa[nome]['Titulo de Eleitor'] = titulo
                sexo = navegador.find_element('xpath', '//*[@id="return_1"]/div/div/div[3]/div[4]').text
                dict_info_pessoa[nome]['Sexo'] = sexo
                telefones = navegador.find_elements('class name', 'mr-2')
                list_tel = []
                for tel in telefones:
                    list_tel.append(tel.text)
                dict_info_pessoa[nome]['Telefone']  = list_tel
                div_emails = navegador.find_elements('xpath' , '//*[@id="consulta_4"]/div[2]')
                list_email = []
                for elementos in div_emails:
                    emails = elementos.find_elements('class name','my-1')
                    for email in emails:
                        list_email.append(email.text)
                dict_info_pessoa[nome]['Emails'] = list_email
                div_enderecos = navegador.find_elements('xpath', '//*[@id="return_6"]/div/div')
                list_endereco = []
                for elementos in div_enderecos:
                    enderecos = elementos.find_elements('class name', 'my-1')
                    for endereco in enderecos:
                        list_endereco.append(endereco.text)
                dict_info_pessoa[nome]['Endereço'] = list_endereco
                dict_info_pessoa[nome]['Processo'] = lista_processo[i]

            except:
                continue
        else:
            # print ('not ok')
            continue

    return dict_info_pessoa



# executando as funções
textopdf = ler_tranformar_pdftotexto('Diario.pdf')
dicionario_processos = transformar_texto_dict_processos_partes(textopdf)
dicionario_processos = pegar_processos_um_adv(dicionario_processos)


lista_valores = []
for key, values in dicionario_processos.items():
    for val in values:
        tupla_valores = (key, *val)
        lista_valores.append(tupla_valores)
    lista_valores.append(('Processo' + '-' * 70, 'Participantes'+ '-' * 70))

df = pd.DataFrame(lista_valores, columns= ['Processo', 'Participantes'])
df.to_excel('Processos.xlsx', index=False)

#pegando somente os reús
reu = df[df['Participantes'].str.contains('RÉU')]
lista_reus = reu['Participantes'].values
lista_processos = reu['Processo'].values


df = pd.DataFrame(pegando_info_webAPI_nome(lista_reus, lista_processos))
df = df.T
df.to_excel('Lead.xlsx', index=False)