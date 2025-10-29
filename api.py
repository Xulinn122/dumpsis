import asyncio
from flask import Flask, request, jsonify
from playwright.async_api import async_playwright
from playwright.__main__ import main as playwright_main

# 🔧 Instala automaticamente o Chromium no Render
asyncio.run(asyncio.to_thread(playwright_main, ["install", "chromium"]))

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "✅ API SISREGI está online! Use /consulta?cpf=XXXXXXXXXXX"})

@app.route('/consulta', methods=['GET'])
async def consulta():
    cpf = request.args.get('cpf')
    if not cpf:
        return jsonify({"erro": "Parâmetro 'cpf' é obrigatório."}), 400

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto("https://sisregiii.saude.gov.br/")
            await page.fill("#usuario", "y4ziok")
            await page.fill("#senha", "by_y4ziok")
            await page.click("button[type=submit], input[type=submit], #botaoEntrar")

            # Aguarda o carregamento pós-login
            await page.wait_for_load_state("networkidle")

            # Ir para o formulário de busca (ajuste se necessário)
            await page.goto("https://sisregiii.saude.gov.br/geral/buscaCnsCpf.do")
            await page.fill("#cpfCns", cpf)
            await page.click("input[type=submit]")

            await page.wait_for_load_state("networkidle")

            html = await page.content()

            # Extrai os dados principais (básico)
            def extrair(campo):
                import re
                match = re.search(f"{campo}\\s*[:|-]\\s*(.*?)<", html, re.IGNORECASE)
                return match.group(1).strip() if match else None

            dados = {
                "CNS": extrair("CNS"),
                "Nome": extrair("Nome"),
                "Data de Nascimento": extrair("Data de Nascimento"),
                "Sexo": extrair("Sexo")
            }

            await browser.close()
            return jsonify(dados)

    except Exception as e:
        return jsonify({"erro": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
