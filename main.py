from playwright.sync_api import sync_playwright
import time
import requests
import os
import argparse
import concurrent.futures

# GitHub Actions ki YAML file yahi folder dhund rahi hai, isliye naam wapas change kiya
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
# WORKER FUNCTION
# ==========================================
def run_browser_worker(worker_id, frames_list):
    print(f"🤖 Worker {worker_id} started! Frames: {frames_list}")
    
    exercises = [
        "deadlifting", "doing bench press", "doing heavy squats", 
        "doing pull-ups", "curling dumbbells", "using cable machines", 
        "pushing a sled", "doing shoulder press", "doing T-bar rows", "doing dips"
    ]
    
    environments = [
        "dark underground gym", "neon cyberpunk gym", "rusty iron gym", 
        "industrial crossfit box", "spotlight lit gym", "high-tech gym", 
        "rooftop gym at night", "basement gym", "red-lit gym", "outdoor muscle beach"
    ]
    
    masks = [
        "a black workout breathing mask", "a futuristic sports mask", 
        "an elevation mask", "a dark cloth wrap covering his mouth", "a cool gym half-mask"
    ]
    
    body_types = [
        "massive bodybuilder", "shredded lifter", 
        "huge powerlifter", "aesthetic fitness model"
    ]

    quote_line_1 = [
        "NO EXCUSES", "PUSH HARDER", "EMBRACE PAIN", "SWEAT TODAY", "GRIND NOW", 
        "LIFT HEAVY", "STAY FOCUSED", "BEAST MODE", "NEVER QUIT", "RISE & GRIND"
    ]
    
    quote_line_2 = [
        "SHINE TOMORROW", "CONQUER ALL", "BE UNSTOPPABLE", "PROVE THEM WRONG", "GROW STRONGER", 
        "OWN SUCCESS", "DEFEAT DEMONS", "EARN RESPECT", "BUILD LEGACY", "TRUST PROCESS"
    ]

    for frame in frames_list:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--start-maximized"])
            context = browser.new_context() 
            page = context.new_page()
            
            try:
                page.goto("https://www.bing.com/images/create")
                time.sleep(5) 
                
                # Math for uniqueness
                idx = frame - 1
                ex = exercises[idx % len(exercises)]
                env = environments[(idx + 2) % len(environments)]
                mask = masks[(idx + 1) % len(masks)]
                body = body_types[(idx + 3) % len(body_types)]
                
                line1 = quote_line_1[idx % 10]
                line2 = quote_line_2[(idx // 10) % 10]

                # PROMPT SHORTENED (Under 250 characters to avoid blank/failed images)
                prompt = (
                    f"A {body} {ex} in a {env}. He is wearing {mask}, face hidden. "
                    f"Bold typography text on the image reading: '{line1}' and below it '{line2}'. "
                    f"Cinematic gym lighting, photorealistic."
                )
                
                print(f"[Worker {worker_id}] Typing Frame {frame} (Len: {len(prompt)} chars)...")
                search_box = page.get_by_placeholder("Describe the image you want to create")
                if not search_box.is_visible():
                    search_box = page.locator("textarea[name='q'], #sb_form_q").first
                
                search_box.fill("")
                search_box.fill(prompt)
                
                generate_btn = page.locator("button:has-text('Generate'), button:has-text('Create'), button:has-text('Join'), #create_btn_c").first
                generate_btn.click()
                
                print(f"[Worker {worker_id}] Waiting max 70s for Frame {frame}...")
                
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
                
                if img_url:
                    filepath = os.path.join(SAVE_FOLDER, f"GymMotivation_{frame}.jpg")
                    download_image(img_url, filepath)
                else:
                    print(f"⚠️ [Worker {worker_id}] Image nahi mili Frame {frame} ke liye.")
                    page.screenshot(path=os.path.join(SAVE_FOLDER, f"ERROR_Gym_{frame}.png"))
                    with open(os.path.join(SAVE_FOLDER, "failed_gym.txt"), "a") as f:
                        f.write(f"Frame {frame} failed\n")
                    
            except Exception as e:
                print(f"⚠️ Error for Frame {frame}: {e}")
                page.screenshot(path=os.path.join(SAVE_FOLDER, f"CRASH_Gym_{frame}.png"))
            finally:
                browser.close()
                
        time.sleep(5)

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
