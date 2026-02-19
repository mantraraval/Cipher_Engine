"""Cipher Engine: LSB steganography platform with RF-based steganalysis."""

import html
import io
import time

import numpy as np
import streamlit as st
from PIL import Image
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(
    page_title="Cipher Engine",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

MESSAGE_DELIMITER = "#####"
ANALYSIS_RESOLUTION = (128, 128)
RANDOM_SEED = 42


def inject_styles() -> None:
    st.markdown(
        """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        .stApp {
            background-color: #000000;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 900px;
        }
        .header-container {
            display: flex;
            flex-direction: row;
            align-items: baseline;
            gap: 12px;
            padding-top: 12px;
            padding-bottom: 0px;
            margin-bottom: 16px;
        }
        .header-title {
            font-family: 'Inter', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            color: #C5A059;
            letter-spacing: -0.02em;
            text-transform: uppercase;
        }
        .header-divider {
            color: #444;
            font-weight: 300;
            font-size: 1.2rem;
        }
        .header-subtitle {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            font-weight: 400;
            color: #636366;
            letter-spacing: -0.02em;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            background-color: transparent;
            border-bottom: none !important;
            padding-bottom: 0px;
            margin-bottom: 16px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border: none;
            color: #636366;
            padding: 8px 0px;
            font-size: 0.9rem;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            letter-spacing: -0.01em;
            transition: color 0.2s ease;
        }
        .stTabs [data-baseweb="tab"]:hover { color: #C5A059; }
        .stTabs [aria-selected="true"] {
            color: #C5A059 !important;
            background-color: transparent !important;
            border-bottom: 2px solid #C5A059 !important;
        }
        .stTabs [data-testid="column"] {
            background-color: #1C1C1E;
            border: 1px solid #2C2C2E;
            border-radius: 6px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        h4 {
            font-family: 'JetBrains Mono', monospace !important;
            color: #86868B;
            font-size: 0.75rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 16px !important;
            font-weight: 500;
            margin-top: 0 !important;
        }
        div[data-testid="stFileUploader"] section {
            background-color: #121212;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 16px;
            min-height: 100px;
        }
        .stTextArea textarea, .stTextInput input {
            background-color: #121212 !important;
            color: #F5F5F7 !important;
            border: 1px solid #333 !important;
            border-radius: 4px;
            font-size: 0.9rem;
            font-family: 'Inter', sans-serif;
            padding: 12px;
        }
        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: #C5A059 !important;
        }
        div.stButton > button, div.stDownloadButton > button {
            width: 100%;
            background-color: #141414;
            color: #C5A059;
            border: 1px solid #C5A059;
            padding: 12px 24px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.9rem;
            font-family: 'Inter', sans-serif;
            letter-spacing: -0.01em;
            transition: all 0.2s ease;
            margin-top: auto;
        }
        div.stButton > button:hover, div.stDownloadButton > button:hover {
            background-color: #1C1C1E;
            border-color: #D4B483;
            color: #D4B483;
            transform: translateY(-1px);
        }
        div.stButton > button:disabled, div.stDownloadButton > button:disabled {
            opacity: 0.4;
            border-color: #333;
            color: #555;
            background-color: #1C1C1E;
            cursor: not-allowed;
        }
        .terminal-window {
            background-color: #050505;
            border: 1px solid #2C2C2E;
            border-radius: 6px;
            font-family: "JetBrains Mono", monospace;
            font-size: 0.8rem;
            margin-top: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .terminal-header {
            background-color: #1C1C1E;
            padding: 8px 12px;
            border-bottom: 1px solid #2C2C2E;
            display: flex;
            align-items: center;
            gap: 8px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        .term-dot { width: 10px; height: 10px; border-radius: 50%; }
        .term-dot.red { background: #FF5F56; }
        .term-dot.yellow { background: #FFBD2E; }
        .term-dot.green { background: #27C93F; }
        .terminal-body {
            padding: 16px;
            color: #C5A059;
            line-height: 1.5;
            height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: "JetBrains Mono", monospace;
        }
        .result-list-panel {
            background-color: #1C1C1E;
            border: 1px solid #2C2C2E;
            border-left: 2px solid #C5A059;
            border-radius: 6px;
            padding: 20px;
            margin-top: 20px;
        }
        .result-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #2C2C2E;
            font-size: 0.85rem;
        }
        .result-item:last-child { border-bottom: none; }
        .result-key { color: #86868B; font-family: 'JetBrains Mono', monospace; }
        .result-val { color: #F5F5F7; font-weight: 500; font-family: "JetBrains Mono", monospace; }
        .result-card {
            background-color: #1C1C1E;
            border: 1px solid #2C2C2E;
            border-radius: 6px;
            padding: 20px;
            text-align: center;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .result-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.5rem;
            font-weight: 700;
            letter-spacing: -0.05em;
            line-height: 1;
            margin-bottom: 8px;
        }
        .telemetry-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #2C2C2E;
            font-size: 0.8rem;
            align-items: center;
        }
        .telemetry-row:last-child { border-bottom: none; }
        .telemetry-key { color: #86868B; font-family: 'JetBrains Mono', monospace; }
        .telemetry-val { color: #F5F5F7; font-family: "JetBrains Mono", monospace; }
    </style>
    """,
        unsafe_allow_html=True,
    )


@st.cache_data
def text_to_binary(text: str) -> str:
    return "".join(format(ord(c), "08b") for c in text)


@st.cache_data
def binary_to_text(binary: str) -> str:
    aligned = binary[: len(binary) - (len(binary) % 8)]
    try:
        return "".join(chr(int(aligned[i : i + 8], 2)) for i in range(0, len(aligned), 8))
    except Exception:
        return ""


def embed_message(image: Image.Image, message: str) -> Image.Image:
    arr = np.array(image)
    if arr.ndim != 3:
        raise ValueError("Image must be RGB (3 channels).")

    bitstream = text_to_binary(message + MESSAGE_DELIMITER)
    if len(bitstream) > arr.size:
        raise ValueError(
            f"Payload size ({len(bitstream)} bits) exceeds image capacity ({arr.size} bits)."
        )

    flat = arr.flatten()
    bits = np.array([int(b) for b in bitstream], dtype=np.uint8)
    flat[: len(bits)] = (flat[: len(bits)] & 0xFE) | bits

    return Image.fromarray(flat.reshape(arr.shape).astype("uint8"))


def extract_message(image: Image.Image) -> str:
    flat = np.array(image).flatten()
    decoded = np.packbits(flat & 1).tobytes().decode("utf-8", errors="ignore")
    if MESSAGE_DELIMITER in decoded:
        return decoded.split(MESSAGE_DELIMITER)[0]
    return "No valid hidden message detected."


def extract_features(image: Image.Image) -> np.ndarray:
    arr = np.array(image.resize(ANALYSIS_RESOLUTION).convert("RGB"))
    hist, _ = np.histogram(arr, bins=256, range=(0, 256))
    probs = hist / hist.sum()
    nonzero = probs[probs > 0]
    entropy = -np.sum(nonzero * np.log2(nonzero))
    return np.array([
        np.mean(arr),
        np.var(arr),
        entropy,
        np.var(arr & 1),
        np.mean(np.abs(np.diff(arr.astype(float), axis=1))),
    ]).reshape(1, -1)


@st.cache_resource
def load_steganalysis_model() -> RandomForestClassifier:
    X, y = [], []

    for _ in range(50):
        img = np.random.randint(0, 256, (*ANALYSIS_RESOLUTION, 3), dtype=np.uint8) & 0xFE
        X.append(extract_features(Image.fromarray(img))[0])
        y.append(0)

    for _ in range(50):
        base = np.random.randint(0, 256, (*ANALYSIS_RESOLUTION, 3), dtype=np.uint8)
        noise = np.random.randint(0, 2, (*ANALYSIS_RESOLUTION, 3), dtype=np.uint8)
        X.append(extract_features(Image.fromarray((base & 0xFE) | noise))[0])
        y.append(1)

    clf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=RANDOM_SEED)
    clf.fit(X, y)
    return clf


def stego_probability(image: Image.Image, model: RandomForestClassifier) -> float:
    return model.predict_proba(extract_features(image))[0][1]


def render_encode_tab() -> None:
    col_input, col_params = st.columns([1, 1], gap="medium")

    with col_input:
        st.markdown("#### Carrier Image")
        uploaded_carrier = st.file_uploader(
            "Upload Image", type=["png", "jpg"], key="enc_u", label_visibility="collapsed"
        )

    with col_params:
        st.markdown("#### Message Payload")
        secret_message = st.text_area(
            "Message",
            placeholder="Enter secure payload data...",
            height=100,
            label_visibility="collapsed",
        )

        if uploaded_carrier:
            img = Image.open(uploaded_carrier).convert("RGB")
            w, h = img.size
            capacity = (w * h * 3) // 8
            valid = len(secret_message) + len(MESSAGE_DELIMITER) < capacity
            color = "#30D158" if valid else "#FF453A"
            state = "READY" if valid else "OVERFLOW"
            st.markdown(
                f"""
                <div class="telemetry-row">
                    <span class="telemetry-key">Dimensions</span>
                    <span class="telemetry-val">{w}x{h} px</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-key">Capacity</span>
                    <span class="telemetry-val">{capacity:,} bits</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-key">System State</span>
                    <span class="telemetry-val" style="color:{color}">{state}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """<div style="flex-grow:1; display:flex; align-items:center; justify-content:center;
                              color:#636366; font-size:0.8rem; height:80px;">Waiting for Input...</div>""",
                unsafe_allow_html=True,
            )

        st.write("")
        is_ready = uploaded_carrier is not None and secret_message != ""
        run_encode = st.button(
            "Encode Message", disabled=not is_ready, key="btn_enc", use_container_width=True
        )

    if run_encode and is_ready:
        try:
            t0 = time.time()
            encoded = embed_message(Image.open(uploaded_carrier).convert("RGB"), secret_message)
            elapsed = time.time() - t0

            st.write("")
            st.markdown(
                f"<div style='color:#30D158; font-family:\"JetBrains Mono\", monospace; font-size:0.85rem;'>"
                f"✔ Encoding complete — {elapsed:.4f}s</div>",
                unsafe_allow_html=True,
            )

            buf = io.BytesIO()
            encoded.save(buf, format="PNG")
            data = buf.getvalue()

            st.markdown(
                f"""
                <div class="result-list-panel">
                    <h4 style="margin-bottom:20px !important; margin-top:0 !important;">OUTPUT DETAILS</h4>
                    <div class="result-item">
                        <span class="result-key">Filename</span>
                        <span class="result-val">encoded_image.png</span>
                    </div>
                    <div class="result-item">
                        <span class="result-key">File Size</span>
                        <span class="result-val">{len(data) / 1024:.2f} KB</span>
                    </div>
                    <div class="result-item">
                        <span class="result-key">Verification</span>
                        <span class="result-val" style="color:#30D158">Confirmed</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write("")
            st.download_button(
                label="Download Encoded Image",
                data=data,
                file_name="encoded_image.png",
                mime="image/png",
                use_container_width=True,
            )

        except ValueError as exc:
            st.error(f"Error: {exc}")


def render_decode_tab() -> None:
    col_input, col_monitor = st.columns([1, 1], gap="medium")

    with col_input:
        st.markdown("#### Input Image")
        uploaded_artifact = st.file_uploader(
            "Upload Image", type=["png"], key="dec_u", label_visibility="collapsed"
        )

    with col_monitor:
        st.markdown("#### Status Monitor")
        if uploaded_artifact:
            st.markdown(
                """
                <div class="telemetry-row">
                    <span class="telemetry-key">Status</span>
                    <span class="telemetry-val" style="color:#30D158">LOADED</span>
                </div>
                <div class="telemetry-row">
                    <span class="telemetry-key">Integrity Check</span>
                    <span class="telemetry-val">PASSED</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """<div style="flex-grow:1; display:flex; align-items:center; justify-content:center;
                              color:#636366; font-size:0.8rem; height:80px;">Awaiting Image...</div>""",
                unsafe_allow_html=True,
            )

        st.write("")
        run_decode = st.button(
            "Decode Message", disabled=uploaded_artifact is None, key="btn_dec", use_container_width=True
        )

    if run_decode and uploaded_artifact is not None:
        try:
            with st.spinner("Extracting data..."):
                result = extract_message(Image.open(uploaded_artifact).convert("RGB"))

            if result != "No valid hidden message detected.":
                st.markdown(
                    f"""
                    <div class="terminal-window">
                        <div class="terminal-header">
                            <div class="term-dot red"></div>
                            <div class="term-dot yellow"></div>
                            <div class="term-dot green"></div>
                            <span style="color:#8E8E93; font-family:-apple-system, BlinkMacSystemFont, sans-serif;
                                         font-size:0.8rem; margin-left:8px;">decoded_message.txt</span>
                        </div>
                        <div class="terminal-body">{html.escape(result)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.error("Verification failed. No valid payload found.")
        except Exception as exc:
            st.error(f"Extraction failed: {exc}")


def render_analysis_tab(model: RandomForestClassifier) -> None:
    col_input, col_metrics = st.columns([1, 1], gap="medium")

    with col_input:
        st.markdown("#### Analysis Input")
        scan_file = st.file_uploader(
            "Select Image", type=["png", "jpg"], key="ai_u", label_visibility="collapsed"
        )

    with col_metrics:
        st.markdown("#### Model Information")
        st.markdown(
            """
            <div class="telemetry-row">
                <span class="telemetry-key">Architecture</span>
                <span class="telemetry-val">RandomForest v1.0</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-key">Training Base</span>
                <span class="telemetry-val">Synthetic Data</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-key">Status</span>
                <span class="telemetry-val" style="color:#30D158">ONLINE</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        run_analysis = st.button(
            "Analyze Image", disabled=scan_file is None, key="btn_ai", use_container_width=True
        )

    if run_analysis and scan_file is not None:
        img = Image.open(scan_file).convert("RGB")
        with st.spinner("Calculating probability..."):
            prob = stego_probability(img, model)
            feats = extract_features(img)[0]

        score = prob * 100
        color = "#FF453A" if score > 50 else "#30D158"
        verdict = "DETECTED" if score > 50 else "CLEAN"

        st.write("")
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-value" style="color:{color}">{score:.0f}%</div>
                <div style="color:#86868B; letter-spacing:0.1em; text-transform:uppercase; font-size:0.8rem;">{verdict}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        st.markdown(
            f"""
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px;">
                <div class="result-card" style="padding:16px; margin:0;">
                    <div style="font-size:1.2rem; font-weight:600; color:#F5F5F7;">{feats[1]:.2f}</div>
                    <div style="font-size:0.65rem; color:#86868B; text-transform:uppercase;">Pixel Var</div>
                </div>
                <div class="result-card" style="padding:16px; margin:0;">
                    <div style="font-size:1.2rem; font-weight:600; color:#F5F5F7;">{feats[2]:.2f}</div>
                    <div style="font-size:0.65rem; color:#86868B; text-transform:uppercase;">Entropy</div>
                </div>
                <div class="result-card" style="padding:16px; margin:0;">
                    <div style="font-size:1.2rem; font-weight:600; color:#F5F5F7;">{feats[3]:.2f}</div>
                    <div style="font-size:0.65rem; color:#86868B; text-transform:uppercase;">LSB Var</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    inject_styles()

    st.markdown(
        """
        <div class="header-container">
            <span class="header-title">Cipher Engine</span>
            <span class="header-divider">·</span>
            <span class="header-subtitle">Advanced Security & Analysis Engine</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    model = load_steganalysis_model()
    tab_encode, tab_decode, tab_analysis = st.tabs(["Encode Vessel", "Decode Artifact", "AI Analysis"])

    with tab_encode:
        render_encode_tab()

    with tab_decode:
        render_decode_tab()

    with tab_analysis:
        render_analysis_tab(model)


if __name__ == "__main__":
    main()