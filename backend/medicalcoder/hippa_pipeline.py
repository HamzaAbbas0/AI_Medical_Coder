import requests
import paramiko
import os
import sys
from pathlib import Path

# -----------------------------
# CONFIGURATION
# -----------------------------
OCR_URL = "http://10.0.0.84:8122/ocr-direct"
OCR_HEADERS = {
    'x-api-key': 'WJ515kbawWpzUcxYajXA4BuIgHNd11QmC5s'
}

SFTP_HOST = "103.217.177.50"
SFTP_PORT = 2099
SFTP_USER = "ehr"
SFTP_PASS = "@hr@!s%^@31"
SFTP_ROOT = "/opt/FileServer/TREE/ehr"

HIPAA_URL = "http://110.93.225.217:8081/redact-text-batched"
 

#LOCAL_INPUT_FILE = r"( Coded ) EMCT_9200_Berry_20250724_2_Robinson, Christopher_O.pdf"
LOCAL_TXT_RESULT = "result.txt"
REMOTE_TEST_DIR = "ham_hippa_test"

REMOTE_OUTPUT_DIR = "ham_hippa_output"

# -----------------------------
# STEP 1: RUN OCR EXTRACTION
# -----------------------------
def run_ocr(file_path):
    try:
        print("[1] Running OCR on:", file_path)
        with open(file_path, "rb") as f:
            files = [('files', ('test.pdf', f, 'application/pdf'))]
            response = requests.post(OCR_URL, headers=OCR_HEADERS, files=files, timeout=1000)
        
        response.raise_for_status()
        data = response.json()
        ocr_text = data.get("ocr_result", "")
        if not ocr_text:
            raise ValueError("OCR result is empty.")
        
        with open(LOCAL_TXT_RESULT, "w", encoding="utf-8") as out:
            out.write(ocr_text)
        print(f"[✓] OCR completed. Saved to {LOCAL_TXT_RESULT}")
        return LOCAL_TXT_RESULT
    
    except requests.exceptions.RequestException as e:
        print(f"[✗] OCR request failed: {e}")
        # sys.exit(1)
    except ValueError as ve:
        print(f"[✗] OCR output error: {ve}")
        # sys.exit(1)


# -----------------------------
# STEP 2: UPLOAD TO SFTP
# -----------------------------
def upload_to_sftp(local_path, remote_dir):
    try:
        print(f"[2] Uploading {local_path} to SFTP...")

        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)

        remote_full_path = f"{SFTP_ROOT}/{remote_dir}/{os.path.basename(local_path)}"

        # Ensure remote dir exists
        try:
            sftp.chdir(f"{SFTP_ROOT}/{remote_dir}")
        except IOError:
            print(f"Creating remote directory {remote_dir}...")
            sftp.mkdir(f"{SFTP_ROOT}/{remote_dir}")

        sftp.put(local_path, remote_full_path)
        print(f"[✓] File uploaded successfully: {remote_full_path}")

        sftp.close()
        transport.close()

        return remote_full_path

    except Exception as e:
        print(f"[✗] SFTP upload failed: {e}")
        # sys.exit(1)


# -----------------------------
# STEP 3: CALL HIPAA REDACTION API
# -----------------------------
def run_hipaa_redaction(input_remote_path, output_dir):
    try:
        print(f"[3] Running HIPAA redaction for: {input_remote_path}")

        payload = {
            "path": input_remote_path,
            "output_path": f"{SFTP_ROOT}/{output_dir}"
        }

        response = requests.post(HIPAA_URL, json=payload, timeout=2000)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success":
            raise ValueError(f"Redaction failed: {data}")

        print(f"[✓] HIPAA redaction completed. Output file: {data.get('redacted_file')}")
        # print(f"PII Count: {data.get('pii_count')}")
        return data

    except requests.exceptions.RequestException as e:
        print(f"[✗] HIPAA API request failed: {e}")
        # sys.exit(1)
    except ValueError as ve:
        print(f"[✗] HIPAA processing error: {ve}")
        # sys.exit(1)


# -----------------------------
# STEP 4: DOWNLOAD REDACTED FILE
# -----------------------------
def download_from_sftp(remote_file_path, local_dest):
    try:
        print(f"[4] Downloading redacted file from SFTP: {remote_file_path}")

        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)

        os.makedirs(os.path.dirname(local_dest), exist_ok=True)
        sftp.get(remote_file_path, local_dest)
        print(f"[✓] File downloaded successfully: {local_dest}")

        sftp.close()
        transport.close()

    except Exception as e:
        print(f"[✗] SFTP download failed: {e}")
        # sys.exit(1)


# -----------------------------
# MAIN WORKFLOW
# -----------------------------
def hipaa_main(LOCAL_INPUT_FILE, REMOTE_TEST_DIR=REMOTE_TEST_DIR, REMOTE_OUTPUT_DIR=REMOTE_OUTPUT_DIR):
    try:
        
        ocr_result_file = run_ocr(LOCAL_INPUT_FILE)

        
        remote_txt_path = upload_to_sftp(ocr_result_file, REMOTE_TEST_DIR)

    
        hipaa_response = run_hipaa_redaction(remote_txt_path, REMOTE_OUTPUT_DIR)

        
        redacted_remote_file = hipaa_response.get("redacted_file")
        if redacted_remote_file:
            local_output_path = os.path.join(Path.cwd(), os.path.basename(redacted_remote_file))
            download_from_sftp(redacted_remote_file, local_output_path)
        else:
            print("[✗] No redacted file path returned in API response.")

        print("\n[✔] Workflow completed successfully!")

        with open("REDACTED_result.txt", "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        return content

    except Exception as e:
        print(f"[✗] Unexpected error: {e}")
        # sys.exit(1)

