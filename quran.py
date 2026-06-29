import os
import requests
import json
import time

# Script configuration
TRANSLATION = "english_hilali_khan"
TOTAL_SURAS = 114  # Or test with 1 or 2 first

for sura in range(1, TOTAL_SURAS + 1):
    print(f"Fetching Surah {sura}...")
    
    # Hit the chapter endpoint
    url = f"https://quranenc.com/api/v1/translation/sura/{TRANSLATION}/{sura}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error fetching Surah {sura}")
        continue
        
    data = response.json()
    verses = data.get('result', [])
    
    # Create the directory structure (e.g., /1/)
    os.makedirs(f"{sura}", exist_ok=True)
    
    # 1. Build the main Surah Page index template
    surah_html = f"---\nlayout: default\ntitle: \"Surah {sura}\"\npermalink: /{sura}/\n---\n\n<h1>Surah {sura}</h1>\n"
    for v in verses:
        surah_html += f'<div class="verse">\n  <p><strong>{v["sura"]}:{v["aya"]}</strong></p>\n'
        surah_html += f'  <p dir="rtl" style="text-align:right; font-size:24px;">{v["arabic_text"]}</p>\n'
        surah_html += f'  <p>{v["translation"]}</p>\n'
        if v["footnotes"]:
            surah_html += f'  <small style="color:gray;">{v["footnotes"]}</small>\n'
        surah_html += '</div>\n<hr>\n\n'
        
    with open(f"{sura}/index.html", "w", encoding="utf-8") as f:
        f.write(surah_html)
        
    # 2. Build individual Verse files (e.g., /1/1.html, /1/2.html)
    for v in verses:
        aya = v["aya"]
        verse_html = f"---\nlayout: default\ntitle: \"Surah {sura}, Verse {aya}\"\npermalink: /{sura}/{aya}\n---\n\n"
        verse_html += f'<div class="single-verse">\n  <p><strong>{sura}:{aya}</strong></p>\n'
        verse_html += f'  <p dir="rtl" style="text-align:right; font-size:32px;">{v["arabic_text"]}</p>\n'
        verse_html += f'  <p style="font-size:18px;">{v["translation"]}</p>\n'
        if v["footnotes"]:
            verse_html += f'  <div style="margin-top:20px; border-left:3px solid #ccc; padding-left:10px; color:#555;"><small>{v["footnotes"]}</small></div>\n'
        verse_html += '</div>\n'
        
        with open(f"{sura}/{aya}.html", "w", encoding="utf-8") as f:
            f.write(verse_html)
            
    # Respect the API server and avoid getting rate limited
    time.sleep(1)

print("Static structure completely generated!")