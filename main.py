from playwright.sync_api import sync_playwright
import time
import requests
import os
import argparse
import concurrent.futures

# Folder ka naam same rakha hai taaki GitHub zip bana sake
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
    
    # 10 Aesthetic / Cute Backgrounds (Tumhari image jaisi vibes)
    backgrounds = [
        "a cozy coffee mug on a wooden table beside a warm brown textured wall",
        "a beautiful aesthetic sunrise through a bedroom window with soft light",
        "a cute desk setup with a tiny cactus and warm pastel pink wall",
        "a rainy glass window with cozy warm bokeh lights in the background",
        "soft glowing fairy lights over a cozy bed with fluffy white pillows",
        "two cups of tea on a table with a beautiful aesthetic sunset background",
        "a minimalistic pastel blue wall with soft sunlight hitting it",
        "a soft aesthetic peach-colored background with scattered rose petals",
        "a cute cafe table with a heart-shaped latte art and a notebook",
        "a warm evening aesthetic setup with a glowing table lamp and textured wall"
    ]

    # Daily Chat / Casual Messaging Parts (10x10 = 100 Unique phrases)
    # Part 1 (Greetings / Openers)
    chat_part_1 = [
        "Good Morning", "Hello ji", "Hey you", "Oye suno", "Aur batao", 
        "Kaise ho?", "Kya haal hai?", "Good Evening", "Kkrh?", "Hi there"
    ]
    
    # Part 2 (Follow-ups / Cute texts)
    chat_part_2 = [
        "have a great day", "chai pi lo", "miss you", "take care", "smile please :)", 
        "sab badhiya?", "khana khaya?", "kya kar rahe ho?", "milte hain", "yaad aayi?"
    ]

    for frame in frames_list:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--start-maximized"])
            context = browser.new_context() 
            page = context.new_page()
            
            try:
                page.goto("https://www.bing.com/images/create")
                time.sleep(5) 
                
                # Math for uniqueness (Background aur Text har photo mein change hoga)
                idx = frame - 1
                bg = backgrounds[idx % len(backgrounds)]
                
                line1 = chat_part_1[idx % 10]
                line2 = chat_part_2[(idx // 10) % 10]

                # ==========================================
                # NEW SHORT AESTHETIC PROMPT
                # ==========================================
                # Prompt ko lamba nahi rakha hai, taaki image blank na aaye.
                prompt = (
                    f"Aesthetic Pinterest photography. {bg}. "
                    f"Direct front view. Cute, casual white handwritten text exactly reading "
                    f"'{line1} {line2}' written beautifully on the wall or empty space. Cozy vibe, photorealistic."
                )
                
                print(f"[Worker {worker_id}] Typing Frame {frame} (Text: {line1} {line2})...")
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
                    filepath = os.path.join(SAVE_FOLDER, f"CuteChat_{frame}.jpg")
                    download_image(img_url, filepath)
                else:
                    print(f"⚠️ [Worker {worker_id}] Image nahi mili Frame {frame} ke liye.")
                    page.screenshot(path=os.path.join(SAVE_FOLDER, f"ERROR_Chat_{frame}.png"))
                    with open(os.path.join(SAVE_FOLDER, "failed_chats.txt"), "a") as f:
                        f.write(f"Frame {frame} failed\n")
                    
            except Exception as e:
                print(f"⚠️ Error for Frame {frame}: {e}")
                page.screenshot(path=os.path.join(SAVE_FOLDER, f"CRASH_Chat_{frame}.png"))
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
