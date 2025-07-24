from datetime import datetime, timedelta

import logfire
from pydantic_ai import Agent
from rich.console import Console
from rich.markdown import Markdown

console = Console()
agent = Agent(
    "google-gla:gemini-2.0-flash",
    system_prompt="Responda as perguntas de maneira formal e com vocabulário de advogados. Quando possível utilize o formato markdown nas respostas.",
)

DIAS_POR_ANO = 365
DIAS_POR_MES = 30

logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_pydantic_ai()


@agent.tool_plain
def converte_para_dias(anos: int, meses: int, dias: int) -> str:
    """
    Converte anos, meses e dias em dias.
    Args:
        anos (int): Número de anos.
        meses (int): Número de meses.
        dias (int): Número de dias.
    Returns:
        str: Total de dias.
    """
    if anos < 0 or meses < 0 or dias < 0:
        return "Por favor, informe um valor válido."
    return str(anos * DIAS_POR_ANO + meses * DIAS_POR_MES + dias)


@agent.tool_plain
def converte_dias_em_anos_meses_dias_por_extenso(dias: int) -> str:
    """
    Converte dias em anos, meses e dias por extenso.
    Args:
        dias (int): Número de dias.
    Returns:
        str: Anos, meses e dias por extenso.
    """
    if dias < 0:
        return "Por favor, informe um valor válido."
    anos = dias // DIAS_POR_ANO
    meses = (dias % DIAS_POR_ANO) // DIAS_POR_MES
    dias_restantes = (dias % DIAS_POR_ANO) % DIAS_POR_MES
    resultado = ""
    if anos > 0:
        resultado += f"{anos} ano{'s' if anos > 1 else ''}"
    if meses > 0:
        if resultado:
            resultado += ", "
        resultado += f"{meses} mes{'es' if meses > 1 else ''}"
    if dias_restantes > 0:
        if resultado:
            resultado += " e "
        resultado += f"{dias_restantes} dia{'s' if dias_restantes > 1 else ''}"
    return resultado


@agent.tool_plain
def diferenca_entre_datas(data1: str, data2: str) -> str:
    """
    Calcula a diferença entre duas datas.

    Args:
        data1 (str): Data inicial no formato 'DD-MM-YYYY'.
        data2 (str): Data final no formato 'DD-MM-YYYY'.
    Returns:
        str: Diferença em dias.
    """
    try:
        d1 = datetime.strptime(data1, "%d-%m-%Y")
        d2 = datetime.strptime(data2, "%d-%m-%Y")
        delta = abs((d2 - d1).days)
        return str(delta)
    except ValueError:
        return "Por favor, informe datas válidas no formato 'YYYY-MM-DD'."


@agent.tool_plain
def soma_ou_subtrai_dias_em_data(data: str, operacao: str, dias: int) -> str:
    """
    Soma ou subtrai dias de uma data.

    Args:
        data (str): Data no formato 'DD-MM-YYYY'.
        operacao (str): Operação a ser realizada ('soma' ou 'subtrai').
        dias (int): Número de dias a serem somados ou subtraídos.
    Returns:
        str: Nova data no formato 'DD-MM-YYYY'.
    """
    try:
        d = datetime.strptime(data, "%d-%m-%Y")
        if operacao == "soma":
            nova_data = d + timedelta(days=dias)
        elif operacao == "subtrai":
            nova_data = d - timedelta(days=dias)
        else:
            return "Operação inválida. Use 'soma' ou 'subtrai'."
        return nova_data.strftime("%d-%m-%Y")
    except ValueError:
        return "Por favor, informe uma data válida no formato 'DD-MM-YYYY'."


@agent.tool_plain
def calcula_fracao_e_porcentagem_baseado_em_dias(dias: int) -> str:
    """Calcula o número de dias correspondentes a 1/6, 1/5, 1/4, 1/3, 3/8, 2/5 ,
       5/12, 11/24, 1/2, 3/5, 2/3 do valor e também as porcentagens
       correspondentes a 16%, 20%, 25%, 30%, 40%, 50%, 60% e 70% do valor.

    Args:
        dias (int): Número de dias.
    Returns:
        str: Resultado com os valores calculados.
    """
    if dias < 0:
        return "Por favor, informe um valor válido."
    fracao = {
        "1/6": dias / 6,
        "1/5": dias / 5,
        "1/4": dias / 4,
        "1/3": dias / 3,
        "3/8": dias * 3 / 8,
        "2/5": dias * 2 / 5,
        "5/12": dias * 5 / 12,
        "11/24": dias * 11 / 24,
        "1/2": dias / 2,
        "3/5": dias * 3 / 5,
        "2/3": dias * 2 / 3,
    }
    porcentagem = {
        "16%": dias * 0.16,
        "20%": dias * 0.20,
        "25%": dias * 0.25,
        "30%": dias * 0.30,
        "40%": dias * 0.40,
        "50%": dias * 0.50,
        "60%": dias * 0.60,
        "70%": dias * 0.70,
    }
    resultado = ""
    for chave, valor in fracao.items():
        resultado += f"{chave}: {valor:.2f} | "
    resultado += "\n"
    for chave, valor in porcentagem.items():
        resultado += f"{chave}: {valor:.2f} | "
    return resultado


perguntas = [
    "Quantos dias tem em 1 ano e 4 meses?",
    "380 dias são quantos anos, meses e dias?",
    "Qual a diferença em dias entre 01-01-2020 e 01-01-2021?",
    "Qual a diferença em dias entre 1 de abril de 2025 e 23 de agosto de 2025?",
    "Se somar 45 dias a 1º de janeiro de 2025, qual será a nova data?",
    "Se subtrair 30 dias de 5 de abril de 2025, qual será a nova data?",
    "Quais são as frações e porcentagens para uma pena de 300 dias? Formate o resultado como uma tabela.",
]
for pergunta in perguntas:
    console.print(Markdown(f"**Pergunta:** {pergunta}"))
    result = agent.run_sync(pergunta)
    console.print(Markdown(result.output))
