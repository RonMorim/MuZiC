"""Songs that are not from Beatport. Imported by build_catalog.py.

group: persian_wedding = Persian songs played at weddings; persian_remix = electronic remix;
       world_party = non-Persian party tracks that YouTube put next to Persian wedding songs.
plays: YouTube views as shown in the user's screenshots (2026-11-18). dur: length shown there.
"""

PLAYLIST = "The user's Apple Music playlist “Persian Party” (screenshot, 2026-11-18)"
YT = "YouTube Mix (user screenshot, 2026-11-18)"


def fa(title, artists, core=False, views=None, dur=None, src=PLAYLIST, group="persian_wedding", lang="fa", **kw):
    sec = None
    if dur:
        m, s = dur.split(":")
        sec = int(m) * 60 + int(s)
    if "Bandari" in title or "Bandari" in " ".join(artists):
        kw.setdefault("genre", "Bandari")
    return dict(title=title, artists=artists, lang=lang, group=group, user_core=core,
                plays=views, plays_src="YouTube views" if views else None, duration_sec=sec, source=src, **kw)


OTHER = [
    # --- Persian remixes from other DJs ---
    dict(title="Sabad Sabad (Afro House Remix)", artists=["Ebi"], remixers=["DJ Next Level"], lang="fa",
         group="persian_remix", genre="Afro House", known_original="Ebi",
         source="https://soundcloud.com/user-947646353/dj-next-level-ebi-sabad-sabad-afrohouse-remix"),
    dict(title="Talagh (Nick AM Edit)", artists=["Googoosh"], remixers=["Nick AM"], lang="fa",
         group="persian_remix", genre="Funk / Edit", known_original="Googoosh", era="pre-1979",
         source="https://thenewlofi.com/nick-am-remixes-talagh-by-persian-madonna-googoosh/"),

    # --- The user's own list: “Persian Party” playlist (23 songs) + songs named in chat ---
    fa("Anar Anar", ["Morteza"], core=True, views=21_000, dur="4:09", title_he="אנר אנר"),
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
    fa("Jooneh Khodet", ["Black Cats"], core=True, views=10_000_000, dur="4:14", title_he="ג׳ונה חודט"),
    fa("Gentleman", ["Sasy"], core=True),
    fa("Beraghsa", ["Mohsen Chavoshi"], core=True),
    fa("Ba Man Miraghsi", ["Tohi", "Sami Beigi"], core=True),
    fa("Temptation", ["Arash"], core=True),
    fa("Stone Flower (Original)", ["Namito"], core=True),
    fa("Baba Karam", ["Iman Sani"], core=True),
    fa("Dokhtare Ahvazi (Bandari)", ["Sandy"], core=True, title_he="דוחטר אווזי"),
    fa("Ronak (Instrumental)", ["Bijan Mortazavi"], core=True),
    fa("Aroos Doomado Beboos", ["Armin Nosrati"], core=True, views=22_000, dur="3:00", title_he="ארוס דומד בבוס"),
    fa("Gol e Goldoon", ["Shahram Solati"], core=True),
    fa("Golpari (Gol Pari Joon)", ["Armin Nosrati"], core=True, views=1_900_000, dur="5:29", src=YT, title_he="גול פרי ג׳ון"),
    fa("Soosan Khanoom", ["Barobax", "Gamno"], core=True, src="https://en.wikipedia.org/wiki/Barobax",
       title_he="סוזן חנום", release_date="2010-01-16"),

    # --- Suggested by YouTube Mixes (not picked by the user) ---
    fa("Jooni Joonom", ["Leila Forouhar"], views=74_000_000, dur="4:14", src=YT),
    fa("Ey Joonam", ["Sami Beigi"], views=49_000_000, dur="3:37", src=YT),
    fa("Del Ey Del", ["Leila Forouhar"], views=45_000_000, dur="6:12", src=YT),
    fa("Delakam Delbarakam", ["Shahram Shabpareh", "Nahid"], views=27_000_000, dur="4:32", src=YT),
    fa("Kabootare Del", ["Susan Roshan"], views=23_000_000, dur="5:34", src=YT),
    fa("Yare Shirin", ["Leila Forouhar"], views=18_000_000, dur="4:39", src=YT),
    fa("Gole Royaei", ["Omid"], views=15_000_000, dur="5:27", src=YT),
    fa("Dir Oumadi", ["Leila Forouhar"], views=11_000_000, dur="4:01", src=YT),
    fa("Rotab (Bandari)", ["Hassan Shamaizadeh"], views=7_600_000, dur="5:34", src=YT),
    fa("Yade Tou", ["Moein"], views=6_300_000, dur="5:00", src=YT),
    fa("Khanoom", ["Black Cats"], views=5_300_000, dur="3:18", src=YT),
    fa("Ye Dokhtar Daram", ["Hassan Shamaeezadeh"], views=5_100_000, dur="4:51", src=YT),
    fa("Dokhtar Bandari", ["Shahrum Kashani"], views=4_300_000, dur="5:13", src=YT, genre="Bandari"),
    fa("Nazi Joon", ["Shahrum Kashani"], views=3_400_000, dur="4:06", src=YT),
    fa("Vay Ke Che Halie", ["Amir Tataloo", "Ardalan Tomeh"], views=3_200_000, dur="3:09", src=YT),
    fa("Baz Mano Kashti", ["Morteza"], views=2_100_000, dur="4:51", src=YT),
    fa("Engaar Na Engaar", ["Mansour"], views=2_000_000, dur="3:36", src=YT),
    fa("Aroos-E-Mahtab", ["Faramarz Assef"], views=1_800_000, dur="4:45", src=YT),
    fa("Nastaran", ["Farshid Amin"], views=1_800_000, dur="5:43", src=YT),
    fa("Dokhtare Irooni", ["Andy"], views=1_700_000, dur="5:36", src=YT),
    fa("Dokhtar Irooni", ["Mehran"], views=1_600_000, dur="4:29", src=YT),
    fa("Ba Cheshmat", ["Ali Danial"], views=1_400_000, dur="3:44", src=YT),
    fa("Del Beh Tou Bastam", ["Morteza"], views=1_100_000, dur="5:09", src=YT),
    fa("Dokhtare Abadan", ["Sharareh"], views=1_000_000, dur="4:32", src=YT),
    fa("Gole Baagh", ["Saeed Mohammadi"], views=626_000, dur="4:48", src=YT),
    fa("Ahoo", ["Morteza"], views=518_000, dur="4:31", src=YT),
    fa("Mano Del", ["Black Cats"], views=506_000, dur="5:02", src=YT),
    fa("Babakaram", ["Armin Nosrati"], views=459_000, dur="5:48", src=YT),
    fa("Doostet Daram", ["Davood Behboodi"], views=451_000, dur="6:06", src=YT),
    fa("Haji 3 Hamoomi", ["Faramarz Assef"], views=231_000, dur="5:32", src=YT),
    fa("Pari & Mari", ["Armin Nosrati"], src=YT),
    fa("Diar (Deyar)", ["Shahram Shabpareh"], src=YT),
    fa("Eshveh", ["Bijan Mortazavi"], src=YT),

    # --- Non-Persian party tracks YouTube placed next to Persian wedding songs ---
    fa("I'll Be Missing You (Just Be Good To Me)", ["P.Diddy", "Karmah"], views=25_000_000, dur="3:15",
       src=YT, group="world_party", lang="en"),
    fa("Asereje (Aftermix)", ["Lautarogalarza Dj"], views=13_000_000, dur="2:26", src=YT, group="world_party", lang="es"),
    fa("Begriff Shuffle", ["Magua"], views=11_000_000, dur="3:41", src=YT, group="world_party", lang=None),
]

PENDING = []
