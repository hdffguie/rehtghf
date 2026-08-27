from playwright.sync_api import sync_playwright
import time
import requests
import os
import argparse
import concurrent.futures

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

# Yeh function 1 browser ka kaam sambhalega
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
                time.sleep(5)
                
                prompt = f"A highly realistic FULL-BODY wide shot photograph of EXACTLY ONE single Indian male standing alone inside a hardcore bodybuilding gym. DO NOT show multiple people. NO BEFORE/AFTER COLLAGE. ABSOLUTELY NO TEXT, NO LETTERS, NO NUMBERS, AND NO WATERMARKS ON THE IMAGE. He is standing straight facing the camera, wearing only black gym shorts (no shirt), showing full arms, chest, and legs clearly. Gym Muscle Transformation Journey: Day {age}."
                
                print(f"[Worker {worker_id}] Typing Age {age}...")
                search_box = page.get_by_placeholder("Describe the image you want to create")
                if not search_box.is_visible():
                    search_box = page.locator("textarea[name='q'], #sb_form_q").first
                
                search_box.fill("")
                search_box.fill(prompt)
                
                generate_btn = page.locator("button:has-text('Generate'), button:has-text('Create'), button:has-text('Join'), #create_btn_c").first
                generate_btn.click()
                
                print(f"[Worker {worker_id}] Waiting 30 sec for Age {age}...")
                time.sleep(30) 
                
                all_image_srcs = page.evaluate("() => Array.from(document.querySelectorAll('img')).map(img => img.src)")
                
                img_url = None
                for src in all_image_srcs:
                    if "OIG" in src:
                        img_url = src
                        break 
                
                if img_url:
                    filepath = os.path.join(SAVE_FOLDER, f"Age_{age}.jpg")
                    download_image(img_url, filepath)
                else:
                    print(f"⚠️ [Worker {worker_id}] Image nahi mili Age {age} ke liye.")
                    
            except Exception as e:
                print(f"⚠️ Error for Age {age}: {e}")
            finally:
                browser.close()
                
        time.sleep(5)

if __name__ == "__main__":
    # GitHub action se Machine ID mangna
    parser = argparse.ArgumentParser()
    parser.add_argument("--machine_id", type=int, required=True)
    args = parser.parse_args()
    
    machine_id = args.machine_id
    print(f"🖥️ MACHINE {machine_id} STARTED!")
    
    # MATHS: Kaam ka bantwara
    # Har machine ke andar 2 worker honge.
    worker_1_id = (machine_id - 1) * 2 + 1
    worker_2_id = (machine_id - 1) * 2 + 2
    
    # Har worker ko 10 ages milengi
    worker_1_ages = list(range((worker_1_id - 1) * 10 + 1, worker_1_id * 10 + 1))
    worker_2_ages = list(range((worker_2_id - 1) * 10 + 1, worker_2_id * 10 + 1))
    
    # 2 Chrome browsers ko ek sath (Parallel) chalana
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(run_browser_worker, worker_1_id, worker_1_ages)
        executor.submit(run_browser_worker, worker_2_id, worker_2_ages)
    
    print(f"✅ MACHINE {machine_id} NE APNA KAAM KHATAM KAR LIYA!")
