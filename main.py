from playwright.sync_api import sync_playwright
import time
import requests
import os
import argparse
import concurrent.futures

# GitHub Actions ke liye same folder
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
# 100 CHAT LINES PROVIDED BY YOU
# ==========================================
CHAT_LINES = [
    "Chai pi lo", "Aur kya ho rha hai?", "Ghoomne chalein?", "Tu mera bhai hai", 
    "Oye kya kar rha hai?", "Hello bhai kaha hai?", "Khana khaya tune?", "Free hokar call kar", 
    "Aaj ka kya plan hai?", "Yaar bahut bore ho rha hu", "Chal chai peene chalte hain", 
    "Ghar pahunch kar message karna", "Aur bhai kya scene hai?", "Tu to bhool hi gaya bhai", 
    "Chal jhoothe sab pata hai", "Bhai tu rehne de tujhse na ho payega", "Itna bhaav kyu kha rha hai?", 
    "Party kab de rha hai phir?", "Bada aadmi ban gaya tu to", "Chal jyada gyaan mat baant", 
    "Bahut tez ho rhe ho hain!", "Tu to mera jigri hai yaar", "Phone utha le bhai urgent hai", 
    "Kaha gayab hai aaj kal?", "Nautanki band kar ab apni", "Chup kar bhai kitna bolta hai", 
    "Chal nikal jyada mat bol", "Ek mast khabar sunau?", "Are yaar ek gadbad ho gayi", 
    "Tune wo reels dekhi kya?", "Aaj to maza hi aa gaya", "Mujhe pehle kyu nahi bataya?", 
    "Chalo kuch order karte hain", "Aaj mera mood kharab hai", "Sach me aisa hua kya?", 
    "Tu hamesha late kyu hota hai?", "Raaste me hu bas 5 minute", "Jhooth mat bol tu ghar pe hai", 
    "Tera bhai hamesha tere sath hai", "Tension mat le sab theek hoga", "Chal jo hoga dekha jayega", 
    "Haan bhai bol", "Na yaar man nahi hai", "Okay done hai", "Abhi busy hu baad me baat karte hain", 
    "Are haan yaad aaya!", "Bilkul sahi bola tune", "Are yaar shit!", "Lol kya bakwaas hai", 
    "Hahaha bhai maaro mujhe", "Kasam se?", "Nice yaar!", "Bye take care", "Good morning bhai", 
    "Good night so ja ab", "Message dekh mera", "Kaha reh gaya tu?", "Jaldi aa yaar", "Koi baat nahi", 
    "Dekhte hain chalo", "Shaam ko kitne baje milega?", "Location bhej apni", "Network nahi aa rha yaar", 
    "Mera phone discharge hone wala hai", "Insta check kar kuch bheja hai", "Bhai ek help chahiye thi", 
    "Paise kab waapas karega bhai?", "Aaj raat ko game khelein?", "Koi acchi movie bata yaar", 
    "Mera to dimag kharab ho gaya", "Chal baad me call karta hu", "Kal sunday hai kuch karte hain", 
    "Khana kha ke milte hain", "Are tune suna kya?", "Tu bahut badal gaya hai", "Gussa mat ho yaar ab", 
    "Chalo chai pe charcha karte hain", "Tune jo bola wahi sahi", "Bhai tu sach me great hai", 
    "Chal ab so ja subah baat karte hain", "Yaad aa rahi hai teri", "Khana khaya mere babu ne?", 
    "Online aa jao na", "Sirf tumhari yaadein aur main", "Aaj bahut pyaare lag rhe high", 
    "Dil nahi lag rha tere bina", "Ek pyaari si photo bhejo na", "Sapne me bhi tum hi aate ho", 
    "Love you so much yaar", "Tumhari aawaz sunni hai", "Itna miss mat kiya karo mujhe", 
    "Naaraaz ho kya mujhse?", "Chalo kahi long drive pe chalein?", "Tum sirf meri ho samjhe?", 
    "Aaj milne ka man hai", "Tumhare bina sab soona hai", "Good night mere sweetu", 
    "Jaldi se reply karo na", "Shakal dekhi hai sheeshe me?", "Khatam tata bye-bye"
]

# Smart Background Function
def get_smart_background(text):
    text_lower = text.lower()
    if any(word in text_lower for word in ["chai", "coffee"]):
        return "a cozy cafe table with a warm cup of tea and aesthetic warm lighting"
    elif any(word in text_lower for word in ["night", "so ja", "sweetu", "sapne"]):
        return "soft glowing fairy lights over a cozy bed in a dark aesthetic room"
    elif any(word in text_lower for word in ["morning", "uth"]):
        return "a beautiful golden sunrise shining through a cozy bedroom window"
    elif any(word in text_lower for word in ["drive", "raaste", "location"]):
        return "a cinematic view from inside a car driving on a beautiful sunset road"
    elif any(word in text_lower for word in ["khana", "order"]):
        return "a cute dining table setup with soft warm aesthetic lighting"
    elif any(word in text_lower for word in ["reels", "movie", "game", "insta", "phone", "network"]):
        return "a cozy desk setup with a glowing phone screen and warm ambient light"
    elif any(word in text_lower for word in ["love", "babu", "yaadein", "miss", "dil", "pyaare"]):
        return "a soft aesthetic peach-colored background with scattered rose petals and soft bokeh"
    elif any(word in text_lower for word in ["gussa", "mood kharab", "shit", "bore", "gadbad"]):
        return "a rainy glass window with cozy warm street bokeh lights in the background"
    elif any(word in text_lower for word in ["bhai", "yaar", "party", "plan"]):
        return "a minimalistic dark aesthetic wall with a tiny indoor plant and soft spotlight"
    else:
        return "a minimalistic pastel colored aesthetic wall with warm sunlight shadows hitting it"

# Reel-Safe Smart Text Splitter Function
def format_text_for_reels(text):
    words = text.split()
    if len(words) > 3:
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        return f"'{line1}' on the first line and '{line2}' right below it"
    else:
        return f"'{text}'"

# ==========================================
# WORKER FUNCTION
# ==========================================
def run_browser_worker(worker_id, frames_list):
    print(f"🤖 Worker {worker_id} started! Frames: {frames_list}")
    
    for frame in frames_list:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--start-maximized"])
            context = browser.new_context() 
            page = context.new_page()
            
            try:
                page.goto("https://www.bing.com/images/create")
                time.sleep(5) 
                
                idx = frame - 1
                current_text = CHAT_LINES[idx]
                smart_bg = get_smart_background(current_text)
                
                # Format text for Reels (Multi-line if long)
                reel_safe_text = format_text_for_reels(current_text)

                # REEL SAFE PROMPT
                prompt = (
                    f"Aesthetic Pinterest photography. {smart_bg}. "
                    f"In the EXACT DEAD CENTER, cute casual white handwritten typography exactly reading {reel_safe_text}. "
                    f"Leave very wide empty negative space on the left and right edges so it can be cropped vertically. "
                    f"Cozy vibe, photorealistic, 8k."
                )
                
                print(f"[Worker {worker_id}] Typing Frame {frame} | Text: '{current_text}'")
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
