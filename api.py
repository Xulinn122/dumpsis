import os
import subprocess
import asyncio
from flask import Flask, request, jsonify
from playwright.async_api import async_playwright

# 🔧 Instalar Chromium automaticamente (modo seguro)
print("🔧 Instalando Chromium...")
subprocess.run(["playwright", "install", "chromium"], check=True)
print("✅ Chromium instalado com sucesso!")

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

            await page.wait_for_load_state("networkidle")

            await page.goto("https://sisregiii.saude.gov.br/geral/buscaCnsCpf.do")
            await page.fill("#cpfCns", cpf)
            await page.click("input[type=submit]")
            await page.wait_for_load_state("networkidle")

            html = await page.content()

            # Extrai dados simples do HTML
            import re
            def extrair(campo):
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
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
