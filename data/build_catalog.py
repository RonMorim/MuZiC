"""Builds data/songs.js (the catalog) from verified sources.

Run:  python3 data/build_catalog.py

Data policy: fill a field only when a source gives it. Missing values stay null.
- BEATPORT rows were copied from Beatport (DJ Phellix artist page, 2026-11-18): BPM, key, genre and label are Beatport's own.
- OTHER rows come from web sources; their BPM and key are not known yet.
- PENDING rows are songs the user named that are not identified yet.
"""
import json, os, re

# id | title | mix | artists | remixers | bpm | key | genre | label | release_date
BEATPORT = """
31270856|Setareha|Original Mix|DJ Phellix, ENKINAKI, Ario Vibes, Mobin Mirzaei, Golshan (TR)||105|B Major|Downtempo|Ario Vibes|2026-11-27
30431209|Ashi Mashi|Original Mix|DJ Phellix, Arash Raouf, Shiraz House, Negar||122|A Major|Organic House|Shiraz House Records|2026-10-02
30931704|Ashi Mashi|Ismail M Remix|DJ Phellix, Arash Raouf, Shiraz House, Negar|ISMAIL.M|122|A Major|Progressive House|Shiraz House Records|2026-10-23
30947469|Delo Din|Original Mix|Buddha Bar, DJ Phellix, Sheenubb||120|A Major|House|George V|2026-10-16
29953716|Persian Heritage|Original Mix|DJ Phellix, ENKINAKI, Mahdis Soltani, Reza Khosravi||122|C Major|House|George V|2026-08-21
30408565|Setareh|Original Mix|Ravin, Buddha Bar, DJ Phellix, Negar||122|F Major|House|George V|2026-09-18
30947474|Bo Toray|Original Mix|Buddha Bar, Idin Gorji, DJ Phellix, RedRozWine||123|B Major|House|George V|2026-10-16
30947475|Mehr|Original Mix|Buddha Bar, DJ Phellix, Khashayar Salehi||120|D Major|House|George V|2026-10-16
28661467|Sama|Original Mix|Buddha Bar, DJ Phellix, ZERO CONTACT, EyeNaz||122|E Major|House|George V|2026-07-03
22900944|Aman|Original Mix|Buddha Bar, Idin Gorji, DJ Phellix, Khashayar Salehi||121|Ab Minor|House|George V|2025-11-21
20055903|ZAL|Original Mix|Buddha Bar, DJ Phellix, Ablozé||122|A Major|House|George V|2025-02-28
29606946|Saghia|Original Mix|DJ Phellix, EyeNaz, Ario Vibes, DR ZAVIN||122|Eb Major|Organic House|Ario Vibes|2026-08-28
30166451|Rooz O Shab|Original Mix|DJ Phellix, EyeNaz, DR ZAVIN||122|Bb Minor|Electronica|Chakra Records|2026-07-31
29242132|Divane|Original Mix|DJ Phellix, Ablozé, Khashayar Salehi||122|A Major|Organic House|Sol Selectas|2026-07-10
28688757|Shirin|DJ Phellix Remix|DJ Bey, Ario Vibes|DJ Phellix|122|B Major|Organic House|Ario Vibes|2026-05-22
24534227|Jombeisa|Original Mix|DJ Phellix, Seventh Soul, Ario Vibes, Mohammad Laryan||123|A Major|Organic House|Ario Vibes|2026-03-21
26877265|Irane Man|DJ Phellix & Idin Gorji Remix|Idin Gorji, DJ Phellix|DJ Phellix, Idin Gorji|120|E Minor|Deep House|Groover Obsessions|2026-03-09
24295009|Moama|DJ Phellix Remix|Moein|DJ Phellix|124|Eb Major|Afro House|Groover Obsessions|2026-02-25
23238557|Gena Del|Original Mix|DJ Phellix, OF REZZ, Mehdi Monfared||123|E Major|Organic House|Sol Selectas|2026-01-30
23458602|Naghme|Original Mix|Idin Gorji, DJ Phellix, EyeNaz||124|A Major|Organic House|Go Deeva Records|2026-01-30
22908448|Atish|DJ Phellix Extended Remix|Jean Vayat, Mohsen Neshom|DJ Phellix|122|F Minor|Organic House|The Book of Genesis|2025-12-25
20791439|Vatan|Extended Mix|DJ Phellix, Ario Vibes, Mahdis Soltani||122|F Major|Organic House|Ario Vibes|2025-08-15
22073079|Vatan|No Hopes Remix|DJ Phellix, Ario Vibes, Mahdis Soltani|No Hopes|122|F Major|Indie Dance|Ario Vibes|2025-12-19
23918701|Afsane|Extended Mix|DJ Phellix, Sheenubb, Ben & Vincent||122|Db Major|Organic House|Sounds Of Sirin|2025-12-19
19176721|Shah E Man|Original Mix|DJ Phellix, OF REZZ, Sant (IR), Ario Vibes, Mardan||122|G Major|Organic House|Ario Vibes|2024-07-05
22073097|Shah E Man|EANP Remix|DJ Phellix, OF REZZ, Sant (IR), Ario Vibes|EANP|122|G Major|Progressive House|Ario Vibes|2025-11-28
22032088|Golnesa|Extended Mix|Idin Gorji, DJ Phellix, EyeNaz, Ario Vibes||120|Gb Minor|Afro House|Ario Vibes|2025-11-07
21459952|Dokhtare Koli|Extended Mix|SIAAH, DJ Phellix, Ario Vibes||120|C Major|Indie Dance|Ario Vibes|2025-10-10
21589474|The Call (feat. ILIYAM)|Extended Mix|Nikita, DJ Phellix, Shiraz House||122|D Major|Organic House|Shiraz House Records|2025-09-26
20563151|Faryad|Original Mix|DJ Phellix, Sheenubb||122|D Major|Organic House|Sol Selectas|2025-06-20
20235881|Mastan|Original Mix|Idin Gorji, DJ Phellix, Khashayar Salehi, Ario Vibes||121|B Minor|Organic House|Ario Vibes|2025-04-18
20224248|Pari Kojaei (feat. Ali Kashani)|Original Mix|DJ Phellix, Seventh Soul, Ario Vibes||120|F Minor|Organic House|Ario Vibes|2025-04-04
20217811|Dideye Tora (feat. Shezriri)|Original Mix|DJ Phellix, Seventh Soul, Ario Vibes||123|B Minor|Organic House|Ario Vibes|2025-03-28
20283394|Parvane (feat. Amir Sheykh)|Original Mix|DJ Phellix, A X L||120|C Minor|Organic House|Cosmic Awakenings|2025-03-22
19922900|Hippie Farangi|Original Mix|SIAAH, DJ Phellix, Seventh Soul||122|Eb Major|Indie Dance|Laschian Records|2025-01-31
18836757|Yare Jani|Original Mix|DJ Phellix, OF REZZ, Sheenubb||120|A Minor|Organic House|Ubersee Music|2024-04-05
19850289|Sorme|Extended Mix|DJ Phellix, Omid Khoshchehre, mojgan hoseyni||120|G Minor|Melodic House & Techno|Sounds Of Sirin|2025-01-10
19850290|Shooshtari|Extended Mix|DJ Phellix, Seventh Soul, Mahi Roozbahani||122|Db Major|Melodic House & Techno|Sounds Of Sirin|2025-01-10
19910031|Madar Bozorg|Original Mix|DJ Phellix, Soundluxx, Ario Vibes||122|E Minor|Organic House|Ario Vibes|2025-01-03
19646656|Ayooni|Original Mix|DJ Phellix||122|G Major|Electronica|Lump Records|2024-11-22
19545419|Ney|Original Mix|Idin Gorji, DJ Phellix, Ario Vibes, Soudeh Sharhi||122|Ab Minor|Organic House|Ario Vibes|2024-10-18
19600714|Shemroon|Original Mix|DJ Phellix, JKC||123|Db Major|Organic House|Elebated Records|2024-10-11
19600722|Jan O Jahan|Original Mix|Idin Gorji, DJ Phellix, EyeNaz||123|A Major|Organic House|Elebated Records|2024-10-11
19539690|Gheisar|Original Mix|DJ Phellix, DR ZAVIN||105|D Major|Organic House|Ario Records|2024-10-04
19547141|Lalay|DJ Phellix Remix|Namito, Foroogh|DJ Phellix|105|G Minor|Organic House|Alt Orient|2024-09-20
19266333|Nowbahar (feat. Amir Sheykh)|Original Mix|Cafe De Anatolia, DJ Phellix||118|C Minor|Organic House|Cafe De Anatolia|2024-08-23
19118632|Delom|Original Mix|DJ Phellix, Sheenubb, Ben & Vincent||108|B Minor|Organic House|Elebated Records|2024-07-12
19097309|Saqi|DJ Phellix Remix|Nikita, Sherryx, Ario Vibes|DJ Phellix|123|D Minor|Organic House|Ario Vibes|2024-06-21
18952399|Noorani (feat. Sina Heydari)|Original Mix|DJ Phellix, ENKINAKI, Sina Heydari||120|G Major|Organic House|Shango Records|2024-05-03
18493182|Jaane Barbat|Original Mix|SIAAH, DJ Phellix, Laschian Records||122|Gb Major|Organic House|Laschian Records|2024-01-19
18538944|Whirling Dervish|DJ Phellix Remix|Sina Bathaie|DJ Phellix|122|A Minor|Organic House|Windcatcher Records|2024-01-18
18448602|Silk Road|Original Mix|DJ Phellix, ENKINAKI, Pooria Shiringoo||122|D Major|Organic House|Sounds Of Sirin|
18261733|Asemoon Kabood|Original Mix|DJ Phellix, ENKINAKI, Hadi Hadadi||123|D Major|Organic House|Ubersee Music|
18131427|Mey|Original Mix|DJ Phellix, OF REZZ, Sheenubb, LUT Project||122|B Major|Organic House|LUT Project|
18126436|Baam E Makhmal|Original Mix|DJ Phellix, ENKINAKI||118|C Minor|Organic House|Bayati Records|
17692413|Che Danestam|DJ Phellix & Enkinaki Remix|Homayoun Shajarian|DJ Phellix, ENKINAKI|120|D Major|Organic House|Ario Records|
17586794|Eshgh|Original Mix|DJ Phellix, Amir Sheykh, Qualista, Fiooji, 2Moein2||120|Gb Major|Organic House|Qualista|
17500190|Ghamar (feat. Fiooji)|Original Mix|DJ Phellix, Amir Sheykh, Fiooji||105|D Minor|Organic House|Shango Records|
16887202|Roye To|Original Mix|DJ Phellix, Amir Sheykh, Sant (IR)||115|A Minor|Organic House|Shango Records|
17415674|Straggler Setar|Original Mix|DJ Phellix, rohaab, Sant (IR)||122|D Major|Organic House|Alt Orient|
17415676|Saadi|Original Mix|DJ Phellix, Amir Sheykh, Sant (IR)||90|D Minor|Organic House|Alt Orient|
17415679|Sanama|Original Mix|DJ Phellix, Amir Sheykh||122|E Minor|Organic House|Alt Orient|
17416416|Shah Sanam|Original Mix|DJ Phellix, Amir Sheykh, Fiooji||100|G Minor|Organic House|Ario Records|
17204348|Bote Chin (feat. Amir Sheykh)|Original Mix|DJ Phellix, Amir Sheykh, OF REZZ||115|A Major|Organic House|trndmsk|
16970147|Eivan (feat. Sheenubb)|Original Mix|Cafe De Anatolia, DJ Phellix, Ahira||116|Bb Minor|Organic House|Cafe De Anatolia LAB|
16588328|Ey Mah|DJ Phellix Remix|Idin Gorji, HAMED SHAMS|DJ Phellix|115|Eb Minor|Deep House|Ario Records|
16588330|Avaye Tanhaei|Original Mix|DJ Phellix, Sheenubb||115|A Minor|Deep House|Ario Records|
16565584|Hich|Original Mix|DJ Phellix, rohaab||114|Db Minor|Deep House|Ario Records|
16358252|Pirhan|Original Mix|Bayza, DJ Phellix, Sant (IR), Sheenubb||108|Db Minor|Organic House|George V|
15475457|Ashke Setareh|Original Mix|DJ Phellix, rohaab||115|E Major|Deep House|Ario Records|
12029708|Sarmast|Original Mix|DJ Phellix, Faeze Zare Rafi||114|C# Minor|Dance / Pop|Deep Strips|
15240202|Hayahoo|Original Mix|DJ Phellix, rohaab||118|Db Minor|Dance / Pop|KudoZ Records|
15784426|Majnoon|Original Mix|Sant, DJ Phellix, Amin Eftekhari||112|B Minor|Organic House|Ario Records|
15733686|Siashum|Original Mix|PARSAPI, DJ Phellix||120|A Minor|Melodic House & Techno|Suprematic|
15507944|Delwan (feat. Sant (IR))|Original Mix|DJ Phellix||110|F Minor|Organic House|Suprematic|
15296706|Hur (feat. Saman Gorgin)|Original Mix|DJ Phellix||120|D Major|Organic House|Suprematic|
15237024|Atashe Del|Original Mix|DJ Phellix, rohaab||115|Bb Major|Deep House|Ario Records|
14686093|DayBreak (ft. Behrooz Shiri)|Original Mix|DJ Phellix, Adeia||91|D Minor|Deep House|Ario Records|
13894493|Pol|DJ Phellix Remix|Alireza Ghorbani|DJ Phellix|123|Gb Minor|Deep House|Ario Records|
13748362|Navaei (feat. Amir Sheykh)|Original Mix|DJ Phellix, Amir Sheykh||110|C# Minor|Electronica|Cafe De Anatolia|
11440562|In Man Kist|DJ Phellix Remix|M Joobi, Pobon|DJ Phellix|122|C Minor|Indie Dance|Deep Strips|
13291702|Del Barnakanam (feat. Amir Sheykh)|Original Mix|DJ Phellix||105|C Minor|Deep House|Ario Records|
13100590|Dashtestani|Original Mix|DJ Phellix, Faeze Zare Rafi||116|C Minor|Electronica|Cafe De Anatolia|
13152672|Bar Sabze Neshin|Original Mix|DJ Phellix, Maryama||120|D Minor|Organic House|George V|
13201597|Man Koja Baran Koja|DJ Phellix Remix|Homayoun Shajarian|DJ Phellix|118|C Minor|Deep House|Adrenaline Records|
16559294|Sheyda|Original Mix|DJ Phellix, Maria Ebra||118|Bb Minor|Mainstage|PalmTherapySounds|
"""

# Remixes of songs by well-known Persian singers. The crowd may recognize the original.
KNOWN_ORIGINALS = {
    "Che Danestam": "Homayoun Shajarian",
    "Man Koja Baran Koja": "Homayoun Shajarian",
    "Pol": "Alireza Ghorbani",
    "Moama": "Moein",
    "In Man Kist": "M Joobi & Pobon",
}

MD = "https://www.mitchatnim.co.il/article/18673/"   # wedding songs by stage (dance floor / ending)
ACUM = "https://www.walla.co.il/entertainment/music/3431954"  # Acum: top 20 at weddings & events in 2020
RIZE = "https://rize.co.il/must-have-songs/"  # "emergency list" for the dance floor, Dec 2025

# group: persian_wedding = Persian songs played at weddings; persian_remix = electronic remix;
#        israeli_wedding = Hebrew/English wedding songs.
# moments come only from a source that names the wedding stage.
OTHER = [
    # --- Persian remixes from other DJs ---
    dict(title="Sabad Sabad (Afro House Remix)", artists=["Ebi"], remixers=["DJ Next Level"], lang="fa",
         group="persian_remix", genre="Afro House", known_original="Ebi",
         source="https://soundcloud.com/user-947646353/dj-next-level-ebi-sabad-sabad-afrohouse-remix"),
    dict(title="Talagh (Nick AM Edit)", artists=["Googoosh"], remixers=["Nick AM"], lang="fa",
         group="persian_remix", genre="Funk / Edit", known_original="Googoosh", era="pre-1979",
         source="https://thenewlofi.com/nick-am-remixes-talagh-by-persian-madonna-googoosh/"),
    # --- The user's Persian wedding songs (identified) ---
    dict(title="Soosan Khanoom", title_he="סוזן חנום", artists=["Barobax", "Gamno"], lang="fa",
         group="persian_wedding", release_date="2010-01-16", user_core=True,
         source="https://en.wikipedia.org/wiki/Barobax"),
    dict(title="Joone Khodet", title_he="ג׳ונה חודט", artists=["Black Cats"], lang="fa",
         group="persian_wedding", user_core=True, notes="Lead vocal: Kamyar",
         source="https://musicrooz.com/%D8%A8%D9%84%DA%A9-%DA%A9%D8%AA%D8%B3-%D8%AC%D9%88%D9%86-%D8%AE%D9%88%D8%AF%D8%AA/"),
    dict(title="Gol Pari Joon", title_he="גול פרי ג׳ון", artists=["Armin Nosrati"], lang="fa",
         group="persian_wedding", user_core=True, notes="The user mentioned parts 1 and 2; part 2 not yet identified",
         source="https://dibasmusic.com/armin-nosrati-golpari-joon/"),
    dict(title="Aroos Domado Beboos", title_he="ארוס דומד בבוס", artists=["Armin Nosrati"], lang="fa",
         group="persian_wedding", user_core=True,
         source="https://ahaang.com/%D8%A2%D8%B1%D9%85%DB%8C%D9%86-%D9%86%D8%B5%D8%B1%D8%AA%DB%8C-%D8%B9%D8%B1%D9%88%D8%B3-%D8%AF%D9%88%D9%85%D8%A7%D8%AF%D9%88-%D8%A8%D8%A8%D9%88%D8%B3/"),
    dict(title="Vay Cheghad Mastam Man", artists=["Sasy"], lang="fa", group="persian_wedding", user_core=True,
         source="https://www.deezer.com/artist/4616523"),
    dict(title="Gentleman", artists=["Sasy"], lang="fa", group="persian_wedding", user_core=True,
         source="https://www.deezer.com/artist/4616523"),
    # --- Israeli weddings: Acum's top 20 for 2020 ---
    *[dict(title=t, artists=a, lang=l, group="israeli_wedding", moments=["dance"], rank=i + 1,
           list_year=2020, source=ACUM) for i, (t, a, l) in enumerate([
        ("יעשו לנו כבוד", ["עומר אדם"], "he"), ("מסע", ["אליעד"], "he"), ("טמפרטורה", ["עומר אדם"], "he"),
        ("פאוץ׳", ["נועה קירל"], "he"), ("Dance Monkey", ["Tones and I"], "en"),
        ("יאסו", ["סטטיק ובן אל תבורי", "עדן בן זקן"], "he"), ("חברות שלך", ["עומר אדם"], "he"),
        ("קרמלה", ["משה פרץ"], "he"), ("שני משוגעים", ["עומר אדם"], "he"),
        ("אין יותר מועדונים", ["עדן חסון"], "he"), ("Soldi", ["Mahmood"], "it"),
        ("חתונת השנה", ["איתי לוי", "אייל גולן"], "he"), ("Further Up", ["סטטיק ובן אל תבורי", "Pitbull"], "en"),
        ("הולכים להשתגע", ["משה פרץ", "אייל גולן"], "he"), ("חגיגה בישראל", ["דודו אהרון", "ליאור נרקיס"], "he"),
        ("דיבור נגוע", ["מרגי", "סטפן"], "he"), ("ממה את מפחדת", ["אייל גולן", "בניה ברבי"], "he"),
        ("מהפכה של שמחה", ["עומר אדם", "ליאור נרקיס"], "he"), ("אח שלי מתחתן", ["מוש בן ארי"], "he"),
        ("לא מבינה עברית", ["אייל גולן"], "he"),
    ])],
    # --- Israeli weddings: dance-floor "emergency list" (2025) ---
    *[dict(title=t, artists=a, lang=l, group="israeli_wedding", moments=["dance"], list_year=2025, source=RIZE)
      for t, a, l in [("תל אביב", ["עומר אדם"], "he"), ("I Gotta Feeling", ["The Black Eyed Peas"], "en"),
                      ("היא רק רוצה לרקוד", ["משה פרץ", "עומר אדם"], "he"), ("Freed From Desire", ["Gala"], "en")]],
    # --- Israeli weddings: dance floor and ending song (mitchatnim) ---
    *[dict(title=t, artists=a, lang=l, group="israeli_wedding", moments=m, source=MD) for t, a, l, m in [
        ("יש לי חור בלב בצורה שלך", ["הג׳ירפות"], "he", ["dance"]), ("הזוג הזה", ["מרגי"], "he", ["dance"]),
        ("זהב", ["סטטיק ובן אל תבורי"], "he", ["dance"]), ("Happy", ["Pharrell Williams"], "en", ["dance"]),
        ("Can't Stop the Feeling", ["Justin Timberlake"], "en", ["dance"]),
        ("Love Me Again", ["John Newman"], "en", ["dance"]),
        ("Signed, Sealed, Delivered (I'm Yours)", ["Stevie Wonder"], "en", ["dance"]),
        ("You've Got the Love", ["Florence + The Machine"], "en", ["dance"]),
        ("About Damn Time", ["Lizzo"], "en", ["dance"]),
        ("הנך יפה", ["עידן רייכל"], "he", ["end_of_night"]), ("שבוע טוב", ["אברהם טל"], "he", ["end_of_night"]),
        ("איש של לילה", ["רוני דלומי"], "he", ["end_of_night"]), ("Levitating", ["Dua Lipa"], "en", ["end_of_night"]),
        ("Golden", ["Harry Styles"], "en", ["end_of_night"]),
        ("Somewhere Over the Rainbow", ["Israel Kamakawiwoʻole"], "en", ["end_of_night"]),
    ]],
]

# Songs the user named whose exact version is still unclear: several singers have a song by that name.
PENDING = [
    dict(name_he="דוחטר אווזי", guess="Dokhtar Irooni", candidates=["Siavash Shams", "Sohrab Pakzad", "Andy"]),
    dict(name_he="אנר אנר", guess="Anar Anar", candidates=["Omid Oghabi", "Ghasem Fazeli", "Morteza Barjasteh", "Abolhasan Javidan"]),
    dict(name_he="ביגהרר", guess="Bigharar / Bigharāram", candidates=["Moein", "Andy (album: Bi Gharar)", "Mohsen Ebrahimzadeh"]),
    dict(name_he="גול פרי ג׳ון 2", guess="Gol Pari Joon 2", candidates=[]),
]

# Standard key-to-Camelot map. Harmonic mixing uses Camelot codes.
CAMELOT = {
    ("C", "Major"): "8B", ("G", "Major"): "9B", ("D", "Major"): "10B", ("A", "Major"): "11B",
    ("E", "Major"): "12B", ("B", "Major"): "1B", ("Gb", "Major"): "2B", ("F#", "Major"): "2B",
    ("Db", "Major"): "3B", ("C#", "Major"): "3B", ("Ab", "Major"): "4B", ("G#", "Major"): "4B",
    ("Eb", "Major"): "5B", ("D#", "Major"): "5B", ("Bb", "Major"): "6B", ("A#", "Major"): "6B",
    ("F", "Major"): "7B",
    ("A", "Minor"): "8A", ("E", "Minor"): "9A", ("B", "Minor"): "10A", ("Gb", "Minor"): "11A",
    ("F#", "Minor"): "11A", ("Db", "Minor"): "12A", ("C#", "Minor"): "12A", ("Ab", "Minor"): "1A",
    ("G#", "Minor"): "1A", ("Eb", "Minor"): "2A", ("D#", "Minor"): "2A", ("Bb", "Minor"): "3A",
    ("A#", "Minor"): "3A", ("F", "Minor"): "4A", ("C", "Minor"): "5A", ("G", "Minor"): "6A",
    ("D", "Minor"): "7A",
}


def split(s):
    return [x.strip() for x in s.split(",") if x.strip()]


def yt_search(q):
    return "https://www.youtube.com/results?search_query=" + q.replace(" ", "+")


songs = []
for line in BEATPORT.strip().splitlines():
    bid, title, mix, artists, remixers, bpm, key, genre, label, date = [p.strip() for p in line.split("|")]
    note, scale = key.split(" ")
    artists_l = split(artists)
    q = f"{title} {mix} {' '.join(a for a in artists_l if a not in ('Buddha Bar', 'Ario Vibes'))}"
    songs.append({
        "id": f"bp-{bid}",
        "title": title,
        "mix": mix,
        "artists": artists_l,
        "remixers": split(remixers),
        "bpm": int(bpm),
        "key": key,
        "camelot": CAMELOT[(note, scale)],
        "genre": genre,
        "label": label,
        "release_date": date or None,
        "known_original": KNOWN_ORIGINALS.get(title),
        "era": None,
        "status": "verified",
        "source": f"https://www.beatport.com/track/{re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')}/{bid}",
        "youtube": yt_search(q),
        # Filled in by the user's listening (not invented):
        "energy": None, "familiarity": None, "moments": [], "my_rating": None,
    })

for s in songs:
    s.update(lang=None, group="persian_remix", user_core=False, title_he=None, notes=None, rank=None, list_year=None)

for i, o in enumerate(OTHER):
    songs.append({
        "id": f"web-{i+1}", "title": o["title"], "title_he": o.get("title_he"), "mix": None,
        "artists": o["artists"], "remixers": o.get("remixers", []), "bpm": None, "key": None, "camelot": None,
        "genre": o.get("genre"), "label": None, "release_date": o.get("release_date"),
        "known_original": o.get("known_original"), "era": o.get("era"),
        "lang": o.get("lang"), "group": o["group"], "user_core": o.get("user_core", False),
        "notes": o.get("notes"), "rank": o.get("rank"), "list_year": o.get("list_year"),
        "status": "partial", "source": o["source"],
        "youtube": yt_search(o["title"] + " " + " ".join(o["artists"])),
        "energy": None, "familiarity": None, "moments": o.get("moments", []), "my_rating": None,
    })

pending = [{"id": f"pending-{i+1}", "status": "needs_identification", **p} for i, p in enumerate(PENDING)]

out = os.path.join(os.path.dirname(__file__), "songs.js")
with open(out, "w", encoding="utf-8") as f:
    f.write("// Generated by data/build_catalog.py. Do not edit by hand.\n")
    f.write("window.CATALOG = ")
    json.dump({"generated": "2026-11-18", "songs": songs, "pending": pending}, f, ensure_ascii=False, indent=1)
    f.write(";\n")
print(f"{len(songs)} songs, {len(pending)} pending -> {out}")
