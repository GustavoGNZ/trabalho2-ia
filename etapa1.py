import os
import PyPDF2
import re
import nltk
from nltk.corpus import stopwords
from collections import Counter
import spacy
import subprocess
import sys
from collections import defaultdict

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Modelo 'en_core_web_sm' não encontrado. Baixando agora...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

PASTA_PDFS = "artigos"

def extrair_texto_pdf_limpo(path):
    doc = PyPDF2.PdfReader(open(path, "rb"))
    total_paginas = len(doc.pages)

    linhas_por_pagina = []
    for pagina in doc.pages:
        texto = pagina.extract_text() or ""
        linhas = [l.strip() for l in texto.splitlines() if l.strip()]
        linhas_por_pagina.append(linhas)

    contador_linhas = defaultdict(int)
    for linhas in linhas_por_pagina:
        linhas_unicas = set(linhas)
        for linha in linhas_unicas:
            contador_linhas[linha] += 1

    limiar = 0.8 * total_paginas  # descarta linhas que aparecem em 80%+ das páginas

    texto_limpo = ""
    for linhas in linhas_por_pagina:
        linhas_filtradas = [l for l in linhas if contador_linhas[l] < limiar]
        texto_limpo += " ".join(linhas_filtradas) + " "

    return texto_limpo

def preprocessar_texto(texto):
    doc = nlp(texto.lower())
    tokens = [token.lemma_ for token in doc if token.is_alpha and token.text not in stop_words]
    return tokens

def remover_referencias(texto):
    partes = re.split(r"\breferences\b", texto, flags=re.IGNORECASE)
    return partes[0], partes[1] if len(partes) > 1 else ""

def analisar_pdfs():
    todos_unigramas = []
    referencias = []

    for arquivo in os.listdir(PASTA_PDFS):
        if not arquivo.endswith(".pdf"):
            continue
        caminho = os.path.join(PASTA_PDFS, arquivo)
        print(f"Lendo {arquivo}...")
        texto = extrair_texto_pdf_limpo(caminho)

        corpo, ref = remover_referencias(texto)
        referencias.append(ref)

        tokens = preprocessar_texto(corpo)
        todos_unigramas.extend(tokens)

    cont_uni = Counter(todos_unigramas)

    print("\nTop 10 Unigramas:")
    for palavra, freq in cont_uni.most_common(10):
        print(f"{palavra}: {freq}")

    with open("referencias_extraidas.txt", "w", encoding="utf-8") as f:
        for ref in referencias:
            f.write(ref.strip() + "\n\n")

    return cont_uni

if __name__ == "__main__":
    analisar_pdfs()
