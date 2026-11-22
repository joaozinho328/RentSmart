
import csv

VALORES_BASE = {
    "apartamento": 700,
    "casa": 900,
    "estudio": 1200
}

ADICIONAL_2_QUARTOS = {
    "apartamento": 200,
    "casa": 250
}

VALOR_VAGA_RESIDENCIAL = 300
PACOTE_ESTUDIO = 250
VAGAS_INCLUIDAS_PACOTE = 2
VALOR_VAGA_EXTRA_ESTUDIO = 60

DESCONTO_SEM_CRIANCAS = 0.05
TAXA_CONTRATUAL = 2000
MAX_PARCELAS = 5
MESES_PROJECAO = 12


def formatar_moeda(valor):
    texto = f"{valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_decimal_csv(valor):
    return f"{valor:.2f}".replace(".", ",")


class Imovel:
    def __init__(self, tipo, quartos, vagas=0, criancas=False):
        if tipo not in VALORES_BASE:
            raise ValueError("Tipo de imóvel inválido.")

        self.tipo = tipo
        self.quartos = quartos
        self.vagas = vagas
        self.criancas = criancas
        self.valor_base = VALORES_BASE[tipo]

    def calcular_detalhamento(self):
        adicional_quartos = 0
        valor_vagas = 0
        desconto = 0

        if self.quartos == 2:
            adicional_quartos = ADICIONAL_2_QUARTOS.get(self.tipo, 0)

        if self.tipo == "estudio":
            if self.vagas > 0:
                extras = max(0, self.vagas - VAGAS_INCLUIDAS_PACOTE)
                valor_vagas = PACOTE_ESTUDIO + extras * VALOR_VAGA_EXTRA_ESTUDIO
        else:
            valor_vagas = self.vagas * VALOR_VAGA_RESIDENCIAL

        subtotal = self.valor_base + adicional_quartos + valor_vagas

        if self.tipo == "apartamento" and not self.criancas:
            desconto = subtotal * DESCONTO_SEM_CRIANCAS

        aluguel = round(subtotal - desconto, 2)

        return {
            "base": self.valor_base,
            "quartos": adicional_quartos,
            "vagas": valor_vagas,
            "desconto": desconto,
            "aluguel": aluguel
        }

    def calcular_aluguel(self):
        return self.calcular_detalhamento()["aluguel"]


class Contrato:
    def __init__(self, imovel, parcelas, taxa_contratual=TAXA_CONTRATUAL):
        if not 1 <= parcelas <= MAX_PARCELAS:
            raise ValueError("Quantidade de parcelas inválida.")

        self.imovel = imovel
        self.parcelas = parcelas
        self.taxa_contratual = taxa_contratual

    def calcular_parcela(self):
        return round(self.taxa_contratual / self.parcelas, 2)


class Orcamento:
    def __init__(self, contrato):
        self.contrato = contrato

    def exibir_resumo(self):
        imovel = self.contrato.imovel
        dados = imovel.calcular_detalhamento()

        print("\n========== RENTSMART ==========")
        print(f"Imóvel: {imovel.tipo}")
        print(f"Quartos: {imovel.quartos}")
        print(f"Vagas de garagem: {imovel.vagas}")
        print("--------------------------------")
        print(f"Valor base: R$ {formatar_moeda(dados['base'])}")
        print(f"Adicional por quartos: R$ {formatar_moeda(dados['quartos'])}")
        print(f"Adicional por vagas: R$ {formatar_moeda(dados['vagas'])}")
        print(f"Desconto: R$ {formatar_moeda(dados['desconto'])}")
        print("--------------------------------")
        print(f"ALUGUEL MENSAL: R$ {formatar_moeda(dados['aluguel'])}")
        print(f"Taxa contratual: R$ {formatar_moeda(self.contrato.taxa_contratual)}")
        print(f"Parcelamento: {self.contrato.parcelas} vezes")
        print(f"Valor da parcela: R$ {formatar_moeda(self.contrato.calcular_parcela())}")
        print("================================")

    def gerar_csv(self, nome_arquivo="projecao_rentsmart.csv"):
        aluguel = self.contrato.imovel.calcular_aluguel()
        parcela = self.contrato.calcular_parcela()

        with open(nome_arquivo, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(["Mes", "Aluguel", "Parcela Contratual", "Total"])

            for mes in range(1, MESES_PROJECAO + 1):
                valor_parcela = parcela if mes <= self.contrato.parcelas else 0
                total = aluguel + valor_parcela

                escritor.writerow([
                    mes,
                    formatar_decimal_csv(aluguel),
                    formatar_decimal_csv(valor_parcela),
                    formatar_decimal_csv(total)
                ])

        print(f"\nArquivo CSV gerado com sucesso: {nome_arquivo}")


def solicitar_numero(mensagem, minimo, maximo):
    while True:
        try:
            valor = int(input(mensagem))

            if minimo <= valor <= maximo:
                return valor

            print(f"Digite um número entre {minimo} e {maximo}.")

        except ValueError:
            print("Digite apenas números inteiros.")


def main():
    print("===== BEM-VINDO AO RENTSMART =====")
    print("\nTipos de imóveis:")
    print("1 - Apartamento")
    print("2 - Casa")
    print("3 - Estúdio")

    tipos = {
        1: "apartamento",
        2: "casa",
        3: "estudio"
    }

    tipo = tipos[solicitar_numero("Escolha o imóvel: ", 1, 3)]
    residencial = tipo in ("apartamento", "casa")

    quartos = 0

    if residencial:
        quartos = solicitar_numero("Quantidade de quartos (1 ou 2): ", 1, 2)

    if residencial:
        vagas = solicitar_numero("Deseja vaga de garagem? (1-Sim / 0-Nao): ", 0, 1)
    else:
        vagas = solicitar_numero("Quantidade de vagas de estacionamento (0 a 10): ", 0, 10)

    criancas = False

    if tipo == "apartamento":
        criancas = solicitar_numero("Possui crianças? (1-Sim / 0-Nao): ", 0, 1) == 1

    parcelas = solicitar_numero(
        f"Em quantas parcelas deseja pagar a taxa contratual (1 a {MAX_PARCELAS})? ",
        1,
        MAX_PARCELAS
    )

    imovel = Imovel(tipo, quartos, vagas, criancas)
    contrato = Contrato(imovel, parcelas)
    orcamento = Orcamento(contrato)

    orcamento.exibir_resumo()
    orcamento.gerar_csv()


if __name__ == "__main__":
    main()
