import os
import webbrowser
import boto3
import subprocess
from botocore.exceptions import NoCredentialsError
from datetime import datetime, timezone
import re

# Settings
BUCKET_NAME = "vb-alex"  # <-- update this
S3_REGION = "us-east-1"               # <-- update if needed
HTML_OUTPUT_FILE = "page_embed_viewer.html"
LAST_INPUT_FILE = "last_embed.txt"
LAST_BROWSER_FILE = "last_browser.txt"

USERPROFILE = os.environ.get("USERPROFILE", "C:\\Users\\Default")
FIREFOX_USER_PATH = os.path.join(USERPROFILE, "AppData", "Local", "Mozilla Firefox", "firefox.exe")

BROWSERS = {
    "1": ("Chrome", [
        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    ]),
    "2": ("Edge", [
        r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        r"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
    ]),
    "3": ("Firefox", [
        r"C:\\Program Files\\Mozilla Firefox\\firefox.exe",
        r"C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
        FIREFOX_USER_PATH
    ])
}

def get_iframe_code():
    last_code = ""
    last_src = ""

    if os.path.exists(LAST_INPUT_FILE):
        with open(LAST_INPUT_FILE, 'r') as f:
            last_code = f.read().strip()
            match = re.search(r'src=["\']([^"\']+)["\']', last_code)
            if match:
                last_src = match.group(1)

    print("Enter new iframe code (or press Enter to reuse last):")
    if last_src:
        print(f"Previous src: {last_src}")

    new_code = input().strip()

    if new_code:
        with open(LAST_INPUT_FILE, 'w') as f:
            f.write(new_code)
        return new_code
    elif last_code:
        return last_code
    else:
        print("No previous iframe code found. Please input new code.")
        return get_iframe_code()

def generate_html(iframe_code):
    escaped_code = iframe_code.replace("<", "&lt;").replace(">", "&gt;")
    html = f"""
    <html>
    <head><title>Embed Preview</title></head>
    <body style='margin:0'>
        <h3 style='padding:10px; font-family:Arial;'>Embed Code:</h3>
        <pre style='padding:10px; background:#f0f0f0; font-family:monospace; white-space:pre-wrap; word-wrap:break-word;'>{escaped_code}</pre>
        {iframe_code}
    </body>
    </html>
    """
    with open(HTML_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[DEBUG] HTML file written to {HTML_OUTPUT_FILE}")

def upload_to_s3():
    s3 = boto3.client('s3', region_name=S3_REGION)
    key_name = f"embed_previews/{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.html"

    try:
        s3.upload_file(HTML_OUTPUT_FILE, BUCKET_NAME, key_name, ExtraArgs={'ContentType': 'text/html', 'ACL': 'public-read'})
        url = f"https://{BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{key_name}"
        print(f"✅ File uploaded to: {url}")
        return url
    except NoCredentialsError:
        print("❌ AWS credentials not found. Make sure they're set in ~/.aws/credentials.")
        return None
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None

def open_in_browser(url):
    if not url:
        return

    last_choice = "1"
    last_incognito = "n"

    if os.path.exists(LAST_BROWSER_FILE):
        with open(LAST_BROWSER_FILE, 'r') as f:
            lines = f.read().splitlines()
            if len(lines) >= 1:
                last_choice = lines[0]
            if len(lines) >= 2:
                last_incognito = lines[1]

    print("Select browser:")
    for key, (name, _) in BROWSERS.items():
        print(f"  {key}: {name}")
    choice = input(f"Choice (default {last_choice}): ").strip() or last_choice

    incognito = input(f"Open in incognito/private mode? (y/n, default {last_incognito}): ").strip().lower() or last_incognito

    with open(LAST_BROWSER_FILE, 'w') as f:
        f.write(f"{choice}\n{incognito}")

    browser_paths = BROWSERS.get(choice, BROWSERS["1"])[1]
    args = []

    if choice == "1" and incognito == "y":
        args.append("--incognito")
    elif choice == "2" and incognito == "y":
        args.append("--inprivate")
    elif choice == "3" and incognito == "y":
        args.append("-private-window")

    for path in browser_paths:
        if os.path.exists(path):
            try:
                subprocess.Popen([path] + args + [url])
                return
            except Exception as e:
                print(f"❌ Failed to launch {path}: {e}")

    print("❌ No valid browser executable found. Please install or update your browser paths.")

if __name__ == "__main__":
    iframe = get_iframe_code()
    generate_html(iframe)
    uploaded_url = upload_to_s3()
    open_in_browser(uploaded_url)
