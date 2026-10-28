import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from googleapiclient.discovery import build

# Configuração da página com tema escuro nativo
st.set_page_config(
    page_title="TubeModeler Pro - Garimpador AI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Avançada (Tema Dark Profissional)
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    .studio-header {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .canal-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .canal-card:hover {
        border-color: #ef4444;
        transform: translateY(-2px);
    }
    .badge-origem {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .metric-box {
        background-color: #1f2937;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        border: 1px solid #374151;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho Principal Estilizado
st.markdown("""
    <div class="studio-header">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span style="background-color: #ef4444; color: white; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: bold;">🔥 TUBE MODELER PRO</span>
                <h1 style="margin: 10px 0 5px 0; font-size: 28px; color: #ffffff;">Radar de Canais Outliers & Oportunidades</h1>
                <p style="color: #9ca3af; margin: 0; font-size: 14px;">Garimpe canais de alto engajamento através da relação exata de Views ÷ Inscritos + Canais de Referência.</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Barra Lateral (Sidebar) Moderna para Parâmetros e Referências
with st.sidebar:
    st.markdown("### ⚙️ Painel de Controle")
    st.markdown("---")
    
    chave_api = st.text_input("🔑 Chave da API do YouTube", value="AIzaSyBGrYp-CUjY6ih-cGs8nbtWmXL9bFv-tdE", type="password")
    
    nicho_opcao = st.selectbox(
        "📂 Escolha o Nicho",
        ["Finanças Pessoais", "Histórias / Mistério", "Cortes de Podcast", "Música", "Tecnologia", "Outro (Digitar abaixo)"]
    )
    if nicho_opcao == "Outro (Digitar abaixo)":
        nicho = st.text_input("🎯 Digite o seu Nicho", value="curiosidades")
    else:
        nicho = nicho_opcao.lower()
        
    max_resultados = st.slider("🔍 Quantos canais buscar", 10, 50, 20, 10)
    max_inscritos = st.number_input("👥 Máximo de Inscritos", value=35000, step=5000)
    min_relacao = st.number_input("📈 Relação Mínima (Views/Inscritos)", value=30.0, step=5.0)
    idade_maxima = st.number_input("📅 Idade máxima (Dias)", value=300, step=30)
    
    st.markdown("---")
    st.markdown("### 🎯 Canais de Referência")
    st.markdown("<p style='font-size: 11px; color: #9ca3af;'>Cole os IDs dos canais que deseja analisar diretamente (um por linha):</p>", unsafe_allow_html=True)
    canais_ref_texto = st.text_area("IDs de Referência", value="", height=100, placeholder="Ex: UC_x5XG1OV2P6uZZ5FSM9Ttw")
    lista_referencias = [c.strip() for c in canais_ref_texto.split("\n") if c.strip()]
    
    st.markdown("---")
    executar_busca = st.button("🚀 INICIAR GARIMPAGEM", use_container_width=True, type="primary")

# Função de busca otimizada
def pegar_dados_canal(youtube_client, canal_id, origem="Busca automática"):
    try:
        stats = youtube_client.channels().list(
            id=canal_id, part="statistics,snippet"
        ).execute()["items"][0]
        
        nome = stats["snippet"]["title"]
        descricao = stats["snippet"].get("description", "Sem descrição.")
        data_criacao = stats["snippet"]["publishedAt"]
        foto_url = stats["snippet"]["thumbnails"]["high"]["url"]
        
        inscritos = int(stats["statistics"].get("subscriberCount", 0))
        total_visualizacoes = int(stats["statistics"].get("viewCount", 0))
        qtd_videos = int(stats["statistics"].get("videoCount", 0))
        
        media_por_video = total_visualizacoes / qtd_videos if qtd_videos > 0 else 0
        relacao = media_por_video / inscritos if inscritos > 0 else 0
        
        return {
            "foto": foto_url,
            "nome": nome,
            "descricao": descricao[:140] + "...",
            "canal_id": canal_id,
            "inscritos": inscritos,
            "videos": qtd_videos,
            "media_visualizacoes_video": round(media_por_video),
            "relacao_vid_ins": round(relacao, 2),
            "data_criacao": data_criacao[:10],
            "url": f"https://youtube.com/channel/{canal_id}",
            "origem": origem
        }
    except Exception as e:
        return None

# Área Principal de Resultados
if executar_busca:
    if not chave_api:
        st.error("⚠️ Insira a Chave da API do YouTube na barra lateral.")
    else:
        try:
            youtube = build("youtube", "v3", developerKey=chave_api)
            todos_canais = []
            
            with st.spinner(f"🔍 Analisando ecossistema e referências..."):
                data_limite = (datetime.now() - timedelta(days=idade_maxima)).isoformat() + "Z"
                
                # 1. Busca Automática por Nicho
                request = youtube.search().list(
                    q=nicho, type="channel", part="id,snippet",
                    maxResults=max_resultados, publishedAfter=data_limite
                )
                response = request.execute()
                
                for item in response.get("items", []):
                    canal_id = item["id"]["channelId"]
                    dados = pegar_dados_canal(youtube, canal_id, origem="Outlier Detectado")
                    if dados and 0 < dados["inscritos"] <= max_inscritos:
                        if dados["relacao_vid_ins"] >= min_relacao:
                            todos_canais.append(dados)
                
                # 2. Análise Direta dos Canais de Referência (se informados)
                if lista_referencias:
                    for cid in lista_referencias:
                        dados_ref = pegar_dados_canal(youtube, cid, origem="✅ Referência Direta")
                        if dados_ref:
                            todos_canais.append(dados_ref)
            
            if todos_canais:
                st.success(f"🎉 Sucesso! Encontrados {len(todos_canais)} canais para modelagem.")
                
                for canal in todos_canais:
                    st.markdown(f"""
                        <div class="canal-card">
                            <div style="display: flex; align-items: flex-start; gap: 20px;">
                                <img src="{canal['foto']}" style="width: 90px; height: 90px; border-radius: 50%; object-fit: cover; border: 2px solid #374151;">
                                <div style="flex-grow: 1;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                        <h3 style="margin: 0; color: #ffffff; font-size: 20px;">{canal['nome']}</h3>
                                        <span class="badge-origem">{canal['origem']}</span>
                                    </div>
                                    <p style="color: #9ca3af; font-size: 13px; margin-bottom: 12px;">{canal['descricao']}</p>
                                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 15px;">
                                        <div class="metric-box"><span style="font-size: 11px; color: #9ca3af;">Inscritos</span><br><b style="color: #fff;">{canal['inscritos']:,}</b></div>
                                        <div class="metric-box"><span style="font-size: 11px; color: #9ca3af;">Média Views/Vídeo</span><br><b style="color: #38bdf8;">{canal['media_visualizacoes_video']:,}</b></div>
                                        <div class="metric-box"><span style="font-size: 11px; color: #9ca3af;">Índice Outlier</span><br><b style="color: #4ade80;">{canal['relacao_vid_ins']}x</b></div>
                                        <div class="metric-box"><span style="font-size: 11px; color: #9ca3af;">Criação</span><br><b style="color: #fff;">{canal['data_criacao']}</b></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col_l, col_r = st.columns([6, 1])
                    with col_r:
                        st.link_button("🔗 Ver Canal", canal['url'], use_container_width=True)
                    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                
                df = pd.DataFrame(todos_canais)
                nome_arquivo = f"tubemodeler-{nicho.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df.to_excel(nome_arquivo, index=False)
                
                with open(nome_arquivo, "rb5") as file:
                    st.download_button(
                        label="📥 Descarregar Relatório Completo em Excel",
                        data=file,
                        file_name=nome_arquivo,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            else:
                st.warning("⚠️ Nenhum canal atingiu estes parâmetros rígidos nesta busca. Tente ajustar os filtros na barra lateral.")
                
        except Exception as e:
            st.error(f"❌ Erro na execução da API: {e}")
else:
    st.info("👈 Configure os seus parâmetros ou adicione canais de referência na **barra lateral à esquerda** e clique em **INICIAR GARIMPAGEM**.")
