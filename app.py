import streamlit as st
from cryptography.fernet import Fernet, InvalidToken
import base64
import zipfile
import io

def generate_key():
    return Fernet.generate_key()

def encrypt_file(file_data, key):
    fernet = Fernet(key)
    return fernet.encrypt(file_data)

def decrypt_file(file_data, key_data):
    try:
        key_stripped = key_data.strip().replace(b'\n', b'').replace(b'\r', b'')
        if len(key_stripped) != 44:
            return "KEY_FORMAT_ERROR"
        base64.urlsafe_b64decode(key_stripped)

        fernet = Fernet(key_stripped)
        return fernet.decrypt(file_data)
    except InvalidToken:
        return "INVALID_KEY"
    except Exception as e:
        return f"ERROR: {e}"

st.set_page_config(page_title="Encrypt/Decrypt", page_icon="🔐")
st.title("🔐 File Encryptor & Decryptor")

mode = st.radio("Select Mode", ["Encrypt", "Decrypt"])

if mode == "Encrypt":
    uploaded_file = st.file_uploader("Upload file to encrypt")

    if uploaded_file:
        file_bytes = uploaded_file.read()
        key = generate_key()
        encrypted = encrypt_file(file_bytes, key)

        # Creating a ZIP with .enc and .key
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("encrypted_file.enc", encrypted)
            zipf.writestr("secret.key", key)
        zip_buffer.seek(0)

        st.success("✅ Encrypted successfully!")
        st.download_button("📦 Download Encrypted Package (.zip)", zip_buffer, file_name="encrypted_package.zip")

elif mode == "Decrypt":
    encrypted_file = st.file_uploader("Upload encrypted file", type=["enc"])
    key_file = st.file_uploader("Upload secret key", type=["key"])

    if encrypted_file and key_file:
        encrypted_data = encrypted_file.read()
        key_data = key_file.read()

        result = decrypt_file(encrypted_data, key_data)

        if result == "INVALID_KEY":
            st.error("❌ Invalid key. Decryption failed.")
        elif result == "KEY_FORMAT_ERROR":
            st.error("❌ Secret key format is incorrect (must be 44-byte base64).")
        elif isinstance(result, str) and result.startswith("ERROR:"):
            st.error(result)
        else:
            st.success("✅ Decryption successful!")
            st.download_button("📂 Download Decrypted File", result, file_name="decrypted_output.txt")
