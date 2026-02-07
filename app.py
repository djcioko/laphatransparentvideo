import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Alpha Video Pro - Chroma Key Expert", layout="wide")

st.title("🎬 Alpha Video Converter + Precise Chroma Key")
st.markdown("""
<style>
    .stProgress > div > div > div > div { background-color: #00ff00; }
</style>
""", unsafe_allow_html=True)

st.info("Folosește selectorul de culoare (Pipeta) pentru a indica exact nuanța de verde/albastru din video.")

# 1. Upload
uploaded_file = st.file_uploader("Încarcă video (recomandat scurt pentru viteză)", type=["mov", "mp4", "webm"])

if uploaded_file:
    with open("input_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📺 Video Original")
        st.video("input_video.mp4")

    # 2. Setări Chroma Key în Sidebar cu Pipetă
    st.sidebar.header("🎯 Selector Culoare & Precizie")
    
    # Pipeta (Color Picker)
    target_color = st.sidebar.color_picker("Alege culoarea de eliminat (Pipeta)", "#498d54")
    
    # Afișăm codul culorii selectate pentru confirmare
    st.sidebar.code(f"HEX: {target_color}")
    
    # Parametrii FFmpeg pentru colorkey
    similarity = st.sidebar.slider("Similarity (Cât de mult elimină)", 0.001, 1.0, 0.12, format="%.3f")
    blend = st.sidebar.slider("Smoothness (Marginile obiectelor)", 0.001, 1.0, 0.10, format="%.3f")
    
    # Conversie HEX în formatul FFmpeg (0xRRGGBB)
    clean_color = target_color.replace("#", "0x")

    # 3. Funcție Preview
    if st.sidebar.button("🖼️ Generează Preview Cadru"):
        # Extragem un cadru de la secunda 1 (sau 0 dacă e prea scurt)
        preview_cmd = [
            "ffmpeg", "-y", "-i", "input_video.mp4",
            "-vf", f"colorkey={clean_color}:{similarity}:{blend},format=rgba",
            "-frames:v", "1", "preview.png"
        ]
        subprocess.run(preview_cmd)
        
        with col2:
            st.subheader("✨ Rezultat Transparență")
            if os.path.exists("preview.png"):
                st.image("preview.png", caption="Verifică marginile aici (fundalul devine transparent/negru)")
            else:
                st.error("Nu s-a putut genera preview. Verifică formatul video.")

    # 4. Format Export
    st.divider()
    st.subheader("🚀 Export Final cu Alpha Channel")
    option = st.selectbox(
        "Alege formatul de export:",
        ("VP9 WebM (.webm) - Recomandat pentru Browser/OBS", "Apple ProRes 4444 (.mov) - Calitate Maximă")
    )

    if st.button("🔴 ÎNCEPE RENDER"):
        output_file = "transparent_render"
        # Adăugăm format=rgba pentru a asigura canalul alpha în procesare
        vf_filter = f"colorkey={clean_color}:{similarity}:{blend},format=rgba"

        if "ProRes" in option:
            output_file += ".mov"
            cmd = [
                "ffmpeg", "-y", "-i", "input_video.mp4",
                "-vf", vf_filter,
                "-c:v", "prores_ks", "-profile:v", "4",
                "-vendor", "apl0", "-pix_fmt", "yuva444p10le", output_file
            ]
        else:
            output_file += ".webm"
            cmd = [
                "ffmpeg", "-y", "-i", "input_video.mp4",
                "-vf", vf_filter,
                "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-auto-alt-ref", "0", output_file
            ]

        try:
            with st.spinner("Procesare video... Te rog așteaptă."):
                process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            st.success("✅ Conversie reușită!")
            with open(output_file, "rb") as f:
                st.download_button(
                    label="📥 DESCARCĂ FIȘIERUL TRANSPARENT",
                    data=f,
                    file_name=output_file,
                    mime="video/quicktime" if ".mov" in output_file else "video/webm"
                )
        except subprocess.CalledProcessError as e:
            st.error(f"Eroare FFmpeg: {e.stderr}")
        except Exception as e:
            st.error(f"Eroare neașteptată: {e}")

# Curățare fișiere temporare la restart (Opțional)
if st.sidebar.button("Șterge fișierele temporare"):
    for f in ["input_video.mp4", "preview.png", "transparent_render.mov", "transparent_render.webm"]:
        if os.path.exists(f):
            os.remove(f)
    st.rerun()
