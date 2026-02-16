import pytesseract
import cv2
import numpy as np
from PIL import ImageGrab, Image
import pyperclip
import re
import json
from datetime import datetime

class InterpretadorApostas:
    def __init__(self):
        # Configurar tesseract - ajuste o caminho se necessário
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def capturar_tela(self):
        """Captura a tela atual"""
        screenshot = ImageGrab.grab()
        return screenshot
    
    def preprocess_image(self, image):
        """Pré-processa a imagem para melhorar OCR"""
        # Converter PIL para OpenCV
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Converter para escala de cinza
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar limiar para melhor contraste
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Redimensionar para melhorar OCR (opcional)
        resized = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        return resized
    
    def extrair_texto(self, image):
        """Extrai texto da imagem usando OCR"""
        processed_img = self.preprocess_image(image)
        texto = pytesseract.image_to_string(processed_img, lang='por')
        return texto
    
    def identificar_campos(self, texto):
        """Identifica e extrai campos específicos de apostas"""
        # Normalizar o texto
        linhas = texto.strip().split('\n')
        
        # Dicionário para armazenar os dados extraídos
        dados_aposta = {
            'valor': '',
            'tipo_aposta': '',
            'stake': '',
            'retorno': ''
        }
        
        # Palavras-chave para identificar campos
        palavras_valor = ['valor', 'total', 'aposta']
        palavras_tipo = ['simples', 'múltipla', 'dupla', 'acumulada', 'combo']
        palavras_stake = ['stake', 'investimento', 'entrada']
        palavras_retorno = ['retorno', 'ganho', 'prêmio', 'receber']
        
        # Expressões regulares para encontrar valores monetários
        padrao_valor = r'R\$?\s*\d+(?:[,.]\d{2,3})*(?:\.\d{2})?|\d+(?:[,.]\d{2,3})*(?:\.\d{2})?\s*R\$?'
        padrao_valor_float = r'\d+(?:[,.]\d{2,3})*(?:\.\d{2})?'
        
        for linha in linhas:
            linha_lower = linha.lower().strip()
            
            # Verificar por palavras-chave e valores
            if any(palavra in linha_lower for palavra in palavras_valor):
                match_valor = re.search(padrao_valor, linha)
                if match_valor:
                    dados_aposta['valor'] = match_valor.group(0)
            
            if any(palavra in linha_lower for palavra in palavras_tipo):
                # Encontrar o tipo de aposta
                for tipo in palavras_tipo:
                    if tipo in linha_lower:
                        dados_aposta['tipo_aposta'] = tipo.capitalize()
                        break
            
            if any(palavra in linha_lower for palavra in palavras_stake):
                match_stake = re.search(padrao_valor, linha)
                if match_stake:
                    dados_aposta['stake'] = match_stake.group(0)
            
            if any(palavra in linha_lower for palavra in palavras_retorno):
                match_retorno = re.search(padrao_valor, linha)
                if match_retorno:
                    dados_aposta['retorno'] = match_retorno.group(0)
        
        # Se não encontrou por palavras-chave, tentar encontrar padrões genéricos
        if not dados_aposta['valor']:
            match_valor = re.search(padrao_valor, texto)
            if match_valor:
                dados_aposta['valor'] = match_valor.group(0)
        
        if not dados_aposta['stake']:
            # Tentar encontrar stake com contexto próximo
            for i, linha in enumerate(linhas):
                if 'stake' in linha.lower() or 'investimento' in linha.lower():
                    match = re.search(padrao_valor, linha)
                    if match:
                        dados_aposta['stake'] = match.group(0)
                        break
        
        if not dados_aposta['retorno']:
            # Tentar encontrar retorno com contexto próximo
            for i, linha in enumerate(linhas):
                if 'retorno' in linha.lower() or 'ganho' in linha.lower() or 'receber' in linha.lower():
                    match = re.search(padrao_valor, linha)
                    if match:
                        dados_aposta['retorno'] = match.group(0)
                        break
        
        return dados_aposta
    
    def formatar_para_excel(self, dados):
        """Formata os dados para cópia direta ao Excel (tab-delimited)"""
        headers = ['Data/Hora', 'Valor', 'Tipo de Aposta', 'Stake', 'Retorno']
        values = [
            datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            dados['valor'],
            dados['tipo_aposta'],
            dados['stake'],
            dados['retorno']
        ]
        
        # Criar string tab-delimited
        header_str = '\t'.join(headers)
        value_str = '\t'.join(values)
        
        excel_format = f"{header_str}\n{value_str}"
        return excel_format
    
    def processar_imagem(self, caminho_imagem=None):
        """Processa uma imagem específica ou captura a tela"""
        if caminho_imagem:
            imagem = Image.open(caminho_imagem)
        else:
            print("Capturando tela em 3 segundos... Posicione seu print screen!")
            import time
            time.sleep(3)
            imagem = self.capturar_tela()
        
        # Extrair texto
        texto = self.extrair_texto(imagem)
        
        # Identificar campos
        dados = self.identificar_campos(texto)
        
        # Formatando para Excel
        dados_formatados = self.formatar_para_excel(dados)
        
        # Copiar para área de transferência
        pyperclip.copy(dados_formatados)
        
        return dados_formatados, dados

def main():
    interpretador = InterpretadorApostas()
    
    print("Interpretador de Apostas - OCR")
    print("1. Processar print screen atual")
    print("2. Processar imagem salva")
    
    escolha = input("Escolha uma opção (1 ou 2): ")
    
    try:
        if escolha == '1':
            dados_formatados, dados_brutos = interpretador.processar_imagem()
        elif escolha == '2':
            caminho = input("Digite o caminho da imagem: ")
            dados_formatados, dados_brutos = interpretador.processar_imagem(caminho)
        else:
            print("Opção inválida!")
            return
    
        print("\nDados extraídos:")
        print(f"Valor: {dados_brutos['valor']}")
        print(f"Tipo de Aposta: {dados_brutos['tipo_aposta']}")
        print(f"Stake: {dados_brutos['stake']}")
        print(f"Retorno: {dados_brutos['retorno']}")
        
        print(f"\n{dados_formatados}")
        print("\n✓ Dados copiados para a área de transferência! Cole diretamente no Excel.")
        
    except Exception as e:
        print(f"Erro durante o processamento: {str(e)}")

if __name__ == "__main__":
    main()