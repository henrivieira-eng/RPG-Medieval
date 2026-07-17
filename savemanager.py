import csv
import os
from estrutura import (LogMixin,
                       Lutador,
                       Espadachim,
                       Atirador,
                       Arqueiro,
                       Feiticeiro,
                       Pocao,
                       Equipamento
                       )

class SaveManager(LogMixin):
    """
    Classe responsável pelo gerenciamento de saves do jogo. Herda de LogMixin.

    Realiza a criação dos arquivos de armazenamento, salvamento e carregamento
    de personagens, inventários e registros de log.

    Attributes:
        personagem (Personagem): Referência ao personagem atualmente sendo
        manipulado pelo gerenciador de saves.
    """

    def __init__(self) -> None:
        self.personagem = None

    def criar_arquivos(self) -> None:
        self.criar_csv("personagens.csv", ["saveid", "nome", "classe", "moedas", "arma", "armadura", "escudo"])
        self.criar_csv("inventario.csv", ["saveid", "nome", "preço", "tipo", "cura", "bonusfor", "bonusres", "bonusagi", "bonusint"])
        self.criar_csv("logs.csv", ["personagem", "mensagem"])

    def criar_csv(self, nome: str, cabecalho: list) -> None:
        if not os.path.exists(nome):
            try:
                with open(nome, "w", newline="", encoding="utf-8") as arquivo:
                    writer = csv.writer(arquivo)
                    writer.writerow(cabecalho)
                self.log(f"Arquivo {nome} criado com sucesso!")
            except IOError as e:
                self.log(f"Erro ao criar arquivo {nome}: {e}")

    def salvar_personagem(self, saveid: int) -> None:
        if not self.personagem:
            return
        
        if not os.path.exists("personagens.csv"):
            self.criar_arquivos()

        p = self.personagem
        with open("personagens.csv", "a", newline="", encoding="utf-8") as arquivo:
            writer = csv.writer(arquivo)
            writer.writerow([
                saveid, 
                p.nome, 
                p.__class__.__name__, 
                getattr(p, "_moedas", 0), 
                p._arma.nome if getattr(p, "_arma", None) else "", 
                p._armadura.nome if getattr(p, "_armadura", None) else "", 
                p._escudo.nome if getattr(p, "_escudo", None) else ""
            ])
        self.salvar_log(f"Personagem '{p.nome}' salvo.")

    def salvar_inventario(self, saveid: int) -> None:
        if not self.personagem or not hasattr(self.personagem, "inventario"):
            return

        with open("inventario.csv", "a", newline="", encoding="utf-8") as arquivo:
            writer = csv.writer(arquivo)
            for item in self.personagem.inventario._itens:
                if getattr(item, "tipo", "") == "Poção":
                    writer.writerow([
                        saveid, item.nome, item.preco, item.tipo, getattr(item, "cura", ""), 
                        "", "", "", ""
                    ])
                else:
                    writer.writerow([
                        saveid, item.nome, item.preco, getattr(item, "tipo", "Equipamento"), "", 
                        getattr(item, "bonus_forca", ""), 
                        getattr(item, "bonus_resistencia", ""), 
                        getattr(item, "bonus_agilidade", ""), 
                        getattr(item, "bonus_inteligencia", "")
                    ])
        self.salvar_log("Inventário salvo.")

    def salvar_log(self, mensagem: str) -> None:
        nome_p = self.personagem.nome if self.personagem else "Sistema"
        with open("logs.csv", "a", newline="", encoding="utf-8") as arquivo:
            writer = csv.writer(arquivo)
            writer.writerow([nome_p, mensagem])

    def gerar_saveid(self) -> int:
        if not os.path.exists("personagens.csv"):
            return 1
        
        try:
            with open("personagens.csv", "r", encoding="utf-8") as arquivo:
                reader = csv.DictReader(arquivo)
                saveids = [int(linha["saveid"]) for linha in reader if linha.get("saveid")]
                return max(saveids) + 1 if saveids else 1
        except (IOError, ValueError):
            return 1

    def salvar_jogo(self) -> None:
        if not self.personagem:
            print("Nenhum personagem carregado para salvar.")
            return
        
        if not hasattr(self.personagem, "saveid"):
            self.personagem.saveid = self.gerar_saveid()

        saveid = self.personagem.saveid

        self.remover_save(saveid)

        self.salvar_personagem(saveid)
        self.salvar_inventario(saveid)

        self.salvar_log("Jogo salvo com sucesso.")

    def listar_saves(self) -> None:
        if not os.path.exists("personagens.csv"):
            print("\nNenhum save encontrado.\n")
            return

        with open("personagens.csv", 'r', encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)
            print("\n===== SAVES =====")
            for linha in leitor:
                print(f"SaveID: {linha['saveid']} | Nome: {linha['nome']} | Classe: {linha['classe']}")
            print("=================\n")

    def remover_personagem(self, saveid: str) -> None:
        self._remover_registro("personagens.csv", str(saveid), ["saveid", "nome", "classe", "moedas", "arma", "armadura", "escudo"])

    def remover_inventario(self, saveid: str) -> None:
        self._remover_registro("inventario.csv", str(saveid), ["saveid", "nome", "preço", "tipo", "cura", "bonusfor", "bonusres", "bonusagi", "bonusint"])

    def _remover_registro(self, nome_arquivo: str, saveid: str, cabecalho: list) -> None:
        if not os.path.exists(nome_arquivo):
            return

        linhas_filtradas = []
        with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                if linha.get("saveid") != saveid:
                    linhas_filtradas.append(linha)

        with open(nome_arquivo, "w", newline="", encoding="utf-8") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=cabecalho)
            writer.writeheader()
            writer.writerows(linhas_filtradas)
        self.salvar_log(f"Registros do SaveID {saveid} removidos de {nome_arquivo}.")

    def remover_save(self, saveid):
        self.remover_personagem(saveid)
        self.remover_inventario(saveid)
        self.salvar_log(f"Save {saveid} removido.")

    def carregar_personagem(self, saveid):
        if not os.path.exists("personagens.csv"):
            print("Nenhum save encontrado.")
            return None

        with open("personagens.csv", "r", encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)

            classes = {
                "Lutador": Lutador,
                "Espadachim": Espadachim,
                "Atirador": Atirador,
                "Arqueiro": Arqueiro,
                "Feiticeiro": Feiticeiro
            }

            for linha in leitor:

                if linha["saveid"] == str(saveid):

                    classe = classes[linha["classe"]]

                    personagem = classe(linha["nome"])

                    personagem._moedas = int(linha["moedas"])

                    personagem.saveid = int(linha["saveid"])

                    self.personagem = personagem

                    print("Save carregado com sucesso!")

                    return personagem, linha

        print("Save não encontrado.")
        return None
    
    def carregar_inventario(self, saveid):

        if not self.personagem:
            print("Carregue um personagem primeiro!")
            return False

        if not os.path.exists("inventario.csv"):
            print("Nenhum arquivo de inventário encontrado.")
            return False

        try:

            with open("inventario.csv", "r", encoding="utf-8") as arquivo:

                leitor = csv.DictReader(arquivo)

                itens_carregados = 0

                for linha in leitor:

                    if linha["saveid"] == str(saveid):

                        preco = int(linha["preço"]) if linha["preço"] else 0

                        if linha["tipo"] == "Poção":

                            item = Pocao(
                                linha["nome"],
                                preco,
                                int(linha["cura"])
                            )

                        else:

                            item = Equipamento(
                                linha["nome"],
                                preco,
                                linha["tipo"],
                                float(linha["bonusfor"]) if linha["bonusfor"] else 0,
                                float(linha["bonusres"]) if linha["bonusres"] else 0,
                                float(linha["bonusagi"]) if linha["bonusagi"] else 0,
                                float(linha["bonusint"]) if linha["bonusint"] else 0
                            )

                        self.personagem.inventario + item

                        itens_carregados += 1

                self.salvar_log(
                    f"Inventário carregado: {itens_carregados} itens restaurados."
                )

                return True

        except (IOError, ValueError) as e:
            print(f"Erro ao carregar inventário: {e}")
            return False
        
    def restaurar_equipamentos(self, dados_save):
        for item in self.personagem.inventario._itens:
            if item.nome == dados_save["arma"]:
                self.personagem.equipar(item)
            elif item.nome == dados_save["armadura"]:
                self.personagem.equipar(item)
            elif item.nome == dados_save["escudo"]:
                self.personagem.equipar(item)

        self.salvar_log("Equipamentos restaurados.")
    
    def carregar_jogo(self, saveid):
        resultado = self.carregar_personagem(saveid)
        if resultado:
            personagem, dados = resultado

            self.carregar_inventario(saveid)
            self.restaurar_equipamentos(dados)
            self.salvar_log(
                f"Jogo completo carregado para '{personagem.nome}'."
            )

            return personagem

        print("Falha ao carregar o jogo.")

        return None