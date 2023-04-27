import pprint
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



textopdf = ler_tranformar_pdftotexto('Diario_3681__13_3_2023.pdf')
dicionario_processos = transformar_texto_dict_processos_partes(textopdf)

df = pd.DataFrame([(key, *val) for key, values in dicionario_processos.items() for val in values])
print(df)
df.to_excel('Processos.xlsx', index=False)