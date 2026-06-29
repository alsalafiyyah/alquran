import os
import requests
import json
import time

# Script configuration
TRANSLATION = "english_hilali_khan"
TOTAL_SURAS = 114  
VERSES_PER_PAGE = 30  

SURAH_NAMES = [
    "Al-Fatihah", "Al-Baqarah", "Aal 'Imran", "An-Nisa'", "Al-Ma'idah", "Al-An'am", "Al-A'raf", "Al-Anfal", "At-Tawbah", "Yunus",
    "Hud", "Yusuf", "Ar-Ra'd", "Ibrahim", "Al-Hijr", "An-Nahl", "Al-Isra'", "Al-Kahf", "Maryam", "Ta-Ha",
    "Al-Anbiya'", "Al-Hajj", "Al-Mu'minun", "An-Nur", "Al-Furqan", "Ash-Shu'ara'", "An-Naml", "Al-Qasas", "Al-Ankabut", "Ar-Rum",
    "Luqman", "As-Sajdah", "Al-Ahzab", "Saba'", "Fatir", "Ya-Sin", "As-Saffat", "Sad", "Az-Zumar", "Ghafir",
    "Fussilat", "Ash-Shura", "Az-Zukhruf", "Ad-Dukhan", "Al-Jathiyah", "Al-Ahqaf", "Muhammad", "Al-Fath", "Al-Hujurat", "Qaf",
    "Adh-Dhariyat", "At-Tur", "An-Najm", "Al-Qamar", "Ar-Rahman", "Al-Waqi'ah", "Al-Hadid", "Al-Mujadilah", "Al-Hashr", "Al-Mumtahanah",
    "As-Saff", "Al-Jumu'ah", "Al-Munafiqun", "At-Taghabun", "At-Talaq", "At-Tahrim", "Al-Mulk", "Al-Qalam", "Al-Haqqah", "Al-Ma'arij",
    "Nuh", "Al-Jinn", "Al-Muzzammil", "Al-Muddaththir", "Al-Qiyamah", "Al-Insan", "Al-Mursalat", "An-Naba'", "An-Nazi'at", "'Abasa",
    "At-Takwir", "Al-Infitar", "Al-Mutaffifin", "Al-Inshiqaq", "Al-Buruj", "At-Tariq", "Al-A'la", "Al-Ghashiyah", "Al-Fajr", "Al-Balad",
    "Ash-Shams", "Al-Layl", "Ad-Duha", "Ash-Sharh", "At-Tin", "Al-'Alaq", "Al-Qadr", "Al-Bayyinah", "Az-Zalzalah", "Al-'Adiyat",
    "Al-Qari'ah", "At-Takathur", "Al-'Asr", "Al-Humazah", "Al-Fil", "Quraysh", "Al-Ma'un", "Al-Kauthar", "Al-Kafirun", "An-Nasr",
    "Al-Masad", "Al-Ikhlas", "Al-Falaq", "An-Nas"
]

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

for sura in range(1, TOTAL_SURAS + 1):
    surah_name = SURAH_NAMES[sura - 1]
    print(f"Fetching Surah {sura}: {surah_name}...")
    
    url = f"https://quranenc.com/api/v1/translation/sura/{TRANSLATION}/{sura}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error fetching Surah {sura}")
        continue
        
    data = response.json()
    verses = data.get('result', [])
    total_verses = len(verses) # Dynamically calculated verse count
    
    base_dir = f"verses/{sura}"
    os.makedirs(base_dir, exist_ok=True)
    
    # --- 1. PAGINATED SURAH PAGES ---
    verse_chunks = list(chunk_list(verses, VERSES_PER_PAGE))
    total_pages = len(verse_chunks)
    
    for page_idx, chunk in enumerate(verse_chunks):
        page_num = page_idx + 1
        
        prev_page_url = None if page_num == 1 else (f"/alquran/{sura}/" if page_num == 2 else f"/{sura}/page{page_num - 1}")
        next_page_url = None if page_num == total_pages else f"/alquran/{sura}/page{page_num + 1}"
        
        # Build Front Matter
        surah_html = "---\nlayout: default\n"
        surah_html += f"title: \"Surah {surah_name} - Page {page_num}\"\n"
        if page_num == 1:
            surah_html += f"permalink: /{sura}/\n"
        else:
            surah_html += f"permalink: /{sura}/page{page_num}\n"
        surah_html += "---\n\n"
        
        # Heading updated to show SVG layout, Name, and Verse count
        surah_html += f'<div class="mb-8 flex flex-col items-center justify-center text-center">\n'
        surah_html += f'  <img src="https://alsalafiyyah.github.io/alquran/assets/svg/{sura}.svg" alt="{surah_name}" class="h-16 w-auto mb-3 object-contain" />\n'
        surah_html += f'  <h1 class="text-3xl font-bold text-slate-800">{surah_name}</h1>\n'
        surah_html += f'  <p class="text-sm text-emerald-600 font-medium mt-1">({total_verses} Verses)</p>\n'
        if total_pages > 1:
            surah_html += f'  <p class="text-xs text-slate-400 mt-1">Page {page_num} of {total_pages}</p>\n'
        surah_html += '</div>\n\n'
        
        for v in chunk:
            surah_html += f'<a href="/alquran/{sura}/{v["aya"]}" class="verse block group hover:border-emerald-500 hover:shadow-md transition-all duration-200 no-underline">\n'
            surah_html += f'  <p class="text-emerald-700 font-bold group-hover:text-emerald-600"><strong>{v["sura"]}:{v["aya"]}</strong></p>\n'
            surah_html += f'  <p dir="rtl" class="font-arabic text-right text-3xl text-slate-900 leading-widest my-4">{v["arabic_text"]}</p>\n'
            surah_html += f'  <p class="text-slate-700 leading-relaxed mt-2">{v["translation"]}</p>\n'
            if v["footnotes"]:
                surah_html += f'  <small style="color:gray;">{v["footnotes"]}</small>\n'
            surah_html += '</a>\n\n'
            
        if total_pages > 1:
            surah_html += '<div class="flex justify-between items-center my-12 pt-6 border-t border-slate-200">\n'
            if prev_page_url:
                surah_html += f'  <a href="{prev_page_url}" class="px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors">&larr; Previous Page</a>\n'
            else:
                surah_html += '  <span class="text-slate-300 text-sm font-medium px-4 py-2">&larr; Previous Page</span>\n'
                
            surah_html += f'  <span class="text-sm text-slate-500">Page {page_num} / {total_pages}</span>\n'
            
            if next_page_url:
                surah_html += f'  <a href="{next_page_url}" class="px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors">Next Page &rarr;</a>\n'
            else:
                surah_html += '  <span class="text-slate-300 text-sm font-medium px-4 py-2">Next Page &rarr;</span>\n'
            surah_html += '</div>\n'
            
        filename = f"{base_dir}/index.html" if page_num == 1 else f"{base_dir}/page{page_num}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(surah_html)
            
    # --- 2. INDIVIDUAL VERSE PAGES ---
    for v in verses:
        aya = v["aya"]
        verse_html = f"---\nlayout: default\ntitle: \"Surah {surah_name}, Verse {aya}\"\npermalink: /{sura}/{aya}\n---\n\n"
        verse_html += f'<div class="single-verse">\n  <p class="text-emerald-700 font-bold mb-4"><strong>{surah_name} ({sura}:{aya})</strong></p>\n'
        verse_html += f'  <p dir="rtl" style="text-align:right; font-size:32px;" class="font-arabic text-slate-900 leading-widest mb-6">{v["arabic_text"]}</p>\n'
        verse_html += f'  <p style="font-size:18px;" class="text-slate-800 leading-relaxed">{v["translation"]}</p>\n'
        if v["footnotes"]:
            verse_html += f'  <div class="mt-6 bg-slate-50 border-l-4 border-slate-300 p-4 text-xs text-slate-500 rounded-r-md leading-relaxed"><small>{v["footnotes"]}</small></div>\n'
        verse_html += '</div>\n'
        
        with open(f"{base_dir}/{aya}.html", "w", encoding="utf-8") as f:
            f.write(verse_html)
            
    time.sleep(1)

print("Static structure generated inside /verses/ with clean public URLs!")