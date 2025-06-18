import requests
from datetime import date
from pathlib import Path
import subprocess

def download_and_commit():
    today = date.today()
    yyyymmdd = today.strftime('%Y%m%d')
    url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{yyyymmdd}_F_0000.csv.zip"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com/"
    }

    dest_dir = Path("/Users/kavishambani/ka/market/nsemirror/public/bhavcopy")
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / f"{yyyymmdd}.zip"

    print(f"Downloading {url}...")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(zip_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Saved: {zip_path}")

        # Git commit and push
        repo_dir = dest_dir.parent.parent
        subprocess.run(["git", "add", "."], cwd=repo_dir)
        subprocess.run(["git", "commit", "-m", f"Add BhavCopy for {yyyymmdd}"], cwd=repo_dir)
        subprocess.run(["git", "push"], cwd=repo_dir)
        print("✅ Git pushed to Vercel!")
    else:
        print(f"❌ Failed to download BhavCopy: {response.status_code}")

if __name__ == "__main__":
    download_and_commit()
