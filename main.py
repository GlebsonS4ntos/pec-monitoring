import csv
import aiohttp
import asyncio
from datetime import datetime
from send import enviar_mensagem
import os

def mudar_status(servico, novoStatus):
    linhas = []

    with open('service_urls.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for linha in reader:
            if linha[0] == servico:
                linha[2] = novoStatus
            linhas.append(linha)

    with open('service_urls.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerows(linhas)


async def fazer_requisicao(session, url, servico, statusMunicipio, mensagens):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=int(os.getenv("TIMEOUT")))) as response:
            if response.status != 200:
                raise Exception
            if statusMunicipio == "false":
                mensagens.append(f"[{datetime.now().strftime('%H:%M:%S')}]: {servico} voltou a ficar Online. ✅")
                mudar_status(servico, 'true')
    except asyncio.TimeoutError:
        if statusMunicipio == "true":
            mensagens.append(f"[{datetime.now().strftime('%H:%M:%S')}]: Foi tentada conexão com {servico} por 10 segundos, mas não houve resposta. ❌")
            mudar_status(servico, 'false')
    except Exception:
        if statusMunicipio == "true":
            mensagens.append(f"[{datetime.now().strftime('%H:%M:%S')}]:{servico} se encontra Offline. ❌")
            mudar_status(servico, 'false')


async def main():
    mensagens = []

    with open('service_urls.csv') as csvfile:
        file = csv.reader(csvfile, delimiter=';')
        async with aiohttp.ClientSession() as session:
            tarefas = [
                fazer_requisicao(session, linha[1], linha[0], linha[2], mensagens)
                for linha in file
            ]
            await asyncio.gather(*tarefas)

        if mensagens:
            await enviar_mensagem("\n".join(mensagens))

async def loop_monitoramento(intervalo=int(os.getenv("TIME_REQUESTS"))):
    while True:
        await main()
        await asyncio.sleep(intervalo)