import os
import PyPDF2
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from collections import Counter
from nltk.util import ngrams
import spacy

# Baixar recursos do NLTK e carregar modelo SpaCy para português
nltk.download('stopwords')
nlp = spacy.load("pt_core_news_sm")

# Caminho da pasta com os PDFs
PASTA_PDFS = "artigos"

# Inicializadores
stop_words = set(stopwords.words("portuguese"))

def extrair_texto_pdf(path):
    texto = ""
    with open(path, "rb") as f:
        leitor = PyPDF2.PdfReader(f)
        for pagina in leitor.pages:
            texto += pagina.extract_text() or ""
    return texto

def preprocessar_texto(texto):
    doc = nlp(texto.lower())
    tokens = [token.lemma_ for token in doc if token.is_alpha and token.text not in stop_words]
    return tokens

def remover_referencias(texto):
    partes = re.split(r"\brefer[êe]ncias\b", texto, flags=re.IGNORECASE)
    return partes[0], partes[1] if len(partes) > 1 else ""

def gerar_ngrams(tokens, n=2):
    return [' '.join(grama) for grama in ngrams(tokens, n)]

def analisar_pdfs():
    todos_unigramas = []
    todos_bigramas = []
    todos_trigramas = []
    referencias = []

    for arquivo in os.listdir(PASTA_PDFS):
        if not arquivo.endswith(".pdf"):
            continue
        caminho = os.path.join(PASTA_PDFS, arquivo)
        print(f"Lendo {arquivo}...")
        texto = extrair_texto_pdf(caminho)

        corpo, ref = remover_referencias(texto)
        referencias.append(ref)

        tokens = preprocessar_texto(corpo)
        todos_unigramas.extend(tokens)
        todos_bigramas.extend(gerar_ngrams(tokens, 2))
        todos_trigramas.extend(gerar_ngrams(tokens, 3))

    # Contagem
    cont_uni = Counter(todos_unigramas)
    cont_bi = Counter(todos_bigramas)
    cont_tri = Counter(todos_trigramas)

    # Mostrar top 10
    print("\nTop 10 Unigramas:")
    for palavra, freq in cont_uni.most_common(10):
        print(f"{palavra}: {freq}")

    print("\nTop 10 Bigramas:")
    for bigrama, freq in cont_bi.most_common(10):
        print(f"{bigrama}: {freq}")

    print("\nTop 10 Trigramas:")
    for trigrama, freq in cont_tri.most_common(10):
        print(f"{trigrama}: {freq}")

    # Salvar referências extraídas
    with open("referencias_extraidas.txt", "w", encoding="utf-8") as f:
        for ref in referencias:
            f.write(ref.strip() + "\n\n")

    return cont_uni, cont_bi, cont_tri

if __name__ == "__main__":
    analisar_pdfs()
