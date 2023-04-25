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
        lista_linhas.append([lines])
        dict_processo[processo] = lista_linhas
        if 'PODER JUDICIÁRIO' in lines:
            i = 0
            lista_linhas =[]

pprint.pprint(dict_processo)

#
# for key in dict_processo:
#     print(key, dict_processo[key])
#     for item in dict_processo[key]:
#         if 'AUTOR' in item[0]:
#             item[0] = item[0].replace('AUTOR ', '')
#
#             print(item)
