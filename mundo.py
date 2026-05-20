import streamlit as st
import random
import math
import time

# ==========================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==========================================
st.set_page_config(page_title="Mundo Artificial Evolutivo", layout="centered")
st.title("🧠 Simulação de Vida Artificial Autônoma")
st.markdown("Seres virtuais que aprendem a coletar blocos, construir abrigos e sobreviver a desastres naturais através de Algoritmos Genéticos.")

# Dimensões lógicas do mundo virtual
LARGURA, ALTURA = 700, 500

# ==========================================
# CLASSES DO MOTOR DE INTELIGÊNCIA ARTIFICIAL
# ==========================================
class Bloco:
    def __init__(self):
        self.x = random.randint(30, LARGURA - 30)
        self.y = random.randint(30, ALTURA - 30)

class Abrigo:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Ser:
    def __init__(self, x, y, cerebro=None):
        self.x = x
        self.y = y
        self.energia = 100.0
        self.blocos_coletados = 0
        self.idade = 0
        self.geracao = cerebro["geracao"] if cerebro else 1
        
        # 18 pesos conectando 6 Entradas a 3 Saídas
        if cerebro:
            self.pesos = list(cerebro["pesos"])
            self.mutar()
        else:
            self.pesos = [random.uniform(-1.0, 1.0) for _ in range(18)]

    def mutar(self):
        """Pequena mutação no cérebro herdado para permitir o aprendizado"""
        for i in range(len(self.pesos)):
            if random.random() < 0.15:  # 15% de chance de mudar um comportamento
                self.pesos[i] += random.uniform(-0.3, 0.3)

    def pensar_e_agir(self, blocos, abrigos, clima):
        self.idade += 1
        self.energia -= 0.3  # Custo constante de sobrevivência

        # --- 1. CAPTAÇÃO DOS SENSORES (INPUTS) ---
        dx_bloco, dy_bloco = 0.0, 0.0
        if blocos:
            b_perto = min(blocos, key=lambda b: math.hypot(b.x - self.x, b.y - self.y))
            dx_bloco = (b_perto.x - self.x) / LARGURA
            dy_bloco = (b_perto.y - self.y) / ALTURA

        dx_abrigo, dy_abrigo = 0.0, 0.0
        if abrigos:
            a_perto = min(abrigos, key=lambda a: math.hypot(a.x - self.x, a.y - self.y))
            dx_abrigo = (a_perto.x - self.x) / LARGURA
            dy_abrigo = (a_perto.y - self.y) / ALTURA

        fome = (100.0 - self.energia) / 100.0
        perigo_clima = 1.0 if clima in ["Seca", "Desastre Natural"] else 0.0

        # --- 2. PROCESSAMENTO NEURAL (TOMADA DE DECISÃO) ---
        out_x = (dx_bloco * self.pesos[0] + dy_bloco * self.pesos[1] + fome * self.pesos[2] + 
                 perigo_clima * self.pesos[3] + dx_abrigo * self.pesos[4] + dy_abrigo * self.pesos[5])
        
        out_y = (dx_bloco * self.pesos[6] + dy_bloco * self.pesos[7] + fome * self.pesos[8] + 
                 perigo_clima * self.pesos[9] + dx_abrigo * self.pesos[10] + dy_abrigo * self.pesos[11])
        
        out_construir = (dx_bloco * self.pesos[12] + dy_bloco * self.pesos[13] + fome * self.pesos[14] + 
                         perigo_clima * self.pesos[15] + dx_abrigo * self.pesos[16] + dy_abrigo * self.pesos[17])

        # --- 3. EXECUÇÃO DA AÇÃO ---
        # Movimentação baseada no pensamento
        self.x += max(-6, min(6, out_x * 6))
        self.y += max(-6, min(6, out_y * 6))
        
        # Limites do mundo
        self.x = max(10, min(LARGURA - 10, self.x))
        self.y = max(10, min(ALTURA - 10, self.y))

        # Decisão voluntária de usar blocos para construir
        if out_construir > 0.5 and self.blocos_coletados >= 2:
            self.blocos_coletados -= 2
            abrigos.append(Abrigo(self.x, self.y))

        # --- 4. EFEITO DO CLIMA NO CORPO ---
        if clima == "Seca":
            self.energia -= 0.2
        elif clima == "Desastre Natural":
            # Verifica se o cérebro dele foi inteligente o suficiente para se mover para perto de um abrigo
            em_seguranca = any(math.hypot(a.x - self.x, a.y - self.y) < 35 for a in abrigos)
            if not em_seguranca:
                self.energia -= 3.0  # Dano massivo por falta de abrigo

# ==========================================
# INICIALIZAÇÃO DO ESTADO DA SESSÃO (MUNDO)
# ==========================================
if "seres" not in st.session_state:
    st.session_state.seres = [Ser(random.randint(50, LARGURA-50), random.randint(50, ALTURA-50)) for _ in range(20)]
    st.session_state.blocos = [Bloco() for _ in range(40)]
    st.session_state.abrigos = []
    st.session_state.clima = "Normal"
    st.session_state.tempo_clima = 30
    st.session_state.ciclo = 0
    st.session_state.max_geracao = 1

# Interface de controle no Streamlit
col1, col2, col3, col4 = st.columns(4)
btn_reset = col1.button("🔄 Reiniciar Mundo")
velocidade = col2.slider("⚡ Velocidade (FPS)", 5, 30, 15)

if btn_reset:
    st.session_state.seres = [Ser(random.randint(50, LARGURA-50), random.randint(50, ALTURA-50)) for _ in range(20)]
    st.session_state.blocos = [Bloco() for _ in range(40)]
    st.session_state.abrigos = []
    st.session_state.clima = "Normal"
    st.session_state.tempo_clima = 30
    st.session_state.ciclo = 0
    st.session_state.max_geracao = 1

# ==========================================
# LOOP DE ATUALIZAÇÃO LOGICA
# ==========================================
st.session_state.ciclo += 1
st.session_state.tempo_clima -= 1

# Mudança climática autônoma
if st.session_state.tempo_clima <= 0:
    st.session_state.clima = random.choice(["Normal", "Chuva", "Seca", "Desastre Natural"])
    st.session_state.tempo_clima = 12 if st.session_state.clima == "Desastre Natural" else 40

# Efeito do Clima no ecossistema (Geração de recursos)
if st.session_state.clima == "Chuva" and random.random() < 0.4:
    st.session_state.blocos.append(Bloco())
elif st.session_state.clima == "Normal" and random.random() < 0.2:
    st.session_state.blocos.append(Bloco())
elif st.session_state.clima == "Desastre Natural" and st.session_state.abrigos and random.random() < 0.15:
    st.session_state.abrigos.pop(random.randint(0, len(st.session_state.abrigos) - 1)) # Destrói abrigo aleatório

# Atualização dos Seres
novos_seres = []
for ser in st.session_state.seres[:]:
    ser.pensar_e_agir(st.session_state.blocos, st.session_state.abrigos, st.session_state.clima)
    
    # Comer / Coletar Bloco próximo
    for bloco in st.session_state.blocos[:]:
        if math.hypot(bloco.x - ser.x, bloco.y - ser.y) < 18:
            if bloco in st.session_state.blocos:
                st.session_state.blocos.remove(bloco)
                ser.blocos_coletados += 1
                ser.energia = min(100.0, ser.energia + 35.0)

    # Lógica de Reprodução Darwiniana (Passa a consciência adiante)
    if ser.energia > 85 and ser.blocos_coletados >= 3 and random.random() < 0.1:
        ser.energia -= 45
        ser.blocos_coletados -= 3
        dna_filho = {"pesos": ser.pesos, "geracao": ser.geracao}
        novos_seres.append(Ser(ser.x + random.randint(-15, 15), ser.y + random.randint(-15, 15), dna_filho))
        if ser.geracao + 1 > st.session_state.max_geracao:
            st.session_state.max_geracao = ser.geracao + 1

    # Filtrar mortos
    if ser.energia <= 0:
        st.session_state.seres.remove(ser)

st.session_state.seres.extend(novos_seres)

# Se houver extinção em massa, novos pioneiros surgem com cérebros em branco
if len(st.session_state.seres) == 0:
    st.session_state.seres = [Ser(random.randint(50, LARGURA-50), random.randint(50, ALTURA-50)) for _ in range(12)]
    st.session_state.abrigos.clear()

# ==========================================
# RENDERIZAÇÃO GRÁFICA VIA HTML5 CANVAS
# ==========================================
# Define a cor do mundo com base no clima atual
cor_fundo = "#228B22"  # Verde Grama
if st.session_state.clima == "Chuva": cor_fundo = "#2F4F4F"
elif st.session_state.clima == "Seca": cor_fundo = "#8B7355"
elif st.session_state.clima == "Desastre Natural": cor_fundo = "#800000"

# Construção das strings de desenho dinâmico para os elementos
desenhar_blocos = "".join([f"ctx.fillStyle = '#8B4513'; ctx.fillRect({b.x}, {b.y}, 8, 8);" for b in st.session_state.blocos])
desenhar_abrigos = "".join([f"ctx.fillStyle = '#4682B4'; ctx.fillRect({a.x}, {a.y}, 18, 18);" for a in st.session_state.abrigos])

desenhar_seres = ""
for ser in st.session_state.seres:
    g = max(0, min(255, int(ser.energia * 2.55)))
    r = max(0, min(255, int((100 - ser.energia) * 2.55)))
    desenhar_seres += f"""
    ctx.beginPath();
    ctx.arc({ser.x}, {ser.y}, 6, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgb({r}, {g}, 0)';
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 0.5;
    ctx.stroke();
    ctx.closePath();
    """

# Injeta a área gráfica integrada na interface Streamlit
html_canvas = f"""
<div style="text-align: center; background-color: #1e1e1e; padding: 10px; border-radius: 8px;">
    <canvas id="mundoCanvas" width="{LARGURA}" height="{HEIGHT:=400}" style="border: 2px solid #555; background-color: {cor_fundo};"></canvas>
</div>
<script>
    var canvas = document.getElementById('mundoCanvas');
    if (canvas) {{
        var ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, {LARGURA}, 400);
        {desenhar_abrigos}
        {desenhar_blocos}
        {desenhar_seres}
    }}
</script>
"""
st.components.v1.html(html_canvas, height=430)

# ==========================================
# PAINEL DE TELEMETRIA E DADOS EM TEMPO REAL
# ==========================================
col4.metric(label="🌤️ Clima Atual", value=st.session_state.clima.upper())
col1.metric(label="👥 População", value=len(st.session_state.seres))
col2.metric(label="🪵 Blocos no Chão", value=len(st.session_state.blocos))
col3.metric(label="🧬 Maior Geração", value=f"Gen {st.session_state.max_geracao}")

# Força o Streamlit a atualizar a tela continuamente criando o efeito de animação
time.sleep(1 / velocidade)
st.rerun()
