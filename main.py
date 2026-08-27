from playwright.sync_api import sync_playwright
import time
import requests
import os
import argparse
import concurrent.futures

# Folder kahan save hoga
SAVE_FOLDER = "bing_automated_images"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def download_image(url, filename):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        clean_url = url.split("?")[0]
        print(f"📥 Downloading: {clean_url[:50]}...") 
        
        response = requests.get(clean_url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"✅ SAVED: {filename}")
        else:
            print(f"❌ Failed! Status Code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

# ==========================================
# WORKER FUNCTION (Jo har image banayega)
# ==========================================
def run_browser_worker(worker_id, emoji_list):
    print(f"🤖 Worker {worker_id} started! Uske hisse ke Emojis: {emoji_list}")
    
    for emoji_id in emoji_list:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--start-maximized"])
            context = browser.new_context() 
            page = context.new_page()
            
            try:
                page.goto("https://www.bing.com/images/create")
                time.sleep(5) 
                
                # ==========================================
                # THE CRAZY LAUGHING BRAIN (Hasi ka Pagalpan)
                # ==========================================
                expression = ""
                
                if emoji_id <= 20:
                    expression = "chuckling mischievously, pointing a finger directly at the viewer and laughing with a few tears, highly detailed roasting 3D emoji"
                elif emoji_id <= 40:
                    expression = "laughing hysterically, crying a massive waterfall of tears, holding its stomach in extreme comedy, highly exaggerated 3D emoji"
                elif emoji_id <= 60:
                    expression = "rolling on the floor laughing, mouth wide open in a chaotic funny roar, spitting out tears, wild and crazy roasting 3D emoji"
                elif emoji_id <= 80:
                    expression = "going absolutely insane with laughter, mind-blowing extreme crazy face, eyes popping out comically, hyper-exaggerated surreal roasting 3D emoji"
                else: # 81 se 100 tak
                    expression = "ultimate chaotic god-level laughter, breaking reality, melting with extreme uncontrollable comedy, never-seen-before bizarre and insanely funny 3D roasting emoji"

                # PROMPT: Solid Green Background + Extreme Unique Style
                prompt = f"A completely unique, never-seen-before ultra-HD 3D glossy emoji face. ABSOLUTELY NO TEXT, NO LETTERS. {expression}. Isolated on a PURE BRIGHT SOLID GREEN background for chroma key. Masterpiece, hyper-detailed meme style, variation {emoji_id}."
                
                print(f"[Worker {worker_id}] Typing Emoji {emoji_id}...")
                search_box = page.get_by_placeholder("Describe the image you want to create")
                if not search_box.is_visible():
                    search_box = page.locator("textarea[name='q'], #sb_form_q").first
                
                search_box.fill("")
                search_box.fill(prompt)
                
                generate_btn = page.locator("button:has-text('Generate'), button:has-text('Create'), button:has-text('Join'), #create_btn_c").first
                generate_btn.click()
                
                # ==========================================
                # SMART WAIT (Max 70 Seconds wait karega)
                # ==========================================
                print(f"[Worker {worker_id}] Waiting for AI to build Emoji {emoji_id}...")
                
                img_url = None
                for attempt in range(35):
                    time.sleep(2) 
                    all_image_srcs = page.evaluate("() => Array.from(document.querySelectorAll('img')).map(img => img.src)")
                    
                    for src in all_image_srcs:
                        if "OIG" in src:
                            img_url = src
                            break 
                    
                    if img_url:
                        print(f"[Worker {worker_id}] 🎉 Image found in {attempt * 2 + 2} seconds!")
                        break 
                
                # ==========================================
                # DOWNLOAD YA ERROR SCREENSHOT
                # ==========================================
                if img_url:
                    filepath = os.path.join(SAVE_FOLDER, f"Emoji_{emoji_id}.jpg")
                    download_image(img_url, filepath)
                else:
                    print(f"⚠️ [Worker {worker_id}] Image nahi mili Emoji {emoji_id} ke liye. Taking Screenshot...")
                    page.screenshot(path=os.path.join(SAVE_FOLDER, f"ERROR_Emoji_{emoji_id}.png"))
                    with open(os.path.join(SAVE_FOLDER, "failed_emojis.txt"), "a") as f:
                        f.write(f"Emoji {emoji_id} failed\n")
                    
            except Exception as e:
                print(f"⚠️ Error for Emoji {emoji_id}: {e}")
                page.screenshot(path=os.path.join(SAVE_FOLDER, f"CRASH_Emoji_{emoji_id}.png"))
            finally:
                browser.close()
                
        time.sleep(5)

# ==========================================
# MATHS & PARALLEL PROCESSING
# ==========================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--machine_id", type=int, required=True)
    args = parser.parse_args()
    
    machine_id = args.machine_id
    print(f"🖥️ MACHINE {machine_id} STARTED!")
    
    worker_1_id = (machine_id - 1) * 2 + 1
    worker_2_id = (machine_id - 1) * 2 + 2
    
    worker_1_items = list(range((worker_1_id - 1) * 10 + 1, worker_1_id * 10 + 1))
    worker_2_items = list(range((worker_2_id - 1) * 10 + 1, worker_2_id * 10 + 1))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(run_browser_worker, worker_1_id, worker_1_items)
        executor.submit(run_browser_worker, worker_2_id, worker_2_items)
    
    print(f"✅ MACHINE {machine_id} NE APNA KAAM KHATAM KAR LIYA!")
