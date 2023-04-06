import PyPDF2
import textract
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd

import pandas as pd

pdffile = open('Faturamento GOOffices-maio-2023.pdf', 'rb')

pdfreader = PyPDF2.PdfReader(pdffile)

num_pages = len(pdfreader.pages)
count = 0
text = ""

while count < num_pages:
    pageObj = pdfreader.pages[count]
    count += 1
    text += pageObj.extract_text()

textoseparado = text.split('\n')

lista_cliente = []
lista_descricao = []
for i, item in enumerate(textoseparado):
    if 'Vencimento:' in item:
        if 'Atenção:' in textoseparado[i - 1]:
            lista_cliente.append(textoseparado[i - 2])
        else:
            lista_cliente.append(textoseparado[i - 1])
    if 'Valor Final' in item:
        for j, cliente in enumerate(lista_cliente):
            lista_descricao = [textoseparado[textoseparado.index(cliente):j]]

print (lista_descricao)

#tokens = word_tokenize(text)
#punctuations = ['(',')',';',':','[',']',',']
#stop_words = stopwords.words('english')
#keywords = [word for word in tokens if not word in stop_words and not word in punctuations]
#print(keywords)