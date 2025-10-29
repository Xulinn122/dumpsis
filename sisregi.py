# sisregi.py
from playwright.async_api import async_playwright
import asyncio
import re
from datetime import datetime

CREDENTIALS = {
    "usuario": "2300869KAMYLA",
    "senha": "Xulinn_777"
}

async def open_cns(cpf):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Acessa login
        await page.goto("https://sisregiii.saude.gov.br/", timeout=60000)

        # Preenche login
        await page.fill("#usuario", CREDENTIALS["usuario"])
        await page.fill("#senha", CREDENTIALS["senha"])
        await page.keyboard.press("Enter")
        await page.wait_for_load_state("networkidle")

        # Espera menu aparecer
        try:
            await page.wait_for_selector("frame[name='principal']", timeout=8000)
        except:
            await browser.close()
            return {"erro": "Falha no login (não encontrou o frame principal)"}

        # Acessa frame principal
        frame_principal = page.frame(name="principal")

        # Acessa menu lateral e procura a opção cadweb50 (Consulta Geral)
        await page.wait_for_selector("frame[name='menu']", timeout=8000)
        frame_menu = page.frame(name="menu")
        await frame_menu.click("text=Consulta Geral")
        await asyncio.sleep(3)

        # Volta ao frame principal e preenche CPF
        frame_principal = page.frame(name="principal")
        await frame_principal.fill("input[name='nu_cns']", cpf)
        await frame_principal.keyboard.press("Enter")
        await asyncio.sleep(4)

        html = await frame_principal.content()

        # Extrai dados com regex
        def busca(padrao):
            m = re.search(padrao, html, re.I)
            return m.group(1).strip() if m else None

        cns = busca(r"CNS<\/td>\s*<td[^>]*>\s*([\d ]+)")
        nome = busca(r"Nome<\/td>\s*<td[^>]*>\s*([A-ZÇÃÉÓÊ ]+)")
        nasc = busca(r"Data de Nascimento<\/td>\s*<td[^>]*>\s*([\d\/]+)")
        sexo = busca(r"Sexo<\/td>\s*<td[^>]*>\s*([A-Z]+)")

        idade = None
        if nasc:
            try:
                nasc_dt = datetime.strptime(nasc, "%d/%m/%Y")
                idade = datetime.now().year - nasc_dt.year
            except:
                pass

        await browser.close()
        return {
            "cns": cns,
            "nome": nome,
            "nascimento": nasc,
            "idade": idade,
            "sexo": sexo
        }

# Teste local
if __name__ == "__main__":
    cpf = input("Digite o CPF/CNS: ").strip()
    resultado = asyncio.run(open_cns(cpf))
    print("\n=== RESULTADO ===")
    print(resultado)
