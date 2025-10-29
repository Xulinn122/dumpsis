# api.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import asyncio
from sisregi import open_cns
import asyncio
import subprocess

# Instala o Chromium automaticamente se ainda não estiver instalado
try:
    subprocess.run(["playwright", "install", "chromium"], check=True)
except Exception as e:
    print("Aviso: Falha ao instalar o Chromium automaticamente:", e)

app = FastAPI(title="API SISREG CNS", description="Consulta CNS automatizada via Playwright", version="1.0")

@app.get("/consulta")
async def consulta_cns(cpf: str):
    try:
        resultado = await open_cns(cpf)
        return JSONResponse(content=resultado)
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
