import requests
from flask import Flask, render_template_string, request, abort

app = Flask(__name__)

# Script configuration
TRANSLATION = "english_hilali_khan"

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

# Base Layout
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Amiri&display=swap" rel="stylesheet">
    <style>
        .font-arabic { font-family: 'Amiri', serif; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen p-4 md:p-12 font-sans text-slate-800">
    <div class="max-w-5xl mx-auto">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

# 1. Main Home / Index Template
INDEX_TEMPLATE = BASE_LAYOUT.replace("{% block content %}{% endblock %}", """
<div class="mb-8 text-center">
    <h1 class="text-4xl font-bold text-slate-900 mb-4">Al-Quran Al-Kareem</h1>
    <div class="max-w-md mx-auto relative">
        <input type="text" id="surahSearch" onkeyup="filterSurahs()" placeholder="Search Surah by name or number..." 
               class="w-full px-4 py-3 rounded-xl border border-slate-200 shadow-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none text-sm transition-all">
    </div>
</div>

<div id="surahGrid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
    {% for name in surah_names %}
    {% set i = loop.index %}
    <a href="/alquran/{{ i }}/" data-name="{{ name | lower }}" data-id="{{ i }}" class="surah-card group flex flex-col justify-center items-center p-5 bg-white border border-slate-200 rounded-xl shadow-xs transition-all duration-200 hover:-translate-y-1 hover:border-emerald-500 hover:shadow-md">
        <span class="text-xs font-semibold text-slate-400 group-hover:text-emerald-600 transition-colors mb-2">
            {{ i }}
        </span>
        <img src="https://alsalafiyyah.github.io/alquran/assets/svg/{{ i }}.svg" alt="{{ name }}" class="h-12 w-auto object-contain group-hover:scale-105 transition-transform duration-200" />
        <span class="text-sm font-medium text-slate-500 mt-2 text-center">
            {{ name }}
        </span>
    </a>
    {% endfor %}
</div>

<script>
function filterSurahs() {
    let input = document.getElementById('surahSearch').value.toLowerCase();
    let cards = document.getElementsByClassName('surah-card');
    
    for (let card of cards) {
        let name = card.getAttribute('data-name');
        let id = card.getAttribute('data-id');
        if (name.includes(input) || id.includes(input)) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    }
}
</script>
""")

# 2. Verses (Chapter, Single, and Range Display) Template
VERSES_TEMPLATE = BASE_LAYOUT.replace("{% block content %}{% endblock %}", """
<nav class="text-sm font-medium text-slate-500 mb-6">
    <a href="/" class="hover:text-emerald-600 transition-colors">Home</a>
    <span class="mx-2 text-slate-300">/</span>
    {% if range_text %}
        <a href="/alquran/{{ sura }}/" class="hover:text-emerald-600 transition-colors">Surah {{ surah_name }}</a>
        <span class="mx-2 text-slate-300">/</span>
        <span class="text-slate-800">{{ range_text }}</span>
    {% else %}
        <span class="text-slate-800">Surah {{ surah_name }}</span>
    {% endif %}
</nav>

<div class="mb-8 flex flex-col items-center justify-center text-center">
    <img src="https://alsalafiyyah.github.io/alquran/assets/svg/{{ sura }}.svg" alt="{{ surah_name }}" class="h-20 w-auto mb-3 object-contain" />
    <h1 class="text-3xl font-bold text-slate-800">{{ surah_name }}</h1>
    <p class="text-sm text-emerald-600 font-medium mt-1">
        {% if range_text %}({{ range_text }}){% else %}({{ total_verses }} Verses){% endif %}
    </p>
</div>

<div class="mb-8 max-w-xs mx-auto">
    <label for="verse-select" class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Jump to Verse</label>
    <select id="verse-select" onchange="window.location.href=this.value" class="block w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-xs outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500">
        <option value="">Select verse...</option>
        {% for total_v in all_verses_list %}
            <option value="/alquran/{{ sura }}/{{ total_v.aya }}">Verse {{ total_v.aya }}</option>
        {% endfor %}
    </select>
</div>

<div class="space-y-6">
    {% for v in verses %}
    <div class="block bg-white border border-slate-200 rounded-2xl p-6 md:p-8 shadow-xs">
        <p class="text-emerald-700 font-bold mb-2"><strong>{{ v.sura }}:{{ v.aya }}</strong></p>
        <p dir="rtl" class="font-arabic text-right text-3xl text-slate-900 leading-widest my-4">{{ v.arabic_text }}</p>
        <p class="text-slate-700 leading-relaxed mt-2">{{ v.translation }}</p>
        {% if v.footnotes %}
            <div class="mt-4 bg-slate-50 border-l-4 border-slate-200 p-3 text-xs text-slate-500 rounded-r-md leading-relaxed"><small>{{ v.footnotes | safe }}</small></div>
        {% endif %}
    </div>
    {% else %}
    <div class="bg-white border border-slate-200 rounded-2xl p-6 text-center text-slate-400">
        No verses found for this range selection.
    </div>
    {% endfor %}
</div>
""")

@app.route('/')
def home():
    return render_template_string(INDEX_TEMPLATE, title="Al-Quran Index", surah_names=SURAH_NAMES)

@app.route('/alquran/<int:sura>/')
@app.route('/alquran/<int:sura>/<string:verse_expr>')
def view_quran(sura, verse_expr=None):
    if sura < 1 or sura > 114:
        abort(404)
        
    surah_name = SURAH_NAMES[sura - 1]
    
    # Live fetch from the translation API endpoint
    url = f"https://quranenc.com/api/v1/translation/sura/{TRANSLATION}/{sura}"
    response = requests.get(url)
    if response.status_code != 200:
        abort(500, description="Error querying API data dependencies.")
        
    data = response.json()
    all_verses = data.get('result', [])
    
    filtered_verses = all_verses
    range_text = None
    
    if verse_expr:
        if '-' in verse_expr:  # Handles Range Urls: /alquran/1/1-3
            try:
                start_str, end_str = verse_expr.split('-')
                start, end = int(start_str), int(end_str)
                filtered_verses = [v for v in all_verses if start <= int(v['aya']) <= end]
                range_text = f"Verses {start} - {end}"
            except ValueError:
                abort(400, description="Invalid range format. Use syntax like '1-3'.")
        else:                  # Handles Single Verse Layouts: /alquran/1/2
            try:
                target_v = int(verse_expr)
                filtered_verses = [v for v in all_verses if int(v['aya']) == target_v]
                range_text = f"Verse {target_v}"
            except ValueError:
                abort(400, description="Invalid verse standard identifier configuration.")

    return render_template_string(
        VERSES_TEMPLATE,
        title=f"Surah {surah_name} {range_text if range_text else ''}",
        sura=sura,
        surah_name=surah_name,
        verses=filtered_verses,
        all_verses_list=all_verses,
        total_verses=len(all_verses),
        range_text=range_text
    )

if __name__ == '__main__':
    # Runs python app server container locally on port 5000
    app.run(debug=True, port=5000)