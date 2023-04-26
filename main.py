import pprint
import PyPDF2
import re
import pandas as pd


pdffile = open('Diario_3681__13_3_2023.pdf', 'rb')

pdfreader = PyPDF2.PdfReader(pdffile)

num_pages = len(pdfreader.pages)
count = 2067
text = ""

while count < 2090:
  pageObj = pdfreader.pages[count]
  count += 1
  print(str(count))
  text += pageObj.extract_text()

textoseparado = text.split('\n')
lista_linhas = []
dict_processo = {}
i = 0
processo = ''
for j, lines in enumerate(textoseparado):
    if 'Processo Nº ATOrd' in lines and i == 0:
        processo = lines + ' $$ ' + str(j)
        i = 1
    elif i == 1:
        lista_linhas.append(lines)
        if 'PODER JUDICIÁRIO' in lines:
            lista_linhas.pop()
            texto = ' '. join(lista_linhas)
            lista_linhas= []
            lista_linhas.append(texto)
            dict_processo[processo] = lista_linhas
            i = 0
            lista_linhas =[]


# pprint.pprint(dict_processo)

for key in dict_processo:
    substring = []
    padrao = re.compile(r'(AUTOR|ADVOGADO|RÉU|TESTEMUNHA)')
    resultado = re.finditer(padrao, dict_processo[key][0])
    for match in resultado:
        start = match.end()
        try:
            end = next(resultado).start()
        except:
            end = None
        substring.append([match.group() + dict_processo[key][0][start:end]])

    dict_processo[key] = substring
    print(key)
    print(substring)
    print('-'*100)


    # dict_processo[key] = condensado
    # print(condensado)
# pprint.pprint(dict_processo)
