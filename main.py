import csv
import aiohttp
import asyncio
from datetime import datetime

def mudar_status(municipio, novoStatus):
    linhas = []

    with open('pec_urls.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for linha in reader:
            if linha[0] == municipio:
                linha[2] = novoStatus
            linhas.append(linha)

    with open('pec_urls.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerows(linhas)


async def fazer_requisicao(session, url, municipio, statusMunicipio):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status != 200:
                raise Exception
            if statusMunicipio == "false":
                print(f"[{datetime.now().strftime('%H:%M:%S')}]: O PEC de {municipio} voltou e se encontra Online.")
                mudar_status(municipio, 'true')
    except asyncio.TimeoutError:
        if statusMunicipio == "true":
            print(f"[{datetime.now().strftime('%H:%M:%S')}]: Ao tentar acessar o PEC de {municipio} durante 10s não foi obtido resposta.")
            mudar_status(municipio, 'false')
    except Exception:
        if statusMunicipio == "true":
            print(f"[{datetime.now().strftime('%H:%M:%S')}]: O PEC de {municipio} se encontra Offline.")
            mudar_status(municipio, 'false')


async def main():
    with open('pec_urls.csv') as csvfile:
        file = csv.reader(csvfile, delimiter=';')
        async with aiohttp.ClientSession() as session:
            tarefas = [
                fazer_requisicao(session, linha[1], linha[0], linha[2])
                for linha in file
            ]
            await asyncio.gather(*tarefas)


async def loop_monitoramento(intervalo=11):
    while True:
        await main()
        await asyncio.sleep(intervalo)


if __name__ == "__main__":
    asyncio.run(loop_monitoramento())