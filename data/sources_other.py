"""Songs that are not from Beatport. Imported by build_catalog.py.

group: persian_wedding = Persian songs played at weddings; persian_remix = electronic remix;
       israeli_now = current Hebrew/English hits.
plays: popularity count as published by its source (YouTube views or Spotify streams), with plays_src.
"""

PLAYLIST = "The user's Apple Music playlist “Persian Party” (screenshot, 2026-11-18)"
YTMIX = "YouTube Mix based on Armin Nosrati – Golpari (user screenshot, 2026-11-18)"
SPOTIFY_IL = "https://kworb.net/spotify/country/il_daily.html"
SPOTIFY_GLOBAL = "https://kworb.net/spotify/country/global_daily.html"


def fa(title, artists, core=False, views=None, src=PLAYLIST, **kw):
    return dict(title=title, artists=artists, lang="fa", group="persian_wedding", user_core=core,
                plays=views, plays_src="YouTube views" if views else None, source=src, **kw)


OTHER = [
    # --- Persian remixes from other DJs ---
    dict(title="Sabad Sabad (Afro House Remix)", artists=["Ebi"], remixers=["DJ Next Level"], lang="fa",
         group="persian_remix", genre="Afro House", known_original="Ebi",
         source="https://soundcloud.com/user-947646353/dj-next-level-ebi-sabad-sabad-afrohouse-remix"),
    dict(title="Talagh (Nick AM Edit)", artists=["Googoosh"], remixers=["Nick AM"], lang="fa",
         group="persian_remix", genre="Funk / Edit", known_original="Googoosh", era="pre-1979",
         source="https://thenewlofi.com/nick-am-remixes-talagh-by-persian-madonna-googoosh/"),

    # --- The user's own list: “Persian Party” playlist (23 songs) + songs named in chat ---
    fa("Anar Anar", ["Morteza"], core=True, title_he="אנר אנר"),
    fa("Yasamin", ["Omid"], core=True),
    fa("Hamsafar", ["Ebi"], core=True),
    fa("Majnoon", ["Moein"], core=True),
    fa("Che Khoshgel Shodi", ["Andy"], core=True),
    fa("Age Eshgh Hamineh", ["Andy"], core=True),
    fa("Sheytoonak", ["Afshin"], core=True),
    fa("Gozashteh", ["Moein"], core=True),
    fa("Khoshgela Bayad Beraghsand", ["Andy"], core=True),
    fa("To To", ["Elcid"], core=True, notes="Shown as unavailable in the Apple Music playlist"),
    fa("Bigharar", ["Moein"], core=True, title_he="ביגהרר"),
    fa("Aziz Delami", ["Mansour"], core=True),
    fa("Jooneh Khodet", ["Black Cats"], core=True, views=10_000_000, title_he="ג׳ונה חודט"),
    fa("Gentleman", ["Sasy"], core=True),
    fa("Beraghsa", ["Mohsen Chavoshi"], core=True),
    fa("Ba Man Miraghsi", ["Tohi", "Sami Beigi"], core=True),
    fa("Temptation", ["Arash"], core=True),
    fa("Stone Flower (Original)", ["Namito"], core=True),
    fa("Baba Karam", ["Iman Sani"], core=True),
    fa("Dokhtare Ahvazi (Bandari)", ["Sandy"], core=True, title_he="דוחטר אווזי", genre="Bandari"),
    fa("Ronak (Instrumental)", ["Bijan Mortazavi"], core=True),
    fa("Aroos Doomado Beboos", ["Armin Nosrati"], core=True, views=22_000, title_he="ארוס דומד בבוס"),
    fa("Gol e Goldoon", ["Shahram Solati"], core=True),
    fa("Golpari (Gol Pari Joon)", ["Armin Nosrati"], core=True, views=1_900_000, src=YTMIX, title_he="גול פרי ג׳ון"),
    fa("Soosan Khanoom", ["Barobax", "Gamno"], core=True, src="https://en.wikipedia.org/wiki/Barobax",
       title_he="סוזן חנום", release_date="2010-01-16"),

    # --- Suggested by YouTube's Mix (not picked by the user) ---
    fa("Jooni Joonom", ["Leila Forouhar"], views=74_000_000, src=YTMIX),
    fa("Ey Joonam", ["Sami Beigi"], views=49_000_000, src=YTMIX),
    fa("Del Ey Del", ["Leila Forouhar"], views=45_000_000, src=YTMIX),
    fa("Yare Shirin", ["Leila Forouhar"], views=18_000_000, src=YTMIX),
    fa("Gole Royaei", ["Omid"], views=15_000_000, src=YTMIX),
    fa("Dir Oumadi", ["Leila Forouhar"], views=11_000_000, src=YTMIX),
    fa("Khanoom", ["Black Cats"], views=5_300_000, src=YTMIX),
    fa("Ye Dokhtar Daram", ["Hassan Shamaeezadeh"], views=5_100_000, src=YTMIX),
    fa("Vay Ke Che Halie", ["Amir Tataloo", "Ardalan Tomeh"], views=3_200_000, src=YTMIX),
    fa("Gole Baagh", ["Saeed Mohammadi"], views=626_000, src=YTMIX),
    fa("Babakaram", ["Armin Nosrati"], views=459_000, src=YTMIX),
    fa("Haji 3 Hamoomi", ["Faramarz Assef"], views=231_000, src=YTMIX),
    fa("Pari & Mari", ["Armin Nosrati"], src=YTMIX),
    fa("Diar (Deyar)", ["Shahram Shabpareh"], src=YTMIX),
    fa("Eshveh", ["Bijan Mortazavi"], src=YTMIX),
]


def il(rows, src, label):
    out = []
    for pos, artist, title, streams in rows:
        lang = "en" if title.isascii() else "he"
        out.append(dict(title=title, artists=[artist], lang=lang, group="israeli_now", rank=pos,
                        list_year=label, plays=streams, plays_src="Spotify streams" if streams else None,
                        source=src))
    return out


# Spotify Israel daily chart, 2026-11-16 (top 60). Streams = total while on the chart.
IL_CHART = [
    (1, "Mor", "מטריקס", 2927255), (2, "נדב חנציס", "קאט לדבר הבא", 2756191),
    (3, "young buta", "גולגול מנקות", 547194), (4, "Ofek Adanek", "נתתי לך בית", 5753608),
    (5, "רואי אדם", "אבי הטחול", 8825180), (6, "young buta", "שחור לבן", 4623422),
    (7, "Mor", "לא קונה אותי", 4868997), (8, "Odeya", "פאפית", 4985877),
    (9, "Bar Tzabary", "ילדה מטורפת", 5282995), (10, "Mor", "תאהב אותי ככה", 4094549),
    (11, "Osher Cohen", "דאון", 4558916), (12, "Eden Ben Zaken", "מחול (עם ששון איפרם שאולוב)", 3700843),
    (13, "נדב חנציס", "כבר לא שמח (עם Ofek Adanek)", 5140316), (14, "Osher Cohen", "כולם גנבים", 16754238),
    (15, "LIAD MEIR", "יוצאת מן הכלל (עם Ofek Adanek)", 7346119), (16, "רואי אדם", "קילומטר קדימה", 2234015),
    (17, "רואי אדם", "אהבת חיי", 6185828), (18, "Eden Hason", "איך שהיא רוקדת (עם Ofek Adanek, Agam Buhbut)", 10006668),
    (19, "Ness", "מונולוג (עם STILLA)", 3438113), (20, "Mor", "אולפנה של צביה", 2945933),
    (21, "Itay Levi", "03", 6659673), (23, "SIENNA SPIRO", "Great Expectation", 2131170),
    (24, "Odeya", "עשר רמות מעליו", 7811832), (25, "Omer Adam", "תקופה חרא", 9099427),
    (26, "Mor", "לא שבת ולא שלום", 2625074), (27, "התאומים", "אם לא את", 1513206),
    (28, "נדב חנציס", "אם את כבר הולכת", 22379919), (29, "Eden Ben Zaken", "רולקס וקסקט", 10116886),
    (30, "Itay Levi", "06", 6228813), (31, "הגר יפת", "אתה חי בחלום", 3231470),
    (32, "Mor", "סחרחורות", 8171791), (33, "Agam Buhbut", "המבט בעיניך", 7074804),
    (34, "נדב חנציס", "אהבה ראשונה", 6639907), (35, "LIAD MEIR", "רוקד כל כך יפה", 911689),
    (36, "ששון איפרם שאולוב", "סתם", 397552), (37, "התאומים", "עץ או פלי", 577633),
    (38, "Omer Adam", "השיר שאת אהבת", 20891026), (39, "Peer Tasi", "הלוואי (עם Hanan Ben Ari)", 7186944),
    (40, "ששון איפרם שאולוב", "נווה הדרים", 4163405), (41, "Ben Zur", "אהבת השם", 9033243),
    (42, "נדב חנציס", "אביצ׳י", 2810953), (43, "Shuli Rand", "לב לבן", 6461218),
    (44, "Jung Kook", "Seven", 10689381), (45, "Tate McRae", "Housewife", 685789),
    (46, "Eden Ben Zaken", "לופ שלא נגמר", 2738559), (47, "young buta", "סוד הנעורים", 1074469),
    (48, "Ben Zur", "איש הפלא", 6581748), (49, "Meir Banai", "אבל את (עם Eviatar Banai)", 3934236),
    (50, "Omer Adam", "בן 32", 7525310), (51, "Ben Zur", "אבא", 13965777),
    (52, "אביחי שלמה", "ילד זינו", 728415), (53, "Temper City", "Self Aware", 5032487),
    (55, "Mor", "תקרא לי מאמי", 7620177), (56, "Itay Levi", "מרכז תל אביב", 7881646),
    (57, "Eden Hason", "לא מעניין אותי", 167802), (58, "Omer Adam", "מלכת הדור", 24539012),
    (59, "Peer Tasi", "עוף מוזר", 13527695), (60, "Itay Levi", "08", 2513607),
]
# Skipped: #22 and #54 are a special/live version of a song already listed.

# Spotify global daily chart, 2026-11-16: current English songs (under ~1 year on the chart;
# Christmas songs and old catalog hits left out). No stream counts copied.
GLOBAL_EN = [
    (1, "Ashe", "Stop The Wedding!", None), (4, "Olivia Rodrigo", "the cure", None),
    (5, "ADÉLA", "Nicole Kidman", None), (6, "ADÉLA", "Ain't In LA", None),
    (7, "Jamie Miller", "Babydoll", None), (8, "Malcolm Todd", "Earrings", None),
    (11, "Olivia Rodrigo", "stupid song", None), (26, "Tame Impala", "Loser", None),
    (28, "Ella Langley", "Choosin' Texas", None), (33, "Harry Styles", "Coming Up Roses", None),
    (37, "Ariana Grande", "hate that i made you love me", None),
]

OTHER += il(IL_CHART, SPOTIFY_IL, "Spotify IL · 2026-11-16")
OTHER += il(GLOBAL_EN, SPOTIFY_GLOBAL, "Spotify Global · 2026-11-16")

# Every song the user named is now identified.
PENDING = []
