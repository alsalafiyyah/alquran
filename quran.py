import os
import requests
import json
import time

# Script configuration
TRANSLATION = "english_hilali_khan"
TOTAL_SURAS = 114  
VERSES_PER_PAGE = 30  

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

for sura in range(1, TOTAL_SURAS + 1):
    print(f"Fetching Surah {sura}...")
    
    url = f"https://quranenc.com/api/v1/translation/sura/{TRANSLATION}/{sura}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error fetching Surah {sura}")
        continue
        
    data = response.json()
    verses = data.get('result', [])
    
    # Files are created inside "verses"
    base_dir = f"verses/{sura}"
    os.makedirs(base_dir, exist_ok=True)
    
    # --- 1. PAGINATED SURAH PAGES ---
    verse_chunks = list(chunk_list(verses, VERSES_PER_PAGE))
    total_pages = len(verse_chunks)
    
    for page_idx, chunk in enumerate(verse_chunks):
        page_num = page_idx + 1
        
        # FIXED: Both previous and next URLs now consistently include /alquran/
        prev_page_url = None if page_num == 1 else (f"/alquran/{sura}/" if page_num == 2 else f"/alquran/{sura}/page{page_num - 1}")
        next_page_url = None if page_num == total_pages else f"/alquran/{sura}/page{page_num + 1}"
        
        # Build Front Matter
        surah_html = "---\nlayout: default\n"
        surah_html += f"title: \"Surah {sura} - Page {page_num}\"\n"
        if page_num == 1:
            surah_html += f"permalink: /alquran/{sura}/\n"  
        else:
            surah_html += f"permalink: /alquran/{sura}/page{page_num}\n"  
        surah_html += "---\n\n"
        
        surah_html += f'<div class="mb-8 text-center">\n  <h1 class="text-3xl font-bold">Surah {sura}</h1>\n'
        if total_pages > 1:
            surah_html += f'  <p class="text-sm text-slate-500 mt-1">Page {page_num} of {total_pages}</p>\n'
        surah_html += '</div>\n\n'
        
        for v in chunk:
            clean_footnote = v["footnotes"].replace('"', '\\"').replace('\n', '\\n') if v["footnotes"] else ""
            
            # FIXED: Internal single verse link updated to /alquran/{sura}/{aya}
            surah_html += f'<div class="relative bg-white border border-slate-200/70 p-6 sm:p-8 rounded-2xl shadow-xs hover:border-emerald-500 hover:shadow-md hover:-translate-y-0.5 transition-all duration-300 group flex flex-col">\n'
            surah_html += f'  <div class="flex justify-between items-center mb-6">\n'
            surah_html += f'    <span class="text-xs font-bold uppercase tracking-widest text-slate-400 bg-slate-50 px-2.5 py-1 border border-slate-200/60 rounded-md">Verse {v["sura"]}:{v["aya"]}</span>\n'
            surah_html += f'    <a href="/alquran/{sura}/{v["aya"]}" class="text-xs font-semibold text-emerald-600 hover:text-emerald-700 hover:underline flex items-center gap-1">Focus Verse &rarr;</a>\n'
            surah_html += f'  </div>\n'
            surah_html += f'  <p dir="rtl" class="font-arabic text-right text-3xl sm:text-4xl text-slate-950 leading-[2] tracking-wide my-4 select-all">{v["arabic_text"]}</p>\n'
            surah_html += f'  <p class="text-slate-700 text-base sm:text-[17px] leading-relaxed mt-4 font-normal">{v["translation"]}</p>\n'
            
            if clean_footnote:
                surah_html += f'  <div class="mt-6 pt-4 border-t border-slate-100 flex items-center">\n'
                surah_html += f'    <button onclick="openFootnote(\'Surah {v["sura"]}:{v["aya"]} Commentary\', `{clean_footnote}`)" class="cursor-pointer inline-flex items-center gap-2 text-xs font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100/80 px-3.5 py-2 rounded-xl border border-emerald-200/40 transition-colors">\n'
                surah_html += f'      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>\n'
                surah_html += f'      View Footnotes\n'
                surah_html += f'    </button>\n'
                surah_html += f'  </div>\n'
            surah_html += '</div>\n\n'
            
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
        # FIXED: Base permalink updated to match layout with /alquran/ prefix
        verse_html = f"---\nlayout: default\ntitle: \"Surah {sura}, Verse {aya}\"\npermalink: /alquran/{sura}/{aya}\n---\n\n"
        verse_html += f'<div class="single-verse">\n  <p class="text-emerald-700 font-bold mb-4"><strong>{sura}:{aya}</strong></p>\n'
        verse_html += f'  <p dir="rtl" style="text-align:right; font-size:32px;" class="font-arabic text-slate-900 leading-widest mb-6">{v["arabic_text"]}</p>\n'
        verse_html += f'  <p style="font-size:18px;" class="text-slate-800 leading-relaxed">{v["translation"]}</p>\n'
        if v["footnotes"]:
            verse_html += f'  <div class="mt-6 bg-slate-50 border-l-4 border-slate-300 p-4 text-xs text-slate-500 rounded-r-md leading-relaxed"><small>{v["footnotes"]}</small></div>\n'
        verse_html += '</div>\n'
        
        with open(f"{base_dir}/{aya}.html", "w", encoding="utf-8") as f:
            f.write(verse_html)
            
    time.sleep(1)

print("Static structure generated with unified /alquran/ routing parameters!")