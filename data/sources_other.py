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
    fa("Gol Pari 2", ["Armin Nosrati"], core=True, src="https://songbpm.com/@armin-nosrati/gol-pari-2---original-mix-ENo4iwEG5O",
       title_he="גול פרי ג׳ון 2"),
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

# BPM / key / energy from songbpm.com (data comes from Spotify's audio analysis), fetched 2026-11-18.
# Each value: (bpm, note, mode, energy, danceable, songbpm path). Only exact song matches are listed.
# Persian 6/8 songs are sometimes reported at double tempo (e.g. 172 instead of 86); the planner allows half/double time.
SONGBPM = {
    "Anar Anar": (109, "Bb", "minor", "high", "somewhat", "morteza/anar-anar"),
    "Yasamin": (110, "F", "minor", "high", "somewhat", "omid/yasamin"),
    "Hamsafar": (133, "A", "major", "average", "somewhat", "ebi/hamsafar-zbsg1"),
    "Majnoon": (172, "C", "minor", "high", "very", "moein/majnoon"),
    "Che Khoshgel Shodi": (122, "Bb", "minor", "high", "very", "andy/che-khoshgel-shodi-MIDEPr9A2e"),
    "Age Eshgh Hamineh": (160, "A", "major", "high", "somewhat", "andy/ageh-eshgh-hamineh-l13rp"),
    "Sheytoonak": (135, "Bb", "minor", "high", "somewhat", "afshin/sheytoonak"),
    "Gozashteh": (97, "E", "minor", "high", "very", "moein/gozashteh"),
    "Khoshgela Bayad Beraghsand": (122, "D", "minor", "high", "very", "andy/khoshgela-bayad-beraghsand"),
    "To To": (127, "Gb", "minor", "high", "very", "elcid/toto-zeqa4"),
    "Bigharar": (116, "E", "minor", "high", "very", "moein/bigharar"),
    "Aziz Delami": (174, "C", "major", "high", "very", "mansour/aziz-delami"),
    "Jooneh Khodet": (120, "Gb", "minor", "high", "very", "black-cats/jooneh-khodet"),
    "Gentleman": (128, "C", "major", "high", "very", "sasy/gentleman-R9qDVmWSMP"),
    "Beraghsa": (120, "Db", "minor", "high", "very", "mohsen-chavoshi/beraghsa-OMzjJqKh1s"),
    "Temptation": (108, "E", "minor", "high", "very", "arash/temptation-feat-rebecca"),
    "Stone Flower (Original)": (114, "G", "major", "high", "very", "namito/stone-flower---original"),
    "Dokhtare Ahvazi (Bandari)": (120, "G", "major", "high", "very", "sandy/dokhtare-ahvazi"),
    "Ronak (Instrumental)": (106, "G", "major", "high", "somewhat", "bijan-mortazavi/ronak"),
    "Aroos Doomado Beboos": (130, "Bb", "minor", "high", "very", "armin-nosrati/aroos-doomado-beboos-bycw7"),
    "Golpari (Gol Pari Joon)": (134, "C", "major", "high", "very", "armin-nosrati/gol-pari---original-mix-8dpDvymjy0"),
    "Gol Pari 2": (134, "Db", "major", "high", "very", "armin-nosrati/gol-pari-2---original-mix-ENo4iwEG5O"),
    "Soosan Khanoom": (128, "Gb", "minor", "high", "very", "barobax/soosan-khanoom-hltmu"),
    "Jooni Joonom": (120, "D", "major", "high", "very", "leila-forouhar/jooni-joonom"),
    "Ey Joonam": (105, "Ab", "major", "high", "somewhat", "sami-beigi/ey-joonam"),
    "Del Ey Del": (121, "Bb", "minor", "high", "somewhat", "leila-forouhar/del-ey-del"),
    "Kabootare Del": (147, "F", "minor", "average", "very", "susan-roshan/kabootare-del-eflug"),
    "Yare Shirin": (148, "Ab", "major", "average", "somewhat", "leila-forouhar/yare-shirin"),
    "Gole Royaei": (192, "F", "minor", "high", "not very", "omid/gole-royaei-ofpkVVg6yR"),
    "Rotab (Bandari)": (121, "D", "major", "high", "very", "hassan-shamaizadeh/rotab-bandari-stxt4"),
    "Yade Tou": (111, "Bb", "minor", "high", "very", "moein/yade-tou-hbgix"),
    "Khanoom": (195, "D", "major", "high", "very", "black-cats/khanoom-trxgd"),
    "Ye Dokhtar Daram": (140, "F", "minor", "low", "very", "hassan-shamaizadeh/yeh-dokhtar-daram-shah-nadareh-whqqk"),
    "Dokhtar Bandari": (122, "A", "minor", "high", "very", "shahrum-kashani/dokhtar-bandari"),
    "Nazi Joon": (123, "Bb", "minor", "high", "very", "shahrum-kashani/nazi-joon-I2rbgqWqoR"),
    "Vay Ke Che Halie": (139, "C", "major", "high", "very", "amir-tataloo/vay-ke-che-halie-gdrE1wd62M"),
    "Baz Mano Kashti": (122, "A", "minor", "high", "very", "morteza/baz-mano-kashti-b3cio"),
    "Engaar Na Engaar": (96, "C", "major", "high", "very", "mansour/engaar-na-engaar"),
    "Aroos-E-Mahtab": (148, "C", "major", "high", "very", "faramarz-assef/aroos-e-mahtab"),
    "Nastaran": (112, "Bb", "minor", "high", "very", "farshid-amin/nastaran"),
    "Dokhtare Irooni": (121, "Bb", "minor", "high", "very", "andy/dokhtare-irooni-eh4i4"),
    "Dokhtar Irooni": (125, "G", "minor", "high", "very", "mehran/doktar-irooni"),
    "Ba Cheshmat": (120, "B", "minor", "high", "very", "ali-danial/ba-cheshmat-MIbV9SkSoe"),
    "Del Beh Tou Bastam": (150, "D", "major", "average", "somewhat", "morteza/del-beh-tou-bastam"),
    "Dokhtare Abadan": (124, "Db", "major", "high", "very", "sharareh/dokhtare-abadan-n7cns"),
    "Ahoo": (120, "A", "minor", "high", "very", "morteza/ahoo-pkmqs"),
    "Mano Del": (125, "G", "minor", "high", "somewhat", "black-cats/mano-del"),
    "Babakaram": (142, "G", "major", "high", "very", "armin-nosrati/baba-karam"),
    "Doostet Daram": (120, "B", "minor", "high", "very", "davood-behboodi/doostet-daram"),
    "Haji 3 Hamoomi": (122, "D", "major", "average", "very", "faramarz-assef/haji-3-hamoomi-IJZkVDMjjR"),
    "Eshveh": (148, "Bb", "major", "high", "very", "bijan-mortazavi/eshveh-yu185"),
    "Asereje (Aftermix)": (128, "Gb", "major", "high", "very", "lautarogalarza-dj/asereje-aftermix-fpocg"),
    "Begriff Shuffle": (122, "G", "minor", "average", "very", "magua/begriff-shuffle-3CgDbRO_3p"),
}
NOTES = {"Dokhtare Abadan": "songbpm lists 3 versions: 2 in Db major, 1 in C major"}

for o in OTHER:
    v = SONGBPM.get(o["title"])
    if v:
        o.update(bpm=v[0], key_note=v[1], key_mode=v[2], energy_src=v[3], danceable=v[4],
                 bpm_source="https://songbpm.com/@" + v[5])
    if o["title"] in NOTES:
        o["notes"] = NOTES[o["title"]]

PENDING = []
