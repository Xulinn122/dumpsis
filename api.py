# api.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import asyncio
from sisregi import open_cns
import asyncio
from playwright.__main__ import main as playwright_main

asyncio.run(asyncio.to_thread(playwright_main, ["install", "chromium"]))

app = FastAPI(title="API SISREG CNS", description="Consulta CNS automatizada via Playwright", version="1.0")

@app.get("/consulta")
async def consulta_cns(cpf: str):
    try:
        resultado = await open_cns(cpf)
        return JSONResponse(content=resultado)
    except Exception as e:
        return JSONResponse(content={"erro": str(e)}, status_code=500)
