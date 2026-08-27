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
def run_browser_worker(worker_id, ages_list):
    print(f"🤖 Worker {worker_id} started! Uske hisse ki Ages: {ages_list}")
    
    for age in ages_list:
        with sync_playwright() as p:
            # GITHUB PAR HEADLESS TRUE HONA CHAHIYE
            browser = p.chromium.launch(headless=True, args=["--start-maximized"])
            context = browser.new_context() 
            page = context.new_page()
            
            try:
                page.goto("https://www.bing.com/images/create")
                time.sleep(5) # Page load hone ka chota wait
                
                # ==========================================
                # THE WEALTH BRAIN (Kapde aur Background)
                # ==========================================
                appearance = ""
                
                if age <= 20:
                    appearance = "extremely poor, wearing dirty torn oversized clothes, standing in a dark dusty street alley with trash"
                elif age <= 40:
                    appearance = "middle-class, wearing clean casual shirt and pants, standing inside a simple modern office workspace"
                elif age <= 60:
                    appearance = "a rich millionaire in a sharp tailored suit with a tie, standing inside a luxury glass high-rise penthouse"
                elif age <= 80:
                    appearance = "an ultra-wealthy billionaire in a designer tuxedo, standing on a private runway near a sleek private jet"
                else: 
                    appearance = "a cosmic trillionaire god-king in glowing gold diamond armor, standing in a futuristic neon sci-fi cyber city"

                prompt = f"8k hyper-realistic FULL-BODY wide shot of EXACTLY ONE Indian male. NO TEXT, NO LETTERS, NO WATERMARKS, NO COLLAGE. Facing camera straight. Cinematic lighting, ultra-detailed. He is {appearance}. Evolution of wealth, Stage {age}."
                
                print(f"[Worker {worker_id}] Typing Age {age}...")
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
                print(f"[Worker {worker_id}] Waiting for AI to build Age {age}... (Smart Wait Max 70s)")
                
                img_url = None
                # 35 loop x 2 seconds = 70 seconds
                for attempt in range(35):
                    time.sleep(2) # Har 2 second me check karega
                    
                    # Page par saari images check karo
                    all_image_srcs = page.evaluate("() => Array.from(document.querySelectorAll('img')).map(img => img.src)")
                    
                    # AI wali image (Jisme 'OIG' hota hai) dhundho
                    for src in all_image_srcs:
                        if "OIG" in src:
                            img_url = src
                            break 
                    
                    # Agar image mil gayi toh loop tod do
                    if img_url:
                        print(f"[Worker {worker_id}] 🎉 Image found in {attempt * 2 + 2} seconds!")
                        break 
                
                # ==========================================
                # DOWNLOAD YA ERROR SCREENSHOT
                # ==========================================
                if img_url:
                    filepath = os.path.join(SAVE_FOLDER, f"Age_{age}.jpg")
                    download_image(img_url, filepath)
                else:
                    print(f"⚠️ [Worker {worker_id}] Image nahi mili Age {age} ke liye. Taking Screenshot...")
                    # Agar 70 second baad bhi nahi aayi, toh screenshot le lo taaki baad me check kar sakein
                    page.screenshot(path=os.path.join(SAVE_FOLDER, f"ERROR_Age_{age}.png"))
                    with open(os.path.join(SAVE_FOLDER, "failed_ages.txt"), "a") as f:
                        f.write(f"Age {age} failed (Timeout ya Block)\n")
                    
            except Exception as e:
                print(f"⚠️ Error for Age {age}: {e}")
                page.screenshot(path=os.path.join(SAVE_FOLDER, f"CRASH_Age_{age}.png"))
                with open(os.path.join(SAVE_FOLDER, "failed_ages.txt"), "a") as f:
                    f.write(f"Age {age} failed (Crash)\n")
            finally:
                # Har image ke baad browser naya khulega
                browser.close()
                
        # Nayi image banne se pehle 5 second ka rest
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
    
    worker_1_ages = list(range((worker_1_id - 1) * 10 + 1, worker_1_id * 10 + 1))
    worker_2_ages = list(range((worker_2_id - 1) * 10 + 1, worker_2_id * 10 + 1))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(run_browser_worker, worker_1_id, worker_1_ages)
        executor.submit(run_browser_worker, worker_2_id, worker_2_ages)
    
    print(f"✅ MACHINE {machine_id} NE APNA KAAM KHATAM KAR LIYA!")
