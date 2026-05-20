import pygame
import random
import math

# Inicialização do Pygame
pygame.init()

# Configurações da Janela
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Mundo Evolutivo - Vida Artificial com IA")
relogio = pygame.time.Clock()

# Cores do Ambiente
C_GRAMA = (34, 139, 34)
C_CHUVA = (47, 79, 79)
C_SECA = (139, 115, 85)
C_DESASTRE = (128, 0, 0)
C_BLOCO = (139, 69, 19)
C_ABRIGO = (70, 130, 180)

class Bloco:
    def __init__(self):
        self.x = random.randint(20, LARGURA - 20)
        self.y = random.randint(20, ALTURA - 20)
        self.tamanho = 8

    def desenhar(self):
        pygame.draw.rect(tela, C_BLOCO, (self.x, self.y, self.tamanho, self.tamanho))

class Abrigo:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tamanho = 16

    def desenhar(self):
        pygame.draw.rect(tela, C_ABRIGO, (self.x, self.y, self.tamanho, self.tamanho))

class Ser:
    def __init__(self, x, y, cerebro=None):
        self.x = x
        self.y = y
        self.raio = 6
        self.energia = 100.0
        self.blocos_coletados = 0
        self.idade = 0

        # Cérebro (Rede Neural Simples): 12 pesos que conectam estímulos a reações
        if cerebro:
            self.pesos = list(cerebro)
            self.mutar()
        else:
            self.pesos = [random.uniform(-1, 1) for _ in range(12)]

    def mutar(self):
        # 15% de chance de mudar levemente um comportamento herdado
        for i in range(len(self.pesos)):
            if random.random() < 0.15:
                self.pesos[i] += random.uniform(-0.3, 0.3)

    def pensar_e_agir(self, blocos, abrigos, clima):
        self.idade += 1
        self.energia -= 0.2  # Gasto natural de viver

        # Procura o bloco mais próximo
        dist_bloco = 800
        if blocos:
            b_perto = min(blocos, key=lambda b: math.hypot(b.x - self.x, b.y - self.y))
            dist_bloco = math.hypot(b_perto.x - self.x, b_perto.y - self.y)

        # Entradas sensoriais do ser
        fome = 1.0 if self.energia < 40 else 0.0
        perigo = 1.0 if clima in ["Seca", "Desastre"] else 0.0

        # Processamento interno da "consciência"
        acao_x = (dist_bloco * self.pesos[0]) + (fome * self.pesos[1]) + (perigo * self.pesos[2])
        acao_y = (dist_bloco * self.pesos[3]) + (fome * self.pesos[4]) + (perigo * self.pesos[5])
        decisao_construir = (self.blocos_coletados * self.pesos[6]) + (perigo * self.pesos[7])

        # Movimentação baseada no pensamento
        self.x += max(-2, min(2, acao_x))
        self.y += max(-2, min(2, acao_y))

        # Fronteiras do mapa
        self.x = max(10, min(LARGURA - 10, self.x))
        self.y = max(10, min(ALTURA - 10, self.y))

        # Lógica de Construção
        if decisao_construir > 0.6 and self.blocos_coletados >= 2:
            self.blocos_coletados -= 2
            abrigos.append(Abrigo(self.x, self.y))

        # Danos causados pelo clima
        if clima == "Seca":
            self.energia -= 0.1
        elif clima == "Desastre":
            protegido = any(math.hypot(a.x - self.x, a.y - self.y) < 30 for a in abrigos)
            if not protegido:
                self.energia -= 1.8  # Desastres machucam muito quem está desabrigado

    def desenhar(self):
        # Cor dinâmica: Verde (saudável) a Vermelho (faminto/fraco)
        g = max(0, min(255, int(self.energia * 2.55)))
        r = max(0, min(255, int((100 - self.energia) * 2.55)))
        pygame.draw.circle(tela, (r, g, 0), (int(self.x), int(self.y)), self.raio)

# Configurações Iniciais da Simulação
seres = [Ser(random.randint(100, 700), random.randint(100, 500)) for _ in range(25)]
blocos = [Bloco() for _ in range(50)]
abrigos = []

climas = ["Normal", "Chuva", "Seca", "Desastre"]
clima_atual = "Normal"
tempo_clima = 200
ciclo_total = 0

# Fonte para o painel de texto
fonte = pygame.font.SysFont("Arial", 18)

# Loop Executável
rodando = True
while rodando:
    ciclo_total += 1
    tempo_clima -= 1

    # Tratamento de eventos do teclado/janela
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # Gerenciador de Clima
    if tempo_clima <= 0:
        clima_atual = random.choice(climas)
        tempo_clima = 60 if clima_atual == "Desastre" else 250

    # Fundo muda conforme as condições do tempo
    if clima_atual == "Normal": tela.fill(C_GRAMA)
    elif clima_atual == "Chuva": tela.fill(C_CHUVA)
    elif clima_atual == "Seca": tela.fill(C_SECA)
    elif clima_atual == "Desastre": tela.fill(C_DESASTRE)

    # Crescimento natural de recursos (blocos)
    if random.random() < 0.15 and clima_atual != "Seca":
        blocos.append(Bloco())

    # Desenhar Abrigos e Blocos existentes
    for abrigo in abrigos: abrigo.desenhar()
    for bloco in blocos[:]:
        bloco.desenhar()

    # Atualizar Ciclo de Vida dos Seres
    for ser in seres[:]:
        ser.pensar_e_agir(blocos, abrigos, clima_atual)
        
        # Comer blocos próximos
        for bloco in blocos[:]:
            if math.hypot(bloco.x - ser.x, bloco.y - ser.y) < 15:
                if bloco in blocos:
                    blocos.remove(bloco)
                    ser.blocos_coletados += 1
                    ser.energia = min(100.0, ser.energia + 35)

        # Sistema de Reprodução Darwiniana
        if ser.energia > 85 and ser.blocos_coletados >= 3 and random.random() < 0.02:
            ser.energia -= 40
            ser.blocos_coletados -= 3
            seres.append(Ser(ser.x + random.randint(-15, 15), ser.y + random.randint(-15, 15), ser.pesos))

        # Morrer se a energia acabar
        if ser.energia <= 0:
            seres.remove(ser)
        else:
            ser.desenhar()

    # Repovoar se houver extinção total
    if len(seres) == 0:
        seres = [Ser(random.randint(100, 700), random.randint(100, 500)) for _ in range(10)]
        abrigos.clear()

    # Painel de Informações Superior
    texto_clima = fonte.render(f"Tempo: {clima_atual.upper()}  |  Vivos: {len(seres)}  |  Ciclos: {ciclo_total}", True, (255, 255, 255))
    tela.blit(texto_clima, (15, 15))

    pygame.display.flip()
    relogio.tick(30)  # Mantém a simulação rodando de forma fluida a 30 FPS

pygame.quit()
