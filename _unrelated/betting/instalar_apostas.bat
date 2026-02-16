@echo off
echo Instalando dependencias para o interpretador de apostas...

pip install -r requirements_apostas.txt

echo.
echo Para usar o interpretador de apostas:
echo 1. Certifique-se de ter o Tesseract instalado no sistema
echo 2. Rode: python interpretador_apostas.py
echo.
echo Se nao tiver o Tesseract instalado:
echo Baixe em: https://github.com/UB-Mannheim/tesseract/wiki
echo Adicione ao PATH ou descomente e ajuste o caminho no codigo
pause