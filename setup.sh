#!/bin/bash

# Cria e ativa o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Atualiza pip e instala libs do requirements.txt
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

