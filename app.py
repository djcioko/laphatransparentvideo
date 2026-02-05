import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Alpha Video Pro", layout="centered")

st.title("🎬 Alpha Video Converter + Chroma Key")
st.markdown("Reglează setările pentru a elimina fundalul verde și a obține transparență reală.")

# 1. Upload
uploaded_file = st.file_uploader("Încarcă video (max 10s)", type=["mov", "mp4", "webm"])

if uploaded_file:
    with open("input_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    
    st.video("input_video.mp4")

    # 2. Setări Chroma Key
    st.sidebar.header("Setări Transparență")
    target_color = st.sidebar.color_picker("Alege culoarea de eliminat", "#498d54")
    similarity = st.sidebar.slider("Similarity (Cât de multă culoare elimină)", 0.01, 1.0, 0.12)
    blend = st.sidebar.slider("Smoothness (Marginile petalelor)", 0.01, 1.0, 0.10)
    
    # Transformăm HEX în format FFmpeg
    clean_color = target_color.replace("#", "0x")

    # 3. Format Export
    option = st.selectbox(
        "Format de ieșire:",
        ("Apple ProRes 4444", "VP9 WebM", "Alpha Mask Only")
    )

    if st.button("Procesează și Elimină Fundalul"):
        output_file = "transparent_render"
        
        # Filtru complex pentru eliminare fundal
        vf_filter = f"colorkey={clean_color}:{similarity}:{blend}"

        if option == "Apple ProRes 4444":
            output_file += ".mov"
            cmd = [
                "ffmpeg", "-y", "-i", "input_video.mp4",
                "-vf", vf_filter,
                "-c:v", "prores_ks", "-profile:v", "4",
                "-vendor", "apl0", "-pix_fmt", "yuva444p10le", output_file
            ]
        elif option == "VP9 WebM":
            output_file += ".webm"
            cmd = [
                "ffmpeg", "-y", "-i", "input_video.mp4",
                "-vf", vf_filter,
                "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", output_file
            ]
        else:
            output_file += "_mask.mp4"
            cmd = [
                "ffmpeg", "-y", "-i", "input_video.mp4",
                "-vf", f"{vf_filter},alphaextract", output_file
            ]

        try:
            with st.spinner("Se elimină fundalul și se randează..."):
                subprocess.run(cmd, check=True)
            
            st.success("Gata! Acum fundalul verde este transparent.")
            with open(output_file, "rb") as f:
                st.download_button("Descarcă Video Transparent", f, file_name=output_file)
        except Exception as e:
            st.error(f"Eroare: {e}")

---

### De ce va merge acum în OBS:
1.  **Eliminare activă:** Codul nu mai face doar o conversie de format, ci "sapă" în imagine și transformă culoarea selectată în pixeli invizibili folosind filtrul `colorkey`.
2.  **Ajustare vizuală:** Dacă petalele tale au margini verzi, crește puțin **Smoothness**. Dacă mai rămân pete verzi pe fundal, crește **Similarity**.
3.  **Testul suprem:** Când descarci fișierul `.mov`, pune-l în OBS peste o altă imagine. Ar trebui să vezi direct imaginea de dedesubt printre petale.

**Vrei să adaug și o funcție de "Preview" (o poză) care să îți arate cum arată transparența înainte să randezi tot video-ul?**
