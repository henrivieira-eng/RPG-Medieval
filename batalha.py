import random
from estrutura import Bandido, Duende, Ogro, Pocao

class Batalha:
    """
    Classe responsável por controlar as batalhas entre o jogador e um inimigo.

    Gerencia a geração de inimigos, os turnos de combate, o uso de poções,
    a fuga da batalha e a distribuição de recompensas ao final do confronto.

    Attributes:
        jogador (Personagem): Personagem controlado pelo jogador.
        inimigo (Inimigo): Inimigo gerado aleatoriamente para a batalha.
    """
    
    def __init__(self, jogador):
        self.jogador = jogador
        self.inimigo = self.gerar_inimigo_aleatorio()

    def gerar_inimigo_aleatorio(self):
        inimigos = [Bandido(), Duende(), Ogro()]
        return random.choice(inimigos)

    def iniciar(self):
        print("\n" * 2)
        print("=" * 40)
        print(f" UM {self.inimigo.nome.upper()} SELVAGEM APARECEU!")
        print("=" * 40)

        while self.jogador._vida > 0 and self.inimigo._vida > 0:
            print(f"\n--- Turno do Jogador ---")
            print(f"Seu HP: {self.jogador._vida}/{self.jogador._vida_max}")
            print(f"HP do {self.inimigo.nome}: {self.inimigo._vida}/{self.inimigo._vida_max}")
            print("\nEscolha sua ação:")
            print("1 | Atacar")
            print("2 | Usar Poção")
            print("3 | Fugir")

            escolha = input("> ")

            if escolha == "1":
                dano_causado = self.jogador.calcular_dano()
                self.inimigo.receber_dano(dano_causado)
                print(f"\nVocê atacou o {self.inimigo.nome} e causou {dano_causado} de dano!")
                
            elif escolha == "2":
                pocoes = [item for item in self.jogador.inventario._itens if isinstance(item, Pocao)]
                
                if not pocoes:
                    print("\nVocê não tem poções no inventário!")
                    continue
                
                print("\nQual poção deseja usar?")
                for i, pocao in enumerate(pocoes, start=1):
                    print(f"{i} - {pocao.nome} (Cura: {pocao.cura})")
                print("Pressione ENTER para voltar.")
                
                escolha_pocao = input("> ")
                if escolha_pocao == "":
                    continue
                
                try:
                    idx = int(escolha_pocao) - 1
                    pocao_escolhida = pocoes[idx]
                    
                    self.jogador.tomar_pocao(pocao_escolhida)
                    self.jogador.inventario - pocao_escolhida
                    print(f"\nVocê usou {pocao_escolhida.nome} e recuperou vida!")
                except (ValueError, IndexError):
                    print("\nEscolha inválida.")
                    continue
                    
            elif escolha == "3":
                if random.random() > 0.5:
                    print("\nVocê conseguiu escapar da batalha com sucesso!")
                    return
                else:
                    print("\nFalha ao tentar fugir! O inimigo bloqueou seu caminho.")
            else:
                print("\nAção inválida.")
                continue

            if self.inimigo._vida > 0:
                print(f"\n--- Turno do {self.inimigo.nome} ---")
                self.jogador.receber_dano(self.inimigo.dano)
                print(f"O {self.inimigo.nome} te atacou e causou {self.inimigo.dano} de dano!")

        self.verificar_resultado()

    def verificar_resultado(self):
        if self.jogador._vida <= 0:
            print("\n==============================")
            print("       VOCÊ FOI DERROTADO!     ")
            print("==============================")
            self.jogador._vida = int(self.jogador._vida_max * 0.2)
            perda = int(self.jogador._moedas * 0.1)
            self.jogador._moedas -= perda
            print(f"Você acordou na cidade. Perdeu {perda} moedas.")
            
        elif self.inimigo._vida <= 0:
            recompensa = random.randint(15, 40)
            self.jogador._moedas += recompensa
            print("\n==============================")
            print("       VITÓRIA!               ")
            print("==============================")
            print(f"Você derrotou o {self.inimigo.nome} e ganhou {recompensa} moedas!")
            
            missao = self.jogador._missao_ativa
            if missao:
                nome_formatado = f"{self.inimigo.nome.lower()}s" if not self.inimigo.nome.lower().endswith('s') else self.inimigo.nome.lower()
                if self.inimigo.nome == "Ogro":
                    nome_formatado = "ogros"
                elif self.inimigo.nome == "Duende":
                    nome_formatado = "duendes"
                elif self.inimigo.nome == "Bandido":
                    nome_formatado = "bandidos"

                if missao.inimigo == nome_formatado:
                    missao.progredir(self.jogador)
                    print(f"Progresso da Missão: {missao.progresso}/{missao.quantidade_inimigos}")
                    if missao.progresso == missao.quantidade_inimigos:
                        print("Missão concluída! Recompensa recebida.")