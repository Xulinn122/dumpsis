from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ API SISREGI está online! Use /consulta?cpf=XXXXXXXXXXX'

@app.route('/consulta')
def consulta():
    cpf = request.args.get('cpf')
    if not cpf:
        return jsonify({'erro': 'CPF/CNS não informado'}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://cadsus.saude.gov.br/pages/login/login.xhtml")

            # Preenche CPF/CNS
            page.locator("input[id*='cpfCns']").fill(cpf)
            page.locator("button[id*='botaoBuscar']").click()
            page.wait_for_timeout(3000)

            resultado = {}
            for campo in ["CNS", "Nome", "Data de Nascimento", "Sexo"]:
                try:
                    elemento = page.locator(f"text={campo}:").locator("xpath=following-sibling::*").inner_text()
                    resultado[campo] = elemento.strip()
                except:
                    resultado[campo] = "Não encontrado"

            browser.close()
            return jsonify(resultado)

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))  # Railway usa PORT
    app.run(host='0.0.0.0', port=port)
