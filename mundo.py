import random
import math

class Bloco:
    def __init__(self, largura, altura):
        self.x = random.randint(20, largura - 20)
        self.y = random.randint(20, altura - 20)

class Abrigo:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Ser:
    def __init__(self, x, y, largura, altura, cerebro=None):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.energia = 100.0
        self.blocos_coletados = 0
        self.idade = 0
        self.geracao = 1
        
        # --- O CÉREBRO (REDE NEURAL) ---
        # Entradas (Percepção):
        # 0: Distância X até o bloco mais próximo
        # 1: Distância Y até o bloco mais próximo
        # 2: Minha energia atual (Fome)
        # 3: Clima é perigoso? (0 ou 1)
        # 4: Distância X até o abrigo mais próximo
        # 5: Distância Y até o abrigo mais próximo
        
        # Saídas (Ações):
        # 0: Mover no eixo X
        # 1: Mover no eixo Y
        # 2: Decisão de Construir abrigo (se > 0.5)
        
        if cerebro:
            self.pesos = list(cerebro["pesos"])
            self.geracao = cerebro["geracao"] + 1
            self.mutar()
        else:
            # Inicializa 18 conexões neurais aleatórias (6 entradas x 3 saídas)
            self.pesos = [random.uniform(-1.0, 1.0) for _ in range(18)]

    def mutar(self):
        """A mutação permite o aprendizado ao longo das gerações"""
        for i in range(len(self.pesos)):
            if random.random() < 0.15:  # 15% de chance de alterar um comportamento
                self.pesos[i] += random.uniform(-0.3, 0.3)

    def pensar_e_agir(self, blocos, abrigos, clima):
        self.idade += 1
        self.energia -= 0.25  # Gasto basal de energia por ciclo

        # 1. PEGAR ENTRADAS (SENSORES DO AMBIENTE)
        dx_bloco, dy_bloco = 0.0, 0.0
        if blocos:
            b_perto = min(blocos, key=lambda b: math.hypot(b.x - self.x, b.y - self.y))
            dx_bloco = (b_perto.x - self.x) / self.largura
            dy_bloco = (b_perto.y - self.y) / self.altura

        dx_abrigo, dy_abrigo = 0.0, 0.0
        if abrigos:
            a_perto = min(abrigos, key=lambda a: math.hypot(a.x - self.x, a.y - self.y))
            dx_abrigo = (a_perto.x - self.x) / self.largura
            dy_abrigo = (a_perto.y - self.y) / self.altura

        fome = (100.0 - self.energia) / 100.0
        perigo_clima = 1.0 if clima in ["Seca", "Desastre Natural"] else 0.0

        # 2. PROCESSAR NA REDE NEURAL (MULTI-CAMADA DIRETA)
        # Saída X
        out_x = (dx_bloco * self.pesos[0] + dy_bloco * self.pesos[1] + fome * self.pesos[2] + 
                 perigo_clima * self.pesos[3] + dx_abrigo * self.pesos[4] + dy_abrigo * self.pesos[5])
        
        # Saída Y
        out_y = (dx_bloco * self.pesos[6] + dy_bloco * self.pesos[7] + fome * self.pesos[8] + 
                 perigo_clima * self.pesos[9] + dx_abrigo * self.pesos[10] + dy_abrigo * self.pesos[11])
        
        # Saída Construção
        out_construir = (dx_bloco * self.pesos[12] + dy_bloco * self.pesos[13] + fome * self.pesos[14] + 
                         perigo_clima * self.pesos[15] + dx_abrigo * self.pesos[16] + dy_abrigo * self.pesos[17])

        # 3. APLICAR AÇÕES NO MUNDO
        # Movimentação física limitada
        self.x += max(-4, min(4, out_x * 5))
        self.y += max(-4, min(4, out_y * 5))
        
        # Limites do mapa
        self.x = max(10, min(self.largura - 10, self.x))
        self.y = max(10, min(self.altura - 10, self.y))

        # Decisão Autônoma de Construção
        # Se o cérebro decidir que o perigo é alto e ele tiver os 2 blocos necessários
        if out_construir > 0.5 and self.blocos_coletados >= 2:
            self.blocos_coletados -= 2
            abrigos.append(Abrigo(self.x, self.y))

        # 4. IMPACTO DO CLIMA
        if clima == "Seca":
            self.energia -= 0.15  # Desidratação / falta de água
        elif clima == "Desastre Natural":
            # Se houver um desastre (ex: tornado/meteoro), ele checa se está dentro de um abrigo (raio de 30px)
            em_seguranca = any(math.hypot(a.x - self.x, a.y - self.y) < 30 for a in abrigos)
            if not em_seguranca:
                self.energia -= 2.5  # Dano massivo por estar desprotegido
