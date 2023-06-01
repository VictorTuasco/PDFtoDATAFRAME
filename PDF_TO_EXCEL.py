import sys
import datetime
import PyPDF2
import re
import pandas as pd
from tqdm import tqdm


data_atual = datetime.datetime.now().strftime('%Y-%m-%d')

def ler_tranformar_pdftotexto(pdf):
    pdffile = open(pdf, 'rb')
    pdfreader = PyPDF2.PdfReader(pdffile)
    num_pages = len(pdfreader.pages)
    text = ""

    for count in tqdm(range(1, num_pages)):
        pageObj = pdfreader.pages[count]
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
df.to_excel(f'Processos -- {data_atual} -- .xlsx', index=False)

sys.exit()