import streamlit as st
import random
import math
import time

# ==========================================
# CONFIGURAÇÃO DO AMBIENTE
# ==========================================
st.set_page_config(page_title="Evolução Artificial Real", layout="centered")
st.title("🧬 Algoritmo Genético: Evolução Visual Real")
st.markdown("Nesta simulação, os seres **não possuem programação de comportamento**. Eles aprendem a cada geração através de seleção natural pura.")

LARGURA, ALTURA = 700, 480
DURACAO_GERACAO = 400  # Tempo de cada rodada para aprendizado

# ==========================================
# ESTRUTURA NEURAL E GENÉTICA
# ==========================================
class Bloco:
    def __init__(self):
        self.x = random.randint(40, LARGURA - 40)
        self.y = random.randint(40, ALTURA - 40)

class Abrigo:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Ser:
    def __init__(self, x, y, pesos=None):
        self.x = x
        self.y = y
        self.energia = 100.0
        self.blocos_coletados = 0
        self.abrigos_construidos = 0
        self.tempo_protegido = 0
        self.morto = False
        
        # Sentido do olhar para renderização
        self.vx, self.vy = 1.0, 0.0
        
        # CÉREBRO: Rede Neural Simples (6 Entradas -> 3 Saídas = 18 Conexões/Pesos)
        # Entradas: [Dist_Bloco_X, Dist_Bloco_Y, Dist_Abrigo_X, Dist_Abrigo_Y, Energia/Fome, Perigo_Clima]
        # Saídas:   [Mover_X, Mover_Y, Decisão_Construir]
        if pesos is not None:
            self.pesos = pesos
        else:
            self.pesos = [random.uniform(-1.0, 1.0) for _ in range(18)]

    def calcular_fitness(self):
        """Avalia matematicamente o quão bom esse ser foi em entender o ambiente"""
        # Se ele coletou blocos, construiu e se protegeu no desastre, o fitness explode
        return (self.blocos_coletados * 10) + (self.abrigos_construidos * 25) + (self.tempo_protegido * 0.5) + 0.1

    def pensar_e_agir(self, blocos, abrigos, clima):
        if self.morto:
            return

        self.energia -= 0.25

        # 1. ENTRADAS DOS SENSORES (Percepção do ambiente ao redor)
        db_x, db_y = 0.0, 0.0
        if blocos:
            b_perto = min(blocos, key=lambda b: math.hypot(b.x - self.x, b.y - self.y))
            db_x = (b_perto.x - self.x) / LARGURA
            db_y = (b_perto.y - self.y) / ALTURA

        da_x, da_y = 0.0, 0.0
        if abrigos:
            a_perto = min(abrigos, key=lambda a: math.hypot(a.x - self.x, a.y - self.y))
            da_x = (a_perto.x - self.x) / LARGURA
            da_y = (a_perto.y - self.y) / ALTURA

        fome = (100.0 - self.energia) / 100.0
        perigo = 1.0 if clima == "DESASTRE" else 0.0

        # 2. PROCESSAMENTO NEURAL (A sinapse elétrica do cérebro artificial)
        out_x = (db_x * self.pesos[0] + db_y * self.pesos[1] + da_x * self.pesos[2] + da_y * self.pesos[3] + fome * self.pesos[4] + perigo * self.pesos[5])
        out_y = (db_x * self.pesos[6] + db_y * self.pesos[7] + da_x * self.pesos[8] + da_y * self.pesos[9] + fome * self.pesos[10] + perigo * self.pesos[11])
        out_con = (db_x * self.pesos[12] + db_y * self.pesos[13] + da_x * self.pesos[14] + da_y * self.pesos[15] + fome * self.pesos[16] + perigo * self.pesos[17])

        # 3. AÇÃO FÍSICA
        self.vx = max(-1, min(1, out_x)) * 6
        self.vy = max(-1, min(1, out_y)) * 6
        
        self.x = max(15, min(LARGURA - 15, self.x + self.vx))
        self.y = max(15, min(ALTURA - 15, self.y + self.vy))

        # Decisão de construir abrigo
        if out_con > 0.4 and self.blocos_coletados >= 2:
            self.blocos_coletados -= 2
            self.abrigos_construidos += 1
            abrigos.append(Abrigo(self.x, self.y))

        # 4. CHECAGEM DE CLIMA E SOBREVIVÊNCIA
        if clima == "DESASTRE":
            protegido = any(math.hypot(a.x - self.x, a.y - self.y) < 35 for a in abrigos)
            if protegido:
                self.tempo_protegido += 1
            else:
                self.energia -= 2.5  # Dano massivo por ignorar o ambiente

        if self.energia <= 0:
            self.morto = True

# ==========================================
# MOTOR DE SELEÇÃO NATURAL E REPRODUÇÃO
# ==========================================
def evoluir_populacao(ancestrais):
    """Pega os melhores da geração anterior e cria filhos inteligentes"""
    # Ordena os seres pelo desempenho real (fitness)
    ancestrais.sort(key=lambda s: s.calcular_fitness(), reverse=True)
    
    # Salva o campeão absoluto da rodada anterior para a telemetria
    melhor_da_rodada = ancestrais[0]
    
    # Seleciona a metade superior (os sobreviventes mais aptos)
    elite = ancestrais[:len(ancestrais)//2]
    
    novos_pesos_populacao = []
    
    while len(novos_pesos_populacao) < 15: # Mantém a população estável
        papai = random.choice(elite)
        mamae = random.choice(elite)
        
        # Crossover (Mistura de DNA - metade dos pensamentos de cada um)
        filho_pesos = []
        for i in range(18):
            filho_pesos.append(papai.pesos[i] if random.random() < 0.5 else mamae.pesos[i])
            
        # Mutação Crítica (Permite descobrir novas estratégias)
        for i in range(18):
            if random.random() < 0.1:  # 10% de taxa de mutação
                filho_pesos[i] += random.uniform(-0.4, 0.4)
                
        novos_pesos_populacao.append(filho_pesos)
        
    # Recria a população física com os cérebros evoluídos
    nova_geracao = []
    for pesos in novos_pesos_populacao:
        nova_geracao.append(Ser(random.randint(100, LARGURA-100), random.randint(100, ALTURA-100), pesos))
        
    return nova_geracao, melhor_da_rodada.calcular_fitness()

# ==========================================
# CONTROLE DE ESTADO DO STREAMLIT
# ==========================================
if "geracao" not in st.session_state:
    st.session_state.geracao = 1
    st.session_state.cronometro = 0
    st.session_state.seres = [Ser(random.randint(100, LARGURA-100), random.randint(100, ALTURA-100)) for _ in range(15)]
    st.session_state.blocos = [Bloco() for _ in range(30)]
    st.session_state.abrigos = []
    st.session_state.clima = "NORMAL"
    st.session_state.historico_fitness = 0.0

# Painel Superior
c1, c2, c3, c4 = st.columns(4)
if c1.button("🔄 Reiniciar Evolução"):
    st.session_state.geracao = 1
    st.session_state.cronometro = 0
    st.session_state.seres = [Ser(random.randint(100, LARGURA-100), random.randint(100, ALTURA-100)) for _ in range(15)]
    st.session_state.blocos = [Bloco() for _ in range(30)]
    st.session_state.abrigos = []
    st.session_state.clima = "NORMAL"
    st.session_state.historico_fitness = 0.0

fps = c2.slider("⚡ Velocidade", 5, 60, 25)

# ==========================================
# ATUALIZAÇÃO DO MUNDO (TICK DO RELÓGIO)
# ==========================================
st.session_state.cronometro += 1

# Ciclo climático fixo para testar adaptabilidade
if st.session_state.cronometro > 200:
    st.session_state.clima = "DESASTRE"
else:
    st.session_state.clima = "NORMAL"

# Reposição natural de blocos na fase normal
if st.session_state.clima == "NORMAL" and random.random() < 0.15 and len(st.session_state.blocos) < 40:
    st.session_state.blocos.append(Bloco())

# Atualiza agentes vivos
for ser in st.session_state.seres:
    ser.pensar_e_agir(st.session_state.blocos, st.session_state.abrigos, st.session_state.clima)
    
    # Captura física do bloco
    for bloco in st.session_state.blocos[:]:
        if not ser.morto and math.hypot(bloco.x - ser.x, bloco.y - ser.y) < 20:
            if bloco in st.session_state.blocos:
                st.session_state.blocos.remove(bloco)
                ser.blocos_coletados += 1
                ser.energia = min(100.0, ser.energia + 35)

# --- FIM DA GERAÇÃO: HORA DA SELEÇÃO NATURAL ---
if st.session_state.cronometro >= DURACAO_GERACAO:
    st.session_state.seres, melhor_score = evoluir_populacao(st.session_state.session_state.seres if "seres" in st.session_state else st.session_state.seres)
    st.session_state.historico_fitness = melhor_score
    st.session_state.blocos = [Bloco() for _ in range(30)]
    st.session_state.abrigos.clear()
    st.session_state.cronometro = 0
    st.session_state.geracao += 1
    st.rerun()

# ==========================================
# RENDERIZAÇÃO GRÁFICA INTERATIVA
# ==========================================
cor_fundo = "#34495E" if st.session_state.clima == "NORMAL" else "#7B241C"

# Transforma dados estruturados em comandos HTML5 Canvas
desenhar_blocos = "".join([f"ctx.fillStyle = '#D35400'; ctx.fillRect({b.x-4}, {b.y-4}, 9, 9);" for b in st.session_state.blocos])
desenhar_abrigos = "".join([f"ctx.fillStyle = '#2980B9'; ctx.fillRect({a.x-12}, {a.y-12}, 24, 24);" for a in st.session_state.abrigos])

desenhar_seres = ""
for ser in st.session_state.seres:
    if ser.morto:
        # Desenha uma pequena marca cinza se morreu de fome antes do fim do tempo
        desenhar_seres += f"ctx.fillStyle = 'rgba(255,255,255,0.15)'; ctx.fillRect({ser.x-3}, {ser.y-3}, 6, 6);"
        continue
        
    g = max(0, min(255, int(ser.energia * 2.55)))
    r = max(0, min(255, int((100 - ser.energia) * 2.55)))
    
    # Vetor de movimento real baseado nas saídas neurais
    mag = math.hypot(ser.vx, ser.vy)
    dx = (ser.vx / mag * 8) if mag > 0 else 0
    dy = (ser.vy / mag * 8) if mag > 0 else 0
    
    desenhar_seres += f"""
    ctx.beginPath();
    ctx.arc({ser.x}, {ser.y}, 9, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgb({r}, {g}, 40)';
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    
    // Direção da linha de visão do cérebro
    ctx.beginPath();
    ctx.moveTo({ser.x}, {ser.y});
    ctx.lineTo({ser.x + dx}, {ser.y + dy});
    ctx.strokeStyle = '#ffff00';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Indicador de inventário de blocos
    if({ser.blocos_coletados} > 0) {{
        ctx.fillStyle = '#ffff00';
        ctx.font = '9px Arial';
        ctx.fillText('📦' + {ser.blocos_coletados}, {ser.x - 10}, {ser.y - 13});
    }}
    """

html_canvas = f"""
<div style="text-align: center;">
    <canvas id="mundoCanvas" width="{LARGURA}" height="{ALTURA}" style="border: 3px solid #2C3E50; background-color: {cor_fundo}; border-radius: 8px;"></canvas>
</div>
<script>
    var canvas = document.getElementById('mundoCanvas');
    if (canvas) {{
        var ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, {LARGURA}, {ALTURA});
        {desenhar_abrigos}
        {desenhar_blocos}
        {desenhar_seres}
    }}
</script>
"""
st.components.v1.html(html_canvas, height=ALTURA + 25)

# Telemetria do Painel
c1.metric(label="🧬 Geração Atual", value=st.session_state.geracao)
c2.metric(label="⏳ Tempo p/ Seleção", value=f"{DURACAO_GERACAO - st.session_state.cronometro} ticks")
c3.metric(label="🏆 Melhor Score Anterior", value=f"{st.session_state.historico_fitness:.1f}")
c4.metric(label="🌤️ Clima do Mundo", value=st.session_state.clima)

# Loop contínuo
time.sleep(1 / fps)
st.rerun()
