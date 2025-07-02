import os
import PyPDF2
import re
import nltk
from nltk.corpus import stopwords
from collections import Counter, defaultdict
import spacy
import subprocess
import sys

# #### Configuração inicial ####

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Modelo 'en_core_web_sm' não encontrado. Baixando agora...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

PASTA_PDFS = "artigos"

padroes = {
    "objetivo": re.compile(r"\b(objective|aim|purpose|goal)(s)? (of|this|the)? (study|article|research)?\b", re.IGNORECASE),
    "problema": re.compile(r"\b(problem|issue|challenge)(s)?\b", re.IGNORECASE),
    "metodo": re.compile(r"\b(method|methodology|interview(s)?|survey(s)?|content analysis|case study|experiment|approach|technique(s)?|) (were|was)? (conducted|used|realized|taken)?\b", re.IGNORECASE),
    "contribuicao": re.compile(r"\b(contribute(s)?|contribution|advances|adds|fills a gap) (to)?\b", re.IGNORECASE),
}

# #### Funções comuns ####

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

# #### Etapa 1: leitura, pré-processamento e top 10 unigramas ####

def etapa1_identificar_termos_mais_citados():
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

    return cont_uni, referencias

# #### Etapa 2: extrair objetivo, problema, método e contribuição ####

def etapa2_extrair_info_artigos():
    resultados = []

    for arquivo in os.listdir(PASTA_PDFS):
        if not arquivo.endswith(".pdf"):
            continue
        caminho = os.path.join(PASTA_PDFS, arquivo)
        print(f"Extraindo infos de {arquivo}...")

        texto = extrair_texto_pdf_limpo(caminho)
        corpo, _ = remover_referencias(texto)

        doc = nlp(corpo) # Processamento com spaCy

        objetivo = ""
        problema = ""
        metodo = ""
        contribuicao = ""

        # Verifica padrões em cada sentença
        for sentenca in doc.sents:
            if padroes["objetivo"].search(sentenca.text):
                objetivo += sentenca.text.strip() + ";;"
            if padroes["problema"].search(sentenca.text):
                problema += sentenca.text.strip() + ";;"
            if padroes["metodo"].search(sentenca.text):
                metodo += sentenca.text.strip() + ";;"
            if padroes["contribuicao"].search(sentenca.text):
                contribuicao += sentenca.text.strip() + ";;"


        resultados.append({
            "arquivo": arquivo,
            "objetivo": objetivo,
            "problema": problema,
            "metodo": metodo,
            "contribuicao": contribuicao,
        })

    return resultados

# #### Etapa 3: salvar dados extraídos ####

def etapa3_salvar_dados(dados_extraidos):
    with open("dados_extraidos.txt", "w", encoding="utf-8") as f:
        for info in dados_extraidos:
            f.write(f"Arquivo: {info['arquivo']}\n")
            f.write("Objetivo:\n")
            f.write(f"{info['objetivo']}\n\n")
            f.write("Problema:\n")
            f.write(f"{info['problema']}\n\n")
            f.write("Método:\n")
            f.write(f"{info['metodo']}\n\n")
            f.write("Contribuição:\n")
            f.write(f"{info['contribuicao']}\n\n")
            f.write("-" * 40 + "\n\n")

def salvar_referencias(referencias):
    with open("referencias_extraidas.txt", "w", encoding="utf-8") as f:
        for i, ref in enumerate(referencias, 1):
            f.write(f"Referência {i}:\n\n")
            f.write(ref.strip() + "\n\n")
            f.write("-" * 40 + "\n\n")  # linha separadora
           



# #### main ####

if __name__ == "__main__":
    # Etapa 1
    contagem_unigramas, referencias = etapa1_identificar_termos_mais_citados()
    salvar_referencias(referencias)

    # # Etapa 2
    infos = etapa2_extrair_info_artigos()

    # Etapa 3
    etapa3_salvar_dados(infos)

    # print("\nProcessamento concluído. Dados extraídos salvos em dados_extraidos.txt")
