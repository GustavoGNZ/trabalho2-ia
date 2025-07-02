import spacy
import subprocess
import sys

def install_spacy_model(model_name="pt_core_news_sm"):
    try:
        spacy.load(model_name)
        print(f"Modelo {model_name} já está instalado.")
    except OSError:
        print(f"Instalando modelo {model_name}...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])

if __name__ == "__main__":
    install_spacy_model()
