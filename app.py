import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Alpha Video Converter", layout="centered")

st.title("🎬 Alpha Video Exporter")
st.info("Încarcă un video de max 10s pentru a genera versiunea cu transparență.")

# Upload file
uploaded_file = st.file_uploader("Alege fișierul video", type=["mov", "mp4", "webm"])

if uploaded_file is not None:
    # Salvare temporară fișier
    with open("input_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    
    st.video("input_video.mp4")

    # Selecție Format
    option = st.selectbox(
        "Alege setarea de render (Alpha Channel):",
        (
            "Apple ProRes 4444 (High Quality)",
            "HEVC with Alpha (Quicktime/Apple)",
            "VP9 (Web Optimized)",
            "Alpha Extract (Mask Only)",
            "HStack (Side-by-Side)"
        )
    )

    if st.button("Procesează Video"):
        output_file = "output_alpha"
        cmd = []

        if option == "Apple ProRes 4444 (High Quality)":
            output_file += ".mov"
            cmd = [
                "ffmpeg", "-y", "-i", "input_video.mp4",
                "-c:v", "prores_ks", "-profile:v", "4",
                "-vendor", "apl0", "-bits_per_mb", "8000",
                "-pix_fmt", "yuva444p10le", output_file
            ]

        elif option == "HEVC with Alpha (Quicktime/Apple)":
            output_file += ".mov"
            # Format compatibil cu ecosistemul Apple/Rotato
            cmd = [
                "ffmpeg", "-y", "-i", "input_video.mp4",
                "-c:v", "hevc_videotoolbox", "-allow_sw", "1", 
                "-alpha_quality", "1", "-pix_fmt", "yuva444p", output_file
            ]

        elif option == "VP9 (Web Optimized)":
            output_file += ".webm"
            cmd = [
                "ffmpeg", "-y", "-i", "input_video.mp4",
                "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", output_file
            ]

        elif option == "Alpha Extract (Mask Only)":
            output_file += "_mask.mp4"
            cmd = [
                "ffmpeg", "-y", "-i", "input_video.mp4",
                "-vf", "alphaextract,format=yuv420p", output_file
            ]

        try:
            with st.spinner("Se procesează..."):
                subprocess.run(cmd, check=True)
            
            st.success("Conversie reușită!")
            
            with open(output_file, "rb") as file:
                st.download_button(
                    label="Descarcă Fișierul",
                    data=file,
                    file_name=output_file,
                    mime="video/quicktime"
                )
        except Exception as e:
            st.error(f"Eroare la procesare: {e}")