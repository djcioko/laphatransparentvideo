import streamlit as st
import subprocess
import os
from PIL import Image

st.set_page_config(page_title="Alpha Video Pro", layout="wide")

st.title("🎬 Alpha Video Converter + Chroma Key")
st.info("Reglează setările din stânga pentru a elimina fundalul verde.")

# 1. Upload
uploaded_file = st.file_uploader("Încarcă video (max 10s)", type=["mov", "mp4", "webm"])

if uploaded_file:
    with open("input_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Video Original")
        st.video("input_video.mp4")

    # 2. Setări Chroma Key în Sidebar
    st.sidebar.header("Setări Transparență")
    target_color = st.sidebar.color_picker("Alege culoarea de eliminat", "#498d54")
    similarity = st.sidebar.slider("Similarity (Eliminare fundal)", 0.01, 1.0, 0.12)
    blend = st.sidebar.slider("Smoothness (Margini petale)", 0.01, 1.0, 0.10)
    
    clean_color = target_color.replace("#", "0x")

    # 3. Funcție Preview (Generăm un cadru să vedem dacă e bine)
    if st.sidebar.button("Generează Preview"):
        preview_cmd = [
            "ffmpeg", "-y", "-i", "input_video.mp4",
            "-vf", f"colorkey={clean_color}:{similarity}:{blend}",
            "-frames:v", "1", "preview.png"
        ]
        subprocess.run(preview_cmd)
        with col2:
            st.subheader("Preview Transparență (pe negru)")
            st.image("preview.png")

    # 4. Format Export
    option = st.selectbox(
        "Alege formatul de export (OBS suportă ambele):",
        ("Apple ProRes 4444 (.mov)", "VP9 WebM (.webm)")
    )

    if st.button("RENDER FINAL"):
        output_file = "transparent_render"
        vf_filter = f"colorkey={clean_color}:{similarity}:{blend}"

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
                "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", output_file
            ]

        try:
            with st.spinner("Se procesează..."):
                subprocess.run(cmd, check=True)
            
            st.success("Conversie reușită!")
            with open(output_file, "rb") as f:
                st.download_button("📥 DESCARCĂ FIȘIERUL TRANSPARENT", f, file_name=output_file)
        except Exception as e:
            st.error(f"Eroare la procesare: {e}")
