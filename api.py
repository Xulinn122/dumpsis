from flask import Flask, request, jsonify
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import re
import os
import subprocess

app = Flask(__name__)

# CREDENCIAIS SISREG III
CREDENTIALS = {
    "usuario": "2300869KAMYLA",
    "senha": "Xulinn_777"
}

# Instala o Chromium se não estiver presente
def install_chromium():
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception as e:
        print("Erro ao instalar Chromium:", e)

install_chromium()

# Função principal para login e consulta CNS
async def consulta_cns_playwright(cpf):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        try:
            await page.goto("https://sisregiii.saude.gov.br", timeout=60000)
            await page.wait_for_load_state("domcontentloaded")

            # Detecta frame do login
            login_frame = None
            for f in page.frames:
                if "#usuario" in await f.content():
                    login_frame = f
                    break
            if not login_frame:
                raise Exception("Não consegui localizar o frame de login.")

            # Preenche login
            await login_frame.fill("#usuario", CREDENTIALS["usuario"])
            await login_frame.fill("#senha", CREDENTIALS["senha"])

            # Tenta clicar no botão
            submit_btn = await login_frame.query_selector("input[type=submit], button[type=submit]")
            if submit_btn:
                await submit_btn.click()
            else:
                raise Exception("Botão de login não encontrado.")

            await page.wait_for_load_state("networkidle", timeout=20000)

            # Navega para página de consulta CNS
            # Ajuste a URL conforme o Sisreg real
            await page.goto("https://sisregiii.saude.gov.br/geral/buscaCnsCpf.do", timeout=60000)
            await page.wait_for_load_state("domcontentloaded")

            # Detecta o frame da busca CNS
            consulta_frame = None
            for f in page.frames:
                if "nu_cns" in await f.content() or "cpfCns" in await f.content():
                    consulta_frame = f
                    break
            if not consulta_frame:
                raise Exception("Não encontrei frame de consulta CNS.")

            # Preenche CPF/CNS
            input_cpf = await consulta_frame.query_selector("input[name='nu_cns'], input[name*='cpf']")
            if not input_cpf:
                raise Exception("Campo de CPF/CNS não encontrado.")
            await input_cpf.fill(cpf)

            # Clica no botão de pesquisar
            search_btn = await consulta_frame.query_selector("input[type=submit], button[type=submit]")
            if search_btn:
                await search_btn.click()
            else:
                raise Exception("Botão de pesquisa CNS não encontrado.")

            await page.wait_for_timeout(2000)

            html = await consulta_frame.content()

            # Extrai alguns dados básicos
            def extrair(campo):
                match = re.search(f"{campo}\\s*[:|-]\\s*(.*?)<", html, re.IGNORECASE)
                return match.group(1).strip() if match else None

            dados = {
                "CNS": extrair("CNS"),
                "Nome": extrair("Nome"),
                "Data de Nascimento": extrair("Data de Nascimento"),
                "Sexo": extrair("Sexo"),
                "HTML_preview": html[:2000]  # só para debug
            }

            await browser.close()
            return {"success": True, "dados": dados}

        except PlaywrightTimeoutError:
            await browser.close()
            return {"success": False, "erro": "Timeout ao carregar a página ou localizar elementos."}
        except Exception as e:
            await browser.close()
            return {"success": False, "erro": str(e)}

# Rota Flask
@app.route("/consulta", methods=["GET"])
def consulta():
    cpf = request.args.get("cpf")
    if not cpf:
        return jsonify({"erro": "Parâmetro 'cpf' obrigatório"}), 400
    try:
        resultado = asyncio.run(consulta_cns_playwright(cpf))
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
