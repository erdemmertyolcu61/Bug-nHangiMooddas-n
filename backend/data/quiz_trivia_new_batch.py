"""
SineQuiz — Yeni soru paketi: seri (127), komedi (110), animasyon (107) = 344 soru.
"""

NEW_TRIVIA_QUESTIONS = [
    # ═══════════════════════════════════════════════════════════════════════
    # SERİ FİLMLER — 127 soru
    # ═══════════════════════════════════════════════════════════════════════

    # --- James Bond (15) ---
    {"question": "İlk James Bond filminde Bond'u kim canlandırmıştır?", "correct": "Sean Connery", "wrong": ["Roger Moore", "George Lazenby", "Timothy Dalton"], "category": "seri", "movie": "Dr. No"},
    {"question": "James Bond serisinde 007'nin kod adını taşıyan ajanın içki tercihi nedir?", "correct": "Vodka Martini", "wrong": ["Viski", "Şampanya", "Gin Tonic"], "category": "seri", "movie": "James Bond"},
    {"question": "GoldenEye filminde Bond'u canlandıran aktör kimdir?", "correct": "Pierce Brosnan", "wrong": ["Timothy Dalton", "Daniel Craig", "Roger Moore"], "category": "seri", "movie": "GoldenEye"},
    {"question": "James Bond'un ünlü sipariş cümlesi 'Martini'mi nasıl isterim' sorusuna verdiği cevap nedir?", "correct": "Karıştırılmış değil, çalkalanmış", "wrong": ["Buzlu ve limonlu", "Zeytinli ve soğuk", "Sade ve kuru"], "category": "seri", "movie": "James Bond"},
    {"question": "Casino Royale (2006) filminde Bond'u kim canlandırır?", "correct": "Daniel Craig", "wrong": ["Pierce Brosnan", "Sean Connery", "Timothy Dalton"], "category": "seri", "movie": "Casino Royale"},
    {"question": "James Bond filmlerinde Q karakterinin görevi nedir?", "correct": "Bond'a teknolojik cihazlar sağlamak", "wrong": ["Bond'un koruması olmak", "Düşman ajanları sorgulamak", "MI6'ın başkanı olmak"], "category": "seri", "movie": "James Bond"},
    {"question": "James Bond serisinde MI6'ın başındaki kişi hangi harfle anılır?", "correct": "M", "wrong": ["Q", "N", "C"], "category": "seri", "movie": "James Bond"},
    {"question": "Skyfall filminde Bond'un çocukluk evi hangi ülkededir?", "correct": "İskoçya", "wrong": ["İngiltere", "İrlanda", "Galler"], "category": "seri", "movie": "Skyfall"},
    {"question": "James Bond serisinde Jaws karakterinin özelliği nedir?", "correct": "Çelik dişleri vardır", "wrong": ["Dev boyludur ve tek gözlüdür", "Metal kolları vardır", "Zırhlı bir yelekleri vardır"], "category": "seri", "movie": "The Spy Who Loved Me"},
    {"question": "Moonraker filminde Bond hangi ortamda savaşır?", "correct": "Uzayda", "wrong": ["Denizaltında", "Çölde", "Kutuplarda"], "category": "seri", "movie": "Moonraker"},
    {"question": "Roger Moore kaç James Bond filminde rol almıştır?", "correct": "7", "wrong": ["5", "6", "8"], "category": "seri", "movie": "James Bond"},
    {"question": "No Time to Die hangi Bond aktörünün son filmidir?", "correct": "Daniel Craig", "wrong": ["Pierce Brosnan", "Roger Moore", "Timothy Dalton"], "category": "seri", "movie": "No Time to Die"},
    {"question": "James Bond'un sekreterinin adı nedir?", "correct": "Miss Moneypenny", "wrong": ["Miss Marple", "Miss Scarlet", "Miss Hudson"], "category": "seri", "movie": "James Bond"},
    {"question": "Goldfinger filminde kötü karakterin altını nasıl ele geçirme planı vardır?", "correct": "Fort Knox'u radyoaktif hale getirmek", "wrong": ["Fort Knox'u soymak", "Altın fiyatlarını düşürmek", "Sahte altın basmak"], "category": "seri", "movie": "Goldfinger"},
    {"question": "James Bond'un favori araba markası hangisidir?", "correct": "Aston Martin", "wrong": ["Bentley", "Jaguar", "Rolls-Royce"], "category": "seri", "movie": "James Bond"},

    # --- Bourne serisi (5) ---
    {"question": "Jason Bourne karakterini hangi aktör canlandırır?", "correct": "Matt Damon", "wrong": ["Jeremy Renner", "Chris Pine", "Brad Pitt"], "category": "seri", "movie": "The Bourne Identity"},
    {"question": "Bourne serisinde Jason Bourne'un bağlı olduğu gizli CIA programının adı nedir?", "correct": "Treadstone", "wrong": ["Blackbriar", "Outcome", "Hydra"], "category": "seri", "movie": "The Bourne Identity"},
    {"question": "The Bourne Ultimatum filminde Bourne'un gerçek adının ne olduğu ortaya çıkar?", "correct": "David Webb", "wrong": ["Jason Carter", "Michael Kane", "Daniel Cross"], "category": "seri", "movie": "The Bourne Ultimatum"},
    {"question": "Bourne serisinin ilk filminde Bourne hangi denizde bulunur?", "correct": "Akdeniz", "wrong": ["Atlas Okyanusu", "Karadeniz", "Kuzey Denizi"], "category": "seri", "movie": "The Bourne Identity"},
    {"question": "The Bourne Supremacy filminde Bourne hangi şehirde araba kovalamacası yapar?", "correct": "Moskova", "wrong": ["Paris", "Berlin", "Londra"], "category": "seri", "movie": "The Bourne Supremacy"},

    # --- Ocean's serisi (5) ---
    {"question": "Ocean's Eleven filminde Danny Ocean'ı kim canlandırır?", "correct": "George Clooney", "wrong": ["Brad Pitt", "Matt Damon", "Andy Garcia"], "category": "seri", "movie": "Ocean's Eleven"},
    {"question": "Ocean's Eleven'da ekip kaç kişiden oluşur?", "correct": "11", "wrong": ["10", "12", "13"], "category": "seri", "movie": "Ocean's Eleven"},
    {"question": "Ocean's Eleven filminde soyulan yer neresidir?", "correct": "Las Vegas kumarhaneleri", "wrong": ["New York bankası", "Londra müzesi", "Paris mücevhercisi"], "category": "seri", "movie": "Ocean's Eleven"},
    {"question": "Ocean's 8 filminde Debbie Ocean'ı kim canlandırır?", "correct": "Sandra Bullock", "wrong": ["Cate Blanchett", "Anne Hathaway", "Rihanna"], "category": "seri", "movie": "Ocean's 8"},
    {"question": "Ocean's serisinde Brad Pitt'in canlandırdığı karakterin adı nedir?", "correct": "Rusty Ryan", "wrong": ["Linus Caldwell", "Basher Tarr", "Reuben Tishkoff"], "category": "seri", "movie": "Ocean's Eleven"},

    # --- Mad Max serisi (5) ---
    {"question": "Mad Max: Fury Road filminde Furiosa'yı kim canlandırır?", "correct": "Charlize Theron", "wrong": ["Gal Gadot", "Scarlett Johansson", "Emily Blunt"], "category": "seri", "movie": "Mad Max: Fury Road"},
    {"question": "Mad Max: Fury Road'da kötü karakterin adı nedir?", "correct": "Immortan Joe", "wrong": ["Lord Humungus", "Toecutter", "Aunty Entity"], "category": "seri", "movie": "Mad Max: Fury Road"},
    {"question": "Orijinal Mad Max filminde Max'i kim canlandırır?", "correct": "Mel Gibson", "wrong": ["Tom Hardy", "Russell Crowe", "Kurt Russell"], "category": "seri", "movie": "Mad Max"},
    {"question": "Mad Max: Fury Road'da savaş araçlarının üzerinde gitar çalan karakter ne yapar?", "correct": "Alev püskürten gitar çalar", "wrong": ["Davul çalar", "Boru çalar", "Keman çalar"], "category": "seri", "movie": "Mad Max: Fury Road"},
    {"question": "Mad Max: Fury Road filminde Furiosa nereye ulaşmaya çalışır?", "correct": "Yeşil Topraklar", "wrong": ["Bartertown", "Bullet Farm", "Gas Town"], "category": "seri", "movie": "Mad Max: Fury Road"},

    # --- Die Hard serisi (5) ---
    {"question": "Die Hard filmlerinde John McClane'i kim canlandırır?", "correct": "Bruce Willis", "wrong": ["Sylvester Stallone", "Arnold Schwarzenegger", "Harrison Ford"], "category": "seri", "movie": "Die Hard"},
    {"question": "İlk Die Hard filminde olaylar hangi binada geçer?", "correct": "Nakatomi Plaza", "wrong": ["Empire State", "Chrysler Building", "World Trade Center"], "category": "seri", "movie": "Die Hard"},
    {"question": "Die Hard filminde ana kötü karakter Hans Gruber'ı kim canlandırır?", "correct": "Alan Rickman", "wrong": ["Jeremy Irons", "Gary Oldman", "Ralph Fiennes"], "category": "seri", "movie": "Die Hard"},
    {"question": "Die Hard filmi hangi tatil döneminde geçer?", "correct": "Noel / Yılbaşı", "wrong": ["Cadılar Bayramı", "Şükran Günü", "Yeni Yıl"], "category": "seri", "movie": "Die Hard"},
    {"question": "John McClane'in ünlü sözü 'Yippee-ki-yay' nasıl devam eder?", "correct": "Motherf***er", "wrong": ["Partner", "Cowboy", "Brother"], "category": "seri", "movie": "Die Hard"},

    # --- Rambo (3) ---
    {"question": "Rambo karakterini hangi aktör canlandırır?", "correct": "Sylvester Stallone", "wrong": ["Arnold Schwarzenegger", "Bruce Willis", "Chuck Norris"], "category": "seri", "movie": "Rambo"},
    {"question": "İlk Rambo filminin orijinal adı nedir?", "correct": "First Blood", "wrong": ["Rambo: The Beginning", "Last Stand", "Blood Sport"], "category": "seri", "movie": "First Blood"},
    {"question": "Rambo hangi savaşın gazisidir?", "correct": "Vietnam Savaşı", "wrong": ["Kore Savaşı", "Irak Savaşı", "II. Dünya Savaşı"], "category": "seri", "movie": "Rambo"},

    # --- Lethal Weapon (3) ---
    {"question": "Lethal Weapon filmlerinde Martin Riggs'i kim canlandırır?", "correct": "Mel Gibson", "wrong": ["Bruce Willis", "Eddie Murphy", "Kurt Russell"], "category": "seri", "movie": "Lethal Weapon"},
    {"question": "Lethal Weapon'da Riggs'in partneri Roger Murtaugh'u kim canlandırır?", "correct": "Danny Glover", "wrong": ["Samuel L. Jackson", "Morgan Freeman", "Wesley Snipes"], "category": "seri", "movie": "Lethal Weapon"},
    {"question": "Lethal Weapon serisinde Murtaugh'un ünlü sözü nedir?", "correct": "Bu iş için çok yaşlandım", "wrong": ["Bir kez daha sahaya", "Son görev", "Emeklilik yaklaşıyor"], "category": "seri", "movie": "Lethal Weapon"},

    # --- Beverly Hills Cop (3) ---
    {"question": "Beverly Hills Cop filmlerinde Axel Foley'i kim canlandırır?", "correct": "Eddie Murphy", "wrong": ["Chris Rock", "Will Smith", "Martin Lawrence"], "category": "seri", "movie": "Beverly Hills Cop"},
    {"question": "Beverly Hills Cop'ta Axel Foley hangi şehirden gelir?", "correct": "Detroit", "wrong": ["New York", "Chicago", "Philadelphia"], "category": "seri", "movie": "Beverly Hills Cop"},
    {"question": "Beverly Hills Cop filminin ikonik tema müziği hangi sanatçıya aittir?", "correct": "Harold Faltermeyer", "wrong": ["Giorgio Moroder", "Jan Hammer", "Vangelis"], "category": "seri", "movie": "Beverly Hills Cop"},

    # --- Men in Black (5) ---
    {"question": "Men in Black filmlerinde Agent J'yi kim canlandırır?", "correct": "Will Smith", "wrong": ["Martin Lawrence", "Chris Tucker", "Jamie Foxx"], "category": "seri", "movie": "Men in Black"},
    {"question": "Men in Black'te Agent K'yı kim canlandırır?", "correct": "Tommy Lee Jones", "wrong": ["Clint Eastwood", "Harrison Ford", "Robert De Niro"], "category": "seri", "movie": "Men in Black"},
    {"question": "Men in Black filmlerinde hafızayı silen cihazın adı nedir?", "correct": "Nöralyzer", "wrong": ["Hafıza Silici", "Beyin Flaşı", "Amneziyatör"], "category": "seri", "movie": "Men in Black"},
    {"question": "Men in Black'te uzaylıların Dünya'daki varlığını gizleyen örgütün tam adı nedir?", "correct": "Men in Black", "wrong": ["Area 51", "X-Files Birimi", "Cosmic Guard"], "category": "seri", "movie": "Men in Black"},
    {"question": "Men in Black filminde Frank adlı konuşan köpeğin aslında ne olduğu ortaya çıkar?", "correct": "Uzaylı", "wrong": ["Robot", "Mutant", "Zaman yolcusu"], "category": "seri", "movie": "Men in Black"},

    # --- Ghostbusters (4) ---
    {"question": "Ghostbusters filminde hayaletleri yakalamak için kullanılan silahın adı nedir?", "correct": "Proton Pack (Proton Sırt Çantası)", "wrong": ["Ghost Blaster", "Ecto Gun", "Plasma Tüfeği"], "category": "seri", "movie": "Ghostbusters"},
    {"question": "Ghostbusters filminde şehri tehdit eden dev marshmallow yaratığın adı nedir?", "correct": "Stay Puft Marshmallow Man", "wrong": ["Gozer", "Zuul", "Slimer"], "category": "seri", "movie": "Ghostbusters"},
    {"question": "Ghostbusters filminde yeşil obur hayaletin takma adı nedir?", "correct": "Slimer", "wrong": ["Casper", "Blobby", "Gooey"], "category": "seri", "movie": "Ghostbusters"},
    {"question": "Ghostbusters'ın ünlü tema şarkısını kim seslendirmiştir?", "correct": "Ray Parker Jr.", "wrong": ["Michael Jackson", "Prince", "Huey Lewis"], "category": "seri", "movie": "Ghostbusters"},

    # --- Alien serisi (5) ---
    {"question": "Alien serisinde Ellen Ripley'i kim canlandırır?", "correct": "Sigourney Weaver", "wrong": ["Jamie Lee Curtis", "Linda Hamilton", "Jodie Foster"], "category": "seri", "movie": "Alien"},
    {"question": "Aliens (1986) filminin yönetmeni kimdir?", "correct": "James Cameron", "wrong": ["Ridley Scott", "David Fincher", "Steven Spielberg"], "category": "seri", "movie": "Aliens"},
    {"question": "Alien filminde mürettebatın gemisinin bilgisayarının adı nedir?", "correct": "Mother (MU-TH-UR)", "wrong": ["Father", "HAL", "GERTY"], "category": "seri", "movie": "Alien"},
    {"question": "Alien serisinde Xenomorph'un kanı hangi özelliğe sahiptir?", "correct": "Asidiktir ve metal eritir", "wrong": ["Zehirli gaz çıkarır", "Dondurucu soğuktur", "Patlayıcıdır"], "category": "seri", "movie": "Alien"},
    {"question": "Prometheus filminde insanlığı yaratan uzaylı ırka ne ad verilir?", "correct": "Engineers (Mühendisler)", "wrong": ["Predators", "Elders", "Creators"], "category": "seri", "movie": "Prometheus"},

    # --- Predator (3) ---
    {"question": "İlk Predator filminde Dutch karakterini kim canlandırır?", "correct": "Arnold Schwarzenegger", "wrong": ["Sylvester Stallone", "Bruce Willis", "Jean-Claude Van Damme"], "category": "seri", "movie": "Predator"},
    {"question": "Predator filminde uzaylı avcının görünmezlik yeteneğinin adı nedir?", "correct": "Optik kamuflaj (Cloaking)", "wrong": ["Hologram kalkan", "Gölge formu", "Işık sapması"], "category": "seri", "movie": "Predator"},
    {"question": "Prey (2022) filminde Predator hangi dönemde avlanır?", "correct": "18. yüzyıl Kuzey Amerika'sı", "wrong": ["Orta Çağ Avrupa'sı", "Antik Mısır", "Feodal Japonya"], "category": "seri", "movie": "Prey"},

    # --- Scream (5) ---
    {"question": "Scream filmlerinde katilin taktığı maskenin adı nedir?", "correct": "Ghostface", "wrong": ["Phantom", "Deathface", "Shadowmask"], "category": "seri", "movie": "Scream"},
    {"question": "Scream filmlerinde Sidney Prescott'u kim canlandırır?", "correct": "Neve Campbell", "wrong": ["Sarah Michelle Gellar", "Jennifer Love Hewitt", "Drew Barrymore"], "category": "seri", "movie": "Scream"},
    {"question": "Scream serisinin yönetmeni kimdir?", "correct": "Wes Craven", "wrong": ["John Carpenter", "Tobe Hooper", "Sam Raimi"], "category": "seri", "movie": "Scream"},
    {"question": "İlk Scream filminde katilin kurbanlarına sorduğu ünlü soru nedir?", "correct": "En sevdiğin korku filmi hangisi?", "wrong": ["Ölmekten korkuyor musun?", "Kapı kilitli mi?", "Yalnız mısın?"], "category": "seri", "movie": "Scream"},
    {"question": "Scream filminde Drew Barrymore'un canlandırdığı karakter filmin hangi bölümünde ölür?", "correct": "Açılış sahnesinde", "wrong": ["Finalde", "Filmin ortasında", "Son 10 dakikada"], "category": "seri", "movie": "Scream"},

    # --- Saw (3) ---
    {"question": "Saw filmlerinde oyun kuran ana kötü karakterin adı nedir?", "correct": "Jigsaw (John Kramer)", "wrong": ["Leatherface", "Pinhead", "Ghostface"], "category": "seri", "movie": "Saw"},
    {"question": "Saw filminde Jigsaw'ın kukla maskotunun adı nedir?", "correct": "Billy", "wrong": ["Chucky", "Annabelle", "Puppet"], "category": "seri", "movie": "Saw"},
    {"question": "İlk Saw filminde iki adam nerede uyanır?", "correct": "Bir banyoda zincirlenmiş halde", "wrong": ["Bir kafeste", "Bir bodrumda", "Bir hastanede"], "category": "seri", "movie": "Saw"},

    # --- The Conjuring Universe (5) ---
    {"question": "The Conjuring filmlerinde Ed ve Lorraine Warren çiftini kimler canlandırır?", "correct": "Patrick Wilson ve Vera Farmiga", "wrong": ["Ryan Reynolds ve Blake Lively", "Bradley Cooper ve Jennifer Lawrence", "Matthew McConaughey ve Anne Hathaway"], "category": "seri", "movie": "The Conjuring"},
    {"question": "The Conjuring evreninde lanetli bebeğin adı nedir?", "correct": "Annabelle", "wrong": ["Chucky", "Tiffany", "Brahms"], "category": "seri", "movie": "Annabelle"},
    {"question": "The Conjuring 2 filminde Warren çifti hangi ülkeye gider?", "correct": "İngiltere", "wrong": ["Fransa", "İtalya", "Almanya"], "category": "seri", "movie": "The Conjuring 2"},
    {"question": "Annabelle gerçekte ne tür bir bebekir?", "correct": "Raggedy Ann bez bebek", "wrong": ["Porselen bebek", "Tahta kukla", "Plastik oyuncak"], "category": "seri", "movie": "Annabelle"},
    {"question": "The Conjuring evreninde rahibe şeytanın adı nedir?", "correct": "Valak", "wrong": ["Bathsheba", "Azazel", "Pazuzu"], "category": "seri", "movie": "The Nun"},

    # --- National Treasure (3) ---
    {"question": "National Treasure filmlerinde Ben Gates'i kim canlandırır?", "correct": "Nicolas Cage", "wrong": ["Harrison Ford", "Tom Hanks", "Matt Damon"], "category": "seri", "movie": "National Treasure"},
    {"question": "National Treasure filminde Ben Gates hangi belgeyi çalar?", "correct": "Bağımsızlık Bildirgesi", "wrong": ["Anayasa", "Magna Carta", "Gettysburg Nutku"], "category": "seri", "movie": "National Treasure"},
    {"question": "National Treasure: Book of Secrets'ta ipuçları hangi başkanın masasında bulunur?", "correct": "Resolute Masası", "wrong": ["Oval Ofis Masası", "Lincoln Masası", "Washington Masası"], "category": "seri", "movie": "National Treasure: Book of Secrets"},

    # --- Night at the Museum (3) ---
    {"question": "Night at the Museum filmlerinde Larry Daley'i kim canlandırır?", "correct": "Ben Stiller", "wrong": ["Adam Sandler", "Jim Carrey", "Will Ferrell"], "category": "seri", "movie": "Night at the Museum"},
    {"question": "Night at the Museum'da müze sergilerini canlandıran tabletin adı nedir?", "correct": "Ahkmenrah Tableti", "wrong": ["Anubis Tableti", "Ra Madalyonu", "Osiris Tableti"], "category": "seri", "movie": "Night at the Museum"},
    {"question": "Night at the Museum filminde Robin Williams hangi tarihi figürü canlandırır?", "correct": "Theodore Roosevelt", "wrong": ["Abraham Lincoln", "George Washington", "Benjamin Franklin"], "category": "seri", "movie": "Night at the Museum"},

    # --- Twilight (5) ---
    {"question": "Twilight serisinde Bella Swan'ı kim canlandırır?", "correct": "Kristen Stewart", "wrong": ["Emma Watson", "Amanda Seyfried", "Anna Kendrick"], "category": "seri", "movie": "Twilight"},
    {"question": "Twilight'ta Edward Cullen'ı kim canlandırır?", "correct": "Robert Pattinson", "wrong": ["Taylor Lautner", "Kellan Lutz", "Jackson Rathbone"], "category": "seri", "movie": "Twilight"},
    {"question": "Twilight serisinde Jacob Black hangi yaratığa dönüşür?", "correct": "Kurt adam", "wrong": ["Vampir", "Yarı-elf", "Şekil değiştiren"], "category": "seri", "movie": "Twilight"},
    {"question": "Twilight serisinde Cullen ailesinin yaşadığı şehir hangisidir?", "correct": "Forks", "wrong": ["Seattle", "Portland", "Salem"], "category": "seri", "movie": "Twilight"},
    {"question": "Twilight'ta vampirlerin güneş ışığına çıkınca ne olur?", "correct": "Derileri parıldar/ışıldar", "wrong": ["Yanarlar", "Görünmez olurlar", "Güçleri artar"], "category": "seri", "movie": "Twilight"},

    # --- Bad Boys (3) ---
    {"question": "Bad Boys filmlerinde Mike Lowrey'i kim canlandırır?", "correct": "Will Smith", "wrong": ["Martin Lawrence", "Eddie Murphy", "Wesley Snipes"], "category": "seri", "movie": "Bad Boys"},
    {"question": "Bad Boys filmlerinde Marcus Burnett'ı kim canlandırır?", "correct": "Martin Lawrence", "wrong": ["Will Smith", "Jamie Foxx", "Chris Tucker"], "category": "seri", "movie": "Bad Boys"},
    {"question": "Bad Boys for Life filminde Mike ve Marcus hangi şehirde görev yapar?", "correct": "Miami", "wrong": ["Los Angeles", "New York", "Atlanta"], "category": "seri", "movie": "Bad Boys for Life"},

    # --- Rush Hour (3) ---
    {"question": "Rush Hour filmlerinde Dedektif Carter'ı kim canlandırır?", "correct": "Chris Tucker", "wrong": ["Eddie Murphy", "Kevin Hart", "Will Smith"], "category": "seri", "movie": "Rush Hour"},
    {"question": "Rush Hour filmlerinde Lee'yi kim canlandırır?", "correct": "Jackie Chan", "wrong": ["Jet Li", "Donnie Yen", "Tony Jaa"], "category": "seri", "movie": "Rush Hour"},
    {"question": "Rush Hour 2 filminde olaylar hangi şehirde geçer?", "correct": "Hong Kong", "wrong": ["Tokyo", "Pekin", "Singapur"], "category": "seri", "movie": "Rush Hour 2"},

    # --- Expendables (3) ---
    {"question": "The Expendables serisinin yönetmeni ve başrol oyuncusu kimdir?", "correct": "Sylvester Stallone", "wrong": ["Arnold Schwarzenegger", "Bruce Willis", "Jason Statham"], "category": "seri", "movie": "The Expendables"},
    {"question": "The Expendables serisinde Jason Statham'ın canlandırdığı karakterin adı nedir?", "correct": "Lee Christmas", "wrong": ["Barney Ross", "Toll Road", "Gunner Jensen"], "category": "seri", "movie": "The Expendables"},
    {"question": "The Expendables 2'de kötü karakteri kim canlandırır?", "correct": "Jean-Claude Van Damme", "wrong": ["Dolph Lundgren", "Chuck Norris", "Steven Seagal"], "category": "seri", "movie": "The Expendables 2"},

    # --- The Hunger Games (5) ---
    {"question": "Hunger Games'te Katniss Everdeen'i kim canlandırır?", "correct": "Jennifer Lawrence", "wrong": ["Shailene Woodley", "Emma Stone", "Brie Larson"], "category": "seri", "movie": "The Hunger Games"},
    {"question": "Hunger Games'te Katniss'in kullandığı silah nedir?", "correct": "Ok ve yay", "wrong": ["Kılıç", "Bıçak", "Mızrak"], "category": "seri", "movie": "The Hunger Games"},
    {"question": "Hunger Games'te başkent Panem'in yönetim merkezi neresidir?", "correct": "Capitol", "wrong": ["District 1", "The Hub", "Central City"], "category": "seri", "movie": "The Hunger Games"},
    {"question": "Hunger Games'te Peeta Mellark'ı kim canlandırır?", "correct": "Josh Hutcherson", "wrong": ["Liam Hemsworth", "Sam Claflin", "Alexander Ludwig"], "category": "seri", "movie": "The Hunger Games"},
    {"question": "Hunger Games serisinde diktatör Başkan Snow'u kim canlandırır?", "correct": "Donald Sutherland", "wrong": ["Philip Seymour Hoffman", "Woody Harrelson", "Stanley Tucci"], "category": "seri", "movie": "The Hunger Games"},

    # --- Maze Runner (3) ---
    {"question": "Maze Runner filmlerinde Thomas'ı kim canlandırır?", "correct": "Dylan O'Brien", "wrong": ["Ansel Elgort", "Thomas Brodie-Sangster", "Ki Hong Lee"], "category": "seri", "movie": "Maze Runner"},
    {"question": "Maze Runner'da labirentin içindeki yaratıkların adı nedir?", "correct": "Grievers (Acı Verenler)", "wrong": ["Cranks", "Walkers", "Scorchers"], "category": "seri", "movie": "Maze Runner"},
    {"question": "Maze Runner serisinde labirenti kontrol eden örgütün adı nedir?", "correct": "WCKD", "wrong": ["SHIELD", "HYDRA", "ADVENT"], "category": "seri", "movie": "Maze Runner"},

    # --- Final Destination (3) ---
    {"question": "Final Destination serisinde karakterler neyden kaçmaya çalışır?", "correct": "Ölümün kendisinden", "wrong": ["Bir katilden", "Bir lanetden", "Bir hastalıktan"], "category": "seri", "movie": "Final Destination"},
    {"question": "İlk Final Destination filminde ana karakter hangi felaketten kurtulur?", "correct": "Uçak kazası", "wrong": ["Tren kazası", "Otobüs kazası", "Gemi kazası"], "category": "seri", "movie": "Final Destination"},
    {"question": "Final Destination serisinin temel konsepti nedir?", "correct": "Ölümün sırası değiştirilemez", "wrong": ["Zaman döngüsü", "Paralel evren", "Lanetli nesne"], "category": "seri", "movie": "Final Destination"},

    # --- Harry Potter ek sorular (5) ---
    {"question": "Harry Potter'da Quidditch'te Golden Snitch'i yakalayan oyuncunun pozisyonu nedir?", "correct": "Seeker (Arayıcı)", "wrong": ["Chaser (Kovucu)", "Beater (Vurcu)", "Keeper (Kaleci)"], "category": "seri", "movie": "Harry Potter"},
    {"question": "Harry Potter'da Voldemort kaç Hortkuluk (Horcrux) yaratmıştır?", "correct": "7", "wrong": ["5", "6", "8"], "category": "seri", "movie": "Harry Potter"},
    {"question": "Harry Potter'da 'Expelliarmus' büyüsü ne işe yarar?", "correct": "Rakibin asasını elinden fırlatır", "wrong": ["Kalkan oluşturur", "Işık saçar", "Düşmanı savurur"], "category": "seri", "movie": "Harry Potter"},
    {"question": "Harry Potter'da Patronus büyüsünün formülü nedir?", "correct": "Expecto Patronum", "wrong": ["Lumos Maxima", "Protego Totalum", "Riddikulus"], "category": "seri", "movie": "Harry Potter"},
    {"question": "Harry Potter'da Hogwarts Ekspres'i hangi perondan kalkar?", "correct": "9 3/4", "wrong": ["7 1/2", "10 1/4", "8 3/4"], "category": "seri", "movie": "Harry Potter"},

    # --- Star Wars ek sorular (5) ---
    {"question": "Star Wars'ta Yoda'nın ışın kılıcının rengi nedir?", "correct": "Yeşil", "wrong": ["Mavi", "Mor", "Sarı"], "category": "seri", "movie": "Star Wars"},
    {"question": "Star Wars'ta Darth Vader'ın ışın kılıcının rengi nedir?", "correct": "Kırmızı", "wrong": ["Mor", "Turuncu", "Siyah"], "category": "seri", "movie": "Star Wars"},
    {"question": "Star Wars'ta Wookiee'lerin ana gezegeni hangisidir?", "correct": "Kashyyyk", "wrong": ["Endor", "Dagobah", "Naboo"], "category": "seri", "movie": "Star Wars"},
    {"question": "Star Wars'ta Han Solo'nun yardımcı pilotu kimdir?", "correct": "Chewbacca", "wrong": ["Lando Calrissian", "Nien Nunb", "R2-D2"], "category": "seri", "movie": "Star Wars"},
    {"question": "Star Wars: Rogue One filminde çalınan planlar hangi silaha aittir?", "correct": "Ölüm Yıldızı (Death Star)", "wrong": ["Starkiller Üssü", "AT-AT Walker", "Star Destroyer"], "category": "seri", "movie": "Rogue One"},

    # ═══════════════════════════════════════════════════════════════════════
    # KOMEDİ — 110 soru
    # ═══════════════════════════════════════════════════════════════════════

    # --- Jim Carrey: Ace Ventura (3) ---
    {"question": "Ace Ventura: Pet Detective filminde Ace'in mesleği nedir?", "correct": "Hayvan dedektifi", "wrong": ["Veteriner", "Hayvan bakıcısı", "Hayvanat bahçesi müdürü"], "category": "komedi", "movie": "Ace Ventura: Pet Detective"},
    {"question": "Ace Ventura filminde kaybolan maskot hayvan nedir?", "correct": "Yunus", "wrong": ["Papağan", "Maymun", "Köpek"], "category": "komedi", "movie": "Ace Ventura: Pet Detective"},
    {"question": "Ace Ventura: When Nature Calls filminde olaylar hangi kıtada geçer?", "correct": "Afrika", "wrong": ["Güney Amerika", "Asya", "Avustralya"], "category": "komedi", "movie": "Ace Ventura: When Nature Calls"},

    # --- The Mask (3) ---
    {"question": "The Mask filminde Stanley Ipkiss'i kim canlandırır?", "correct": "Jim Carrey", "wrong": ["Adam Sandler", "Ben Stiller", "Mike Myers"], "category": "komedi", "movie": "The Mask"},
    {"question": "The Mask filminde maskenin hangi tanrıya ait olduğu söylenir?", "correct": "Loki", "wrong": ["Thor", "Odin", "Hermes"], "category": "komedi", "movie": "The Mask"},
    {"question": "The Mask filminde Tina Carlyle'ı kim canlandırır?", "correct": "Cameron Diaz", "wrong": ["Drew Barrymore", "Jennifer Aniston", "Renée Zellweger"], "category": "komedi", "movie": "The Mask"},

    # --- Liar Liar (3) ---
    {"question": "Liar Liar filminde Fletcher Reede neden yalan söyleyemez?", "correct": "Oğlunun doğum günü dileği yüzünden", "wrong": ["Büyülü bir yüzük takar", "Bir lanet yüzünden", "Hipnoz edilmiştir"], "category": "komedi", "movie": "Liar Liar"},
    {"question": "Liar Liar'da Fletcher Reede'in mesleği nedir?", "correct": "Avukat", "wrong": ["Doktor", "Politikacı", "Emlakçı"], "category": "komedi", "movie": "Liar Liar"},
    {"question": "Liar Liar filminde Jim Carrey'nin canlandırdığı karakter kaç saat yalan söyleyemez?", "correct": "24 saat", "wrong": ["12 saat", "48 saat", "1 hafta"], "category": "komedi", "movie": "Liar Liar"},

    # --- Bruce Almighty (3) ---
    {"question": "Bruce Almighty filminde Bruce'a tanrısal güçleri kim verir?", "correct": "Tanrı (Morgan Freeman)", "wrong": ["Bir melek", "Bir cin", "Bir büyücü"], "category": "komedi", "movie": "Bruce Almighty"},
    {"question": "Bruce Almighty'de Bruce'un mesleği nedir?", "correct": "TV muhabiri", "wrong": ["Gazeteci", "Radyo sunucusu", "Film yapımcısı"], "category": "komedi", "movie": "Bruce Almighty"},
    {"question": "Bruce Almighty filminde Bruce'un kız arkadaşını kim canlandırır?", "correct": "Jennifer Aniston", "wrong": ["Cameron Diaz", "Drew Barrymore", "Renée Zellweger"], "category": "komedi", "movie": "Bruce Almighty"},

    # --- Dumb and Dumber (3) ---
    {"question": "Dumb and Dumber filminde Jim Carrey hangi karakteri canlandırır?", "correct": "Lloyd Christmas", "wrong": ["Harry Dunne", "Sea Bass", "Joe Mentalino"], "category": "komedi", "movie": "Dumb and Dumber"},
    {"question": "Dumb and Dumber'da Harry Dunne'ı kim canlandırır?", "correct": "Jeff Daniels", "wrong": ["Owen Wilson", "Woody Harrelson", "Bill Murray"], "category": "komedi", "movie": "Dumb and Dumber"},
    {"question": "Dumb and Dumber filminde Lloyd ve Harry nereye yolculuk yapar?", "correct": "Aspen, Colorado", "wrong": ["Las Vegas", "Miami", "Hawaii"], "category": "komedi", "movie": "Dumb and Dumber"},

    # --- Mrs. Doubtfire (3) ---
    {"question": "Mrs. Doubtfire filminde Daniel Hillard'ı kim canlandırır?", "correct": "Robin Williams", "wrong": ["Jim Carrey", "Eddie Murphy", "Adam Sandler"], "category": "komedi", "movie": "Mrs. Doubtfire"},
    {"question": "Mrs. Doubtfire'da Daniel neden kadın kılığına girer?", "correct": "Çocuklarını görebilmek için", "wrong": ["Bir suçludan kaçmak için", "Bir bahis yüzünden", "Bir film rolü için"], "category": "komedi", "movie": "Mrs. Doubtfire"},
    {"question": "Mrs. Doubtfire filminde Daniel hangi rolde çocuklarına yaklaşır?", "correct": "Yaşlı İngiliz dadı", "wrong": ["Yaşlı İtalyan aşçı", "Yaşlı Alman öğretmen", "Yaşlı İskoç bahçıvan"], "category": "komedi", "movie": "Mrs. Doubtfire"},

    # --- Groundhog Day (3) ---
    {"question": "Groundhog Day filminde Phil Connors'ı kim canlandırır?", "correct": "Bill Murray", "wrong": ["Dan Aykroyd", "Chevy Chase", "Steve Martin"], "category": "komedi", "movie": "Groundhog Day"},
    {"question": "Groundhog Day'de Phil hangi günü tekrar tekrar yaşar?", "correct": "2 Şubat", "wrong": ["14 Şubat", "1 Nisan", "25 Aralık"], "category": "komedi", "movie": "Groundhog Day"},
    {"question": "Groundhog Day filminde olaylar hangi kasabada geçer?", "correct": "Punxsutawney", "wrong": ["Woodstock", "Springfield", "Greendale"], "category": "komedi", "movie": "Groundhog Day"},

    # --- Anchorman (3) ---
    {"question": "Anchorman filminde Ron Burgundy'yi kim canlandırır?", "correct": "Will Ferrell", "wrong": ["Steve Carell", "John C. Reilly", "Vince Vaughn"], "category": "komedi", "movie": "Anchorman"},
    {"question": "Anchorman'de Ron Burgundy'nin çalıştığı TV kanalı hangi şehirdedir?", "correct": "San Diego", "wrong": ["Los Angeles", "New York", "Chicago"], "category": "komedi", "movie": "Anchorman"},
    {"question": "Anchorman'de Ron Burgundy'nin ünlü sözü nedir?", "correct": "Stay classy, San Diego", "wrong": ["Good evening, America", "News flash, people", "Breaking news, folks"], "category": "komedi", "movie": "Anchorman"},

    # --- Step Brothers (3) ---
    {"question": "Step Brothers filminde Brennan Huff'ı kim canlandırır?", "correct": "Will Ferrell", "wrong": ["John C. Reilly", "Adam McKay", "Mark Wahlberg"], "category": "komedi", "movie": "Step Brothers"},
    {"question": "Step Brothers'da iki üvey kardeş kaç yaşında olmasına rağmen ailesiyle yaşar?", "correct": "Yaklaşık 40", "wrong": ["Yaklaşık 25", "Yaklaşık 30", "Yaklaşık 50"], "category": "komedi", "movie": "Step Brothers"},
    {"question": "Step Brothers filminde Brennan ve Dale hangi aktiviteyi birlikte yapmaya başlar?", "correct": "Müzik grubu kurarlar", "wrong": ["Spor salonuna giderler", "Restoran açarlar", "YouTube kanalı kurarlar"], "category": "komedi", "movie": "Step Brothers"},

    # --- Elf (3) ---
    {"question": "Elf filminde Buddy'yi kim canlandırır?", "correct": "Will Ferrell", "wrong": ["Jim Carrey", "Adam Sandler", "Ben Stiller"], "category": "komedi", "movie": "Elf"},
    {"question": "Elf filminde Buddy hangi şehre gelir?", "correct": "New York", "wrong": ["Chicago", "Los Angeles", "Boston"], "category": "komedi", "movie": "Elf"},
    {"question": "Elf filminde Buddy'nin en sevdiği yiyecek grubu nedir?", "correct": "Her şeye şeker ve şurup döker", "wrong": ["Pizza", "Hamburger", "Dondurma"], "category": "komedi", "movie": "Elf"},

    # --- Zoolander (3) ---
    {"question": "Zoolander filminde Derek Zoolander'ı kim canlandırır?", "correct": "Ben Stiller", "wrong": ["Owen Wilson", "Will Ferrell", "Vince Vaughn"], "category": "komedi", "movie": "Zoolander"},
    {"question": "Zoolander'da Derek'in ünlü bakışının adı nedir?", "correct": "Blue Steel", "wrong": ["Iron Gaze", "Silver Fox", "Golden Eye"], "category": "komedi", "movie": "Zoolander"},
    {"question": "Zoolander filminde Derek'in mesleği nedir?", "correct": "Erkek manken", "wrong": ["Aktör", "Şarkıcı", "Dansçı"], "category": "komedi", "movie": "Zoolander"},

    # --- Tropic Thunder (3) ---
    {"question": "Tropic Thunder filminde Tugg Speedman'ı kim canlandırır?", "correct": "Ben Stiller", "wrong": ["Jack Black", "Robert Downey Jr.", "Tom Cruise"], "category": "komedi", "movie": "Tropic Thunder"},
    {"question": "Tropic Thunder'da Robert Downey Jr. hangi tartışmalı rolüyle dikkat çeker?", "correct": "Avustralya'lı bir aktör olarak siyahi bir asker rolü yapar", "wrong": ["Kadın kılığına girer", "Çocuk rolü yapar", "Yaşlı bir adam rolü yapar"], "category": "komedi", "movie": "Tropic Thunder"},
    {"question": "Tropic Thunder filminde Tom Cruise hangi sürpriz rolde görünür?", "correct": "Les Grossman (yapımcı)", "wrong": ["Yönetmen", "General", "Muhabir"], "category": "komedi", "movie": "Tropic Thunder"},

    # --- Borat (3) ---
    {"question": "Borat filminde Borat karakterini kim canlandırır?", "correct": "Sacha Baron Cohen", "wrong": ["Ali G", "Bruno", "Ben Stiller"], "category": "komedi", "movie": "Borat"},
    {"question": "Borat hangi ülkeden geldiğini iddia eder?", "correct": "Kazakistan", "wrong": ["Özbekistan", "Türkmenistan", "Kırgızistan"], "category": "komedi", "movie": "Borat"},
    {"question": "Borat filminde Borat hangi ülkeye yolculuk yapar?", "correct": "Amerika Birleşik Devletleri", "wrong": ["İngiltere", "Fransa", "Almanya"], "category": "komedi", "movie": "Borat"},

    # --- Grand Budapest Hotel (3) ---
    {"question": "The Grand Budapest Hotel filminde M. Gustave'ı kim canlandırır?", "correct": "Ralph Fiennes", "wrong": ["Bill Murray", "Adrien Brody", "Willem Dafoe"], "category": "komedi", "movie": "The Grand Budapest Hotel"},
    {"question": "The Grand Budapest Hotel filminin yönetmeni kimdir?", "correct": "Wes Anderson", "wrong": ["Quentin Tarantino", "Coen Kardeşler", "Edgar Wright"], "category": "komedi", "movie": "The Grand Budapest Hotel"},
    {"question": "The Grand Budapest Hotel'de lobi çocuğu Zero'yu kim canlandırır?", "correct": "Tony Revolori", "wrong": ["Timothée Chalamet", "Tom Holland", "Ansel Elgort"], "category": "komedi", "movie": "The Grand Budapest Hotel"},

    # --- Napoleon Dynamite (3) ---
    {"question": "Napoleon Dynamite filminde Napoleon'ı kim canlandırır?", "correct": "Jon Heder", "wrong": ["Michael Cera", "Jesse Eisenberg", "Andy Samberg"], "category": "komedi", "movie": "Napoleon Dynamite"},
    {"question": "Napoleon Dynamite'ta Napoleon'ın en yakın arkadaşının adı nedir?", "correct": "Pedro", "wrong": ["Rico", "Kip", "Deb"], "category": "komedi", "movie": "Napoleon Dynamite"},
    {"question": "Napoleon Dynamite filminde Napoleon'ın finalinde yaptığı performans nedir?", "correct": "Dans gösterisi", "wrong": ["Şarkı söyler", "Konuşma yapar", "Sihirbazlık gösterisi"], "category": "komedi", "movie": "Napoleon Dynamite"},

    # --- The Big Lebowski (3) ---
    {"question": "The Big Lebowski'de 'The Dude' karakterini kim canlandırır?", "correct": "Jeff Bridges", "wrong": ["John Goodman", "Steve Buscemi", "Philip Seymour Hoffman"], "category": "komedi", "movie": "The Big Lebowski"},
    {"question": "The Big Lebowski'de Dude'un en sevdiği içecek nedir?", "correct": "White Russian", "wrong": ["Bira", "Viski", "Margarita"], "category": "komedi", "movie": "The Big Lebowski"},
    {"question": "The Big Lebowski filminin yönetmenleri kimlerdir?", "correct": "Coen Kardeşler", "wrong": ["Wachowski Kardeşler", "Farrelly Kardeşler", "Russo Kardeşler"], "category": "komedi", "movie": "The Big Lebowski"},

    # --- Monty Python and the Holy Grail (3) ---
    {"question": "Monty Python and the Holy Grail filminde şövalyeler ne ararlar?", "correct": "Kutsal Kase (Holy Grail)", "wrong": ["Excalibur kılıcı", "Kutsal Mızrak", "Altın Kalkan"], "category": "komedi", "movie": "Monty Python and the Holy Grail"},
    {"question": "Monty Python and the Holy Grail'de Kara Şövalye kolları kesilince ne der?", "correct": "Bu sadece bir çizik!", "wrong": ["Pes etmiyorum!", "Henüz bitmedi!", "Geri döneceğim!"], "category": "komedi", "movie": "Monty Python and the Holy Grail"},
    {"question": "Monty Python and the Holy Grail'de katil tavşanı yenmek için ne kullanılır?", "correct": "Antakya'nın Kutsal El Bombası", "wrong": ["Büyülü bir kılıç", "Ateşli ok", "Kutsal su"], "category": "komedi", "movie": "Monty Python and the Holy Grail"},

    # --- Life of Brian (2) ---
    {"question": "Life of Brian filminde Brian'ı kim canlandırır?", "correct": "Graham Chapman", "wrong": ["John Cleese", "Michael Palin", "Terry Gilliam"], "category": "komedi", "movie": "Life of Brian"},
    {"question": "Life of Brian'ın ünlü final şarkısı hangisidir?", "correct": "Always Look on the Bright Side of Life", "wrong": ["Bohemian Rhapsody", "Don't Stop Me Now", "Another One Bites the Dust"], "category": "komedi", "movie": "Life of Brian"},

    # --- Airplane! (3) ---
    {"question": "Airplane! filminde Ted Striker'ı kim canlandırır?", "correct": "Robert Hays", "wrong": ["Leslie Nielsen", "Peter Graves", "Lloyd Bridges"], "category": "komedi", "movie": "Airplane!"},
    {"question": "Airplane! filminde 'Shirley deme bana' repliğini söyleyen karakter kimdir?", "correct": "Dr. Rumack (Leslie Nielsen)", "wrong": ["Ted Striker", "Kaptan Oveur", "Steve McCroskey"], "category": "komedi", "movie": "Airplane!"},
    {"question": "Airplane! filminde uçağı kimin indirmesi gerekir?", "correct": "Eski bir savaş pilotu olan yolcu", "wrong": ["Hostes", "Bir doktor", "Otomatik pilot"], "category": "komedi", "movie": "Airplane!"},

    # --- The Naked Gun (3) ---
    {"question": "The Naked Gun filmlerinde Frank Drebin'i kim canlandırır?", "correct": "Leslie Nielsen", "wrong": ["Steve Martin", "Chevy Chase", "Bill Murray"], "category": "komedi", "movie": "The Naked Gun"},
    {"question": "The Naked Gun'da Frank Drebin'in mesleği nedir?", "correct": "Polis dedektifi", "wrong": ["FBI ajanı", "Özel dedektif", "Güvenlik müdürü"], "category": "komedi", "movie": "The Naked Gun"},
    {"question": "The Naked Gun filminde Frank Drebin hangi takımın maçını korumak zorundadır?", "correct": "Beyzbol maçı", "wrong": ["Basketbol maçı", "Amerikan futbolu maçı", "Boks maçı"], "category": "komedi", "movie": "The Naked Gun"},

    # --- Coming to America (3) ---
    {"question": "Coming to America filminde Prens Akeem'i kim canlandırır?", "correct": "Eddie Murphy", "wrong": ["Chris Rock", "Will Smith", "Martin Lawrence"], "category": "komedi", "movie": "Coming to America"},
    {"question": "Coming to America'da Prens Akeem hangi hayali Afrika ülkesinden gelir?", "correct": "Zamunda", "wrong": ["Wakanda", "Genovia", "Sokovia"], "category": "komedi", "movie": "Coming to America"},
    {"question": "Coming to America'da Akeem eş bulmak için hangi şehre gider?", "correct": "Queens, New York", "wrong": ["Brooklyn, New York", "Harlem, New York", "Bronx, New York"], "category": "komedi", "movie": "Coming to America"},

    # --- Trading Places (3) ---
    {"question": "Trading Places filminde Billy Ray Valentine'i kim canlandırır?", "correct": "Eddie Murphy", "wrong": ["Richard Pryor", "Chris Tucker", "Samuel L. Jackson"], "category": "komedi", "movie": "Trading Places"},
    {"question": "Trading Places'te Louis Winthorpe III'ü kim canlandırır?", "correct": "Dan Aykroyd", "wrong": ["Chevy Chase", "Bill Murray", "Steve Martin"], "category": "komedi", "movie": "Trading Places"},
    {"question": "Trading Places filminde Duke kardeşler hangi sektörde çalışır?", "correct": "Borsa / Emtia ticareti", "wrong": ["Emlak", "Bankacılık", "Petrol"], "category": "komedi", "movie": "Trading Places"},

    # --- Bridesmaids (3) ---
    {"question": "Bridesmaids filminde Annie Walker'ı kim canlandırır?", "correct": "Kristen Wiig", "wrong": ["Melissa McCarthy", "Rose Byrne", "Maya Rudolph"], "category": "komedi", "movie": "Bridesmaids"},
    {"question": "Bridesmaids filminde gelinin adı nedir?", "correct": "Lillian", "wrong": ["Annie", "Helen", "Megan"], "category": "komedi", "movie": "Bridesmaids"},
    {"question": "Bridesmaids'te ünlü yemek zehirlenmesi sahnesi nerede geçer?", "correct": "Gelinlik mağazasında", "wrong": ["Restoranda", "Uçakta", "Otelde"], "category": "komedi", "movie": "Bridesmaids"},

    # --- Pitch Perfect (3) ---
    {"question": "Pitch Perfect filminde Beca'yı kim canlandırır?", "correct": "Anna Kendrick", "wrong": ["Rebel Wilson", "Anna Camp", "Brittany Snow"], "category": "komedi", "movie": "Pitch Perfect"},
    {"question": "Pitch Perfect'te Beca'nın katıldığı a cappella grubunun adı nedir?", "correct": "Barden Bellas", "wrong": ["Treblemakers", "High Notes", "Tone Hangers"], "category": "komedi", "movie": "Pitch Perfect"},
    {"question": "Pitch Perfect'te Fat Amy karakterini kim canlandırır?", "correct": "Rebel Wilson", "wrong": ["Melissa McCarthy", "Anna Kendrick", "Elizabeth Banks"], "category": "komedi", "movie": "Pitch Perfect"},

    # --- 21 Jump Street (3) ---
    {"question": "21 Jump Street filminde Schmidt'i kim canlandırır?", "correct": "Jonah Hill", "wrong": ["Channing Tatum", "Dave Franco", "Ice Cube"], "category": "komedi", "movie": "21 Jump Street"},
    {"question": "21 Jump Street'te iki polis memuru nereye gizli ajan olarak girer?", "correct": "Liseye", "wrong": ["Üniversiteye", "Hapisaneye", "Askeri üsse"], "category": "komedi", "movie": "21 Jump Street"},
    {"question": "21 Jump Street filminde Jenko'yu kim canlandırır?", "correct": "Channing Tatum", "wrong": ["Jonah Hill", "Dave Franco", "Rob Riggle"], "category": "komedi", "movie": "21 Jump Street"},

    # --- We're the Millers (3) ---
    {"question": "We're the Millers filminde David Clark'ı kim canlandırır?", "correct": "Jason Sudeikis", "wrong": ["Will Poulter", "Ed Helms", "Jason Bateman"], "category": "komedi", "movie": "We're the Millers"},
    {"question": "We're the Millers'da sahte ailenin sınırdan geçirmeye çalıştığı şey nedir?", "correct": "Uyuşturucu", "wrong": ["Silah", "Sahte para", "Çalıntı mücevher"], "category": "komedi", "movie": "We're the Millers"},
    {"question": "We're the Millers'da sahte anneyi kim canlandırır?", "correct": "Jennifer Aniston", "wrong": ["Emma Roberts", "Sandra Bullock", "Cameron Diaz"], "category": "komedi", "movie": "We're the Millers"},

    # --- Scary Movie (3) ---
    {"question": "Scary Movie serisinde Cindy Campbell'ı kim canlandırır?", "correct": "Anna Faris", "wrong": ["Sarah Michelle Gellar", "Neve Campbell", "Shannon Elizabeth"], "category": "komedi", "movie": "Scary Movie"},
    {"question": "Scary Movie filmleri başka filmlerin ne türüdür?", "correct": "Parodi (Komik taklidi)", "wrong": ["Remake (Yeniden çevrimi)", "Devam filmi", "Prequel"], "category": "komedi", "movie": "Scary Movie"},
    {"question": "İlk Scary Movie filmi hangi korku filminin parodisidir?", "correct": "Scream", "wrong": ["Halloween", "Friday the 13th", "A Nightmare on Elm Street"], "category": "komedi", "movie": "Scary Movie"},

    # --- White Chicks (3) ---
    {"question": "White Chicks filminde Wayans kardeşler ne kılığına girer?", "correct": "Sarışın beyaz kadın", "wrong": ["Yaşlı erkek", "Çocuk", "Rock yıldızı"], "category": "komedi", "movie": "White Chicks"},
    {"question": "White Chicks filminde Marcus ve Kevin'ın mesleği nedir?", "correct": "FBI ajanı", "wrong": ["Polis", "Özel dedektif", "CIA ajanı"], "category": "komedi", "movie": "White Chicks"},
    {"question": "White Chicks filminde olaylar hangi lüks tatil beldesinde geçer?", "correct": "Hamptons", "wrong": ["Beverly Hills", "Malibu", "Miami Beach"], "category": "komedi", "movie": "White Chicks"},

    # --- Deadpool (5) ---
    {"question": "Deadpool filmlerinde Wade Wilson'ı kim canlandırır?", "correct": "Ryan Reynolds", "wrong": ["Chris Pratt", "Ryan Gosling", "Chris Evans"], "category": "komedi", "movie": "Deadpool"},
    {"question": "Deadpool'un süper gücü nedir?", "correct": "Hızlı iyileşme (Rejenerasyon)", "wrong": ["Süper güç", "Uçabilme", "Görünmezlik"], "category": "komedi", "movie": "Deadpool"},
    {"question": "Deadpool filmlerinde dördüncü duvarı kırmak ne demektir?", "correct": "Seyirciye doğrudan konuşmak", "wrong": ["Duvardan geçmek", "Sahneyi yıkmak", "Kamera açısını değiştirmek"], "category": "komedi", "movie": "Deadpool"},
    {"question": "Deadpool 2'de Cable karakterini kim canlandırır?", "correct": "Josh Brolin", "wrong": ["Terry Crews", "Zazie Beetz", "Julian Dennison"], "category": "komedi", "movie": "Deadpool 2"},
    {"question": "Deadpool'un sevgilisinin adı nedir?", "correct": "Vanessa", "wrong": ["Jessica", "Karen", "Domino"], "category": "komedi", "movie": "Deadpool"},

    # --- Knives Out (3) ---
    {"question": "Knives Out filminde Dedektif Blanc'ı kim canlandırır?", "correct": "Daniel Craig", "wrong": ["Chris Evans", "Michael Shannon", "Lakeith Stanfield"], "category": "komedi", "movie": "Knives Out"},
    {"question": "Knives Out filminde öldürülen aile reisinin mesleği nedir?", "correct": "Gizemli roman yazarı", "wrong": ["Profesör", "Avukat", "İş insanı"], "category": "komedi", "movie": "Knives Out"},
    {"question": "Knives Out filminde Marta'nın yalan söylediğinde ne olur?", "correct": "Kusar", "wrong": ["Kızarır", "Hıçkırık tutar", "Gözleri sulanır"], "category": "komedi", "movie": "Knives Out"},

    # --- The Nice Guys (3) ---
    {"question": "The Nice Guys filminde Holland March'ı kim canlandırır?", "correct": "Ryan Gosling", "wrong": ["Russell Crowe", "Matt Damon", "Brad Pitt"], "category": "komedi", "movie": "The Nice Guys"},
    {"question": "The Nice Guys filminde Jackson Healy'yi kim canlandırır?", "correct": "Russell Crowe", "wrong": ["Ryan Gosling", "Mark Wahlberg", "Tom Hardy"], "category": "komedi", "movie": "The Nice Guys"},
    {"question": "The Nice Guys filminde olaylar hangi on yılda geçer?", "correct": "1970'ler", "wrong": ["1960'lar", "1980'ler", "1990'lar"], "category": "komedi", "movie": "The Nice Guys"},

    # --- Game Night (3) ---
    {"question": "Game Night filminde Max'i kim canlandırır?", "correct": "Jason Bateman", "wrong": ["Jason Sudeikis", "Will Arnett", "Ed Helms"], "category": "komedi", "movie": "Game Night"},
    {"question": "Game Night'ta oyun gecesi hangi gerçek olaya dönüşür?", "correct": "Gerçek bir adam kaçırma olayına", "wrong": ["Soygun planına", "Cinayet soruşturmasına", "Casusluk operasyonuna"], "category": "komedi", "movie": "Game Night"},
    {"question": "Game Night filminde Annie'yi kim canlandırır?", "correct": "Rachel McAdams", "wrong": ["Isla Fisher", "Rose Byrne", "Tina Fey"], "category": "komedi", "movie": "Game Night"},

    # --- Ted (3) ---
    {"question": "Ted filminde Ted'in sesini kim seslendirmiştir?", "correct": "Seth MacFarlane", "wrong": ["Mark Wahlberg", "Mila Kunis", "Joel McHale"], "category": "komedi", "movie": "Ted"},
    {"question": "Ted filminde Ted aslında nedir?", "correct": "Canlanan bir oyuncak ayı", "wrong": ["Bir robot", "Bir uzaylı", "Hologram"], "category": "komedi", "movie": "Ted"},
    {"question": "Ted filminde John Bennett'ı kim canlandırır?", "correct": "Mark Wahlberg", "wrong": ["Seth Rogen", "Jonah Hill", "James Franco"], "category": "komedi", "movie": "Ted"},

    # --- Neighbors (3) ---
    {"question": "Neighbors filminde Mac Radner'ı kim canlandırır?", "correct": "Seth Rogen", "wrong": ["Zac Efron", "Dave Franco", "James Franco"], "category": "komedi", "movie": "Neighbors"},
    {"question": "Neighbors filminde aile hangi komşuyla savaşır?", "correct": "Öğrenci kardeşlik evi (Fraternity)", "wrong": ["Rock grubu", "Parti organizatörü", "Gece kulübü sahibi"], "category": "komedi", "movie": "Neighbors"},
    {"question": "Neighbors'da Teddy Sanders'ı kim canlandırır?", "correct": "Zac Efron", "wrong": ["Seth Rogen", "Dave Franco", "Christopher Mintz-Plasse"], "category": "komedi", "movie": "Neighbors"},

    # --- Juno (3) ---
    {"question": "Juno filminde Juno MacGuff'ı kim canlandırır?", "correct": "Ellen Page (Elliot Page)", "wrong": ["Michael Cera", "Jennifer Garner", "Olivia Thirlby"], "category": "komedi", "movie": "Juno"},
    {"question": "Juno filminin ana konusu nedir?", "correct": "Lise öğrencisinin hamileliği ve evlat edinme süreci", "wrong": ["Üniversiteye kabul hikayesi", "İlk aşk hikayesi", "Müzik grubu kurma hayali"], "category": "komedi", "movie": "Juno"},
    {"question": "Juno filminde Juno'nun bebeğini evlat edinecek çiftten kadını kim canlandırır?", "correct": "Jennifer Garner", "wrong": ["Sandra Bullock", "Drew Barrymore", "Reese Witherspoon"], "category": "komedi", "movie": "Juno"},

    # --- Superbad ekstra (3) ---
    {"question": "Superbad filminde McLovin'ı kim canlandırır?", "correct": "Christopher Mintz-Plasse", "wrong": ["Jonah Hill", "Michael Cera", "Seth Rogen"], "category": "komedi", "movie": "Superbad"},
    {"question": "Superbad'de McLovin'ın sahte kimliğindeki adı nedir?", "correct": "McLovin", "wrong": ["Mohammed", "Chang", "O'Brien"], "category": "komedi", "movie": "Superbad"},
    {"question": "Superbad filminde Seth'i kim canlandırır?", "correct": "Jonah Hill", "wrong": ["Michael Cera", "Christopher Mintz-Plasse", "Bill Hader"], "category": "komedi", "movie": "Superbad"},

    # ═══════════════════════════════════════════════════════════════════════
    # ANİMASYON — 107 soru
    # ═══════════════════════════════════════════════════════════════════════

    # --- The Lion King (5) ---
    {"question": "Aslan Kral filminde Simba'nın babası kimdir?", "correct": "Mufasa", "wrong": ["Scar", "Zazu", "Rafiki"], "category": "animasyon", "movie": "The Lion King"},
    {"question": "Aslan Kral'da Simba'nın amcası Scar ne yapar?", "correct": "Mufasa'yı öldürür", "wrong": ["Simba'yı sürgün eder", "Tahtı terk eder", "Hyena'larla savaşır"], "category": "animasyon", "movie": "The Lion King"},
    {"question": "Aslan Kral'da 'Hakuna Matata' ne anlama gelir?", "correct": "Sorun yok / Dert etme", "wrong": ["Güçlü ol", "Özgür ol", "Hayatı sev"], "category": "animasyon", "movie": "The Lion King"},
    {"question": "Aslan Kral'da Simba'nın çocukluk arkadaşının adı nedir?", "correct": "Nala", "wrong": ["Sarabi", "Kiara", "Vitani"], "category": "animasyon", "movie": "The Lion King"},
    {"question": "Aslan Kral'da Simba'yı büyüten ikili kimlerdir?", "correct": "Timon ve Pumbaa", "wrong": ["Zazu ve Rafiki", "Shenzi ve Banzai", "Ed ve Scar"], "category": "animasyon", "movie": "The Lion King"},

    # --- Aladdin (3) ---
    {"question": "Aladdin filminde Cin'in yaşadığı nesne nedir?", "correct": "Sihirli lamba", "wrong": ["Sihirli halı", "Sihirli yüzük", "Sihirli kutu"], "category": "animasyon", "movie": "Aladdin"},
    {"question": "Aladdin filminde prensesin adı nedir?", "correct": "Yasemin (Jasmine)", "wrong": ["Ariel", "Belle", "Aurora"], "category": "animasyon", "movie": "Aladdin"},
    {"question": "Aladdin filminde kötü vezirin adı nedir?", "correct": "Jafar", "wrong": ["Hades", "Gaston", "Scar"], "category": "animasyon", "movie": "Aladdin"},

    # --- Beauty and the Beast (3) ---
    {"question": "Güzel ve Çirkin filminde Belle'in babası neyle uğraşır?", "correct": "Mucit / İcatçı", "wrong": ["Kütüphaneci", "Çiftçi", "Tüccar"], "category": "animasyon", "movie": "Beauty and the Beast"},
    {"question": "Güzel ve Çirkin'de Canavar'ın hizmetçisi olan saatin adı nedir?", "correct": "Cogsworth", "wrong": ["Lumiere", "Chip", "Mrs. Potts"], "category": "animasyon", "movie": "Beauty and the Beast"},
    {"question": "Güzel ve Çirkin'de kasaba yakışıklısının adı nedir?", "correct": "Gaston", "wrong": ["LeFou", "Maurice", "Philippe"], "category": "animasyon", "movie": "Beauty and the Beast"},

    # --- The Little Mermaid (3) ---
    {"question": "Küçük Deniz Kızı filminde Ariel'in babası kimdir?", "correct": "Kral Triton", "wrong": ["Poseidon", "Neptün", "Sebastian"], "category": "animasyon", "movie": "The Little Mermaid"},
    {"question": "Küçük Deniz Kızı'nda deniz cadısının adı nedir?", "correct": "Ursula", "wrong": ["Maleficent", "Cruella", "Morgana"], "category": "animasyon", "movie": "The Little Mermaid"},
    {"question": "Küçük Deniz Kızı'nda Ariel sesi karşılığında ne alır?", "correct": "İnsan bacakları", "wrong": ["Güzellik", "Ölümsüzlük", "Büyü gücü"], "category": "animasyon", "movie": "The Little Mermaid"},

    # --- Mulan (3) ---
    {"question": "Mulan filminde Mulan'ın küçük ejderha koruyucusunun adı nedir?", "correct": "Mushu", "wrong": ["Cri-Kee", "Khan", "Shan Yu"], "category": "animasyon", "movie": "Mulan"},
    {"question": "Mulan filminde Mulan neden erkek kılığına girer?", "correct": "Yaşlı babasının yerine savaşmak için", "wrong": ["Bir macera yaşamak için", "İmparatoru korumak için", "Onur kazanmak için"], "category": "animasyon", "movie": "Mulan"},
    {"question": "Mulan filminde düşman komutanın adı nedir?", "correct": "Shan Yu", "wrong": ["Li Shang", "Chi-Fu", "Yao"], "category": "animasyon", "movie": "Mulan"},

    # --- Cinderella (2) ---
    {"question": "Sindirella filminde sihir gece yarısı ne olur?", "correct": "Büyü bozulur", "wrong": ["Prens uyur", "Sindirella kaybolur", "Saray kapanır"], "category": "animasyon", "movie": "Cinderella"},
    {"question": "Sindirella'nın balodan kaçarken geride bıraktığı şey nedir?", "correct": "Cam ayakkabı", "wrong": ["Eldiven", "Taç", "Kolye"], "category": "animasyon", "movie": "Cinderella"},

    # --- The Jungle Book (2) ---
    {"question": "Orman Çocuğu filminde insan yavrusu Mowgli'yi kim büyütür?", "correct": "Kurtlar", "wrong": ["Maymunlar", "Filler", "Ayılar"], "category": "animasyon", "movie": "The Jungle Book"},
    {"question": "Orman Çocuğu'nda tembel ayının adı nedir?", "correct": "Baloo", "wrong": ["Bagheera", "Shere Khan", "King Louie"], "category": "animasyon", "movie": "The Jungle Book"},

    # --- 101 Dalmatians (2) ---
    {"question": "101 Dalmaçyalı filminde kötü kadının adı nedir?", "correct": "Cruella De Vil", "wrong": ["Maleficent", "Ursula", "Yzma"], "category": "animasyon", "movie": "101 Dalmatians"},
    {"question": "101 Dalmaçyalı'da Cruella köpekleri neden kaçırır?", "correct": "Kürk manto yapmak için", "wrong": ["Sirke satmak için", "Deney yapmak için", "Koleksiyon yapmak için"], "category": "animasyon", "movie": "101 Dalmatians"},

    # --- Bambi (2) ---
    {"question": "Bambi filminde Bambi'nin en iyi arkadaşı tavşanın adı nedir?", "correct": "Thumper", "wrong": ["Flower", "Faline", "Ronno"], "category": "animasyon", "movie": "Bambi"},
    {"question": "Bambi filminde Bambi büyüyünce ne olur?", "correct": "Ormanın Prensi olur", "wrong": ["Ormanı terk eder", "İnsanlarla yaşar", "Çoban olur"], "category": "animasyon", "movie": "Bambi"},

    # --- Dumbo (2) ---
    {"question": "Dumbo filminde Dumbo'nun özel yeteneği nedir?", "correct": "Kulaklarıyla uçabilir", "wrong": ["Konuşabilir", "Görünmez olabilir", "Hortumu ile ateş fışkırtır"], "category": "animasyon", "movie": "Dumbo"},
    {"question": "Dumbo filminde Dumbo'nun annesi neden kafese kapatılır?", "correct": "Yavrusunu korurken saldırgan davrandığı için", "wrong": ["Sirki terk ettiği için", "Gösteri yapmayı reddettiği için", "Diğer filleri korkuttuğu için"], "category": "animasyon", "movie": "Dumbo"},

    # --- Finding Nemo/Dory (5) ---
    {"question": "Kayıp Balık Nemo'da Nemo'nun babası kimdir?", "correct": "Marlin", "wrong": ["Gill", "Crush", "Bruce"], "category": "animasyon", "movie": "Finding Nemo"},
    {"question": "Kayıp Balık Nemo'da Dory'nin sorunu nedir?", "correct": "Kısa süreli hafıza kaybı", "wrong": ["Kör olması", "Konuşamaması", "Yüzememesi"], "category": "animasyon", "movie": "Finding Nemo"},
    {"question": "Kayıp Balık Nemo'da Nemo hangi şehrin denizinden yakalanır?", "correct": "Sydney", "wrong": ["Melbourne", "Brisbane", "Perth"], "category": "animasyon", "movie": "Finding Nemo"},
    {"question": "Finding Dory filminde Dory'nin ailesi nerededir?", "correct": "Deniz Biyolojisi Enstitüsü'nde", "wrong": ["Büyük Bariyer Resifi'nde", "Açık okyanusta", "Bir akvaryumda"], "category": "animasyon", "movie": "Finding Dory"},
    {"question": "Kayıp Balık Nemo'da köpekbalığı Bruce'un ünlü sözü nedir?", "correct": "Balıklar arkadaştır, yemek değil", "wrong": ["Okyanusun kralıyım", "Dişlerime güvenin", "Yüzmek özgürlüktür"], "category": "animasyon", "movie": "Finding Nemo"},

    # --- Monsters Inc (5) ---
    {"question": "Monsters Inc. filminde Sulley'nin tam adı nedir?", "correct": "James P. Sullivan", "wrong": ["John P. Sullivan", "Jack P. Sullivan", "Joseph P. Sullivan"], "category": "animasyon", "movie": "Monsters, Inc."},
    {"question": "Monsters Inc.'da enerji üretmek için ne kullanılır?", "correct": "Çocukların çığlıkları", "wrong": ["Çocukların gözyaşları", "Çocukların korkuları", "Çocukların rüyaları"], "category": "animasyon", "movie": "Monsters, Inc."},
    {"question": "Monsters Inc.'da Sulley'nin en iyi arkadaşı kimdir?", "correct": "Mike Wazowski", "wrong": ["Randall Boggs", "Roz", "Celia"], "category": "animasyon", "movie": "Monsters, Inc."},
    {"question": "Monsters Inc.'da insan çocuğunun takma adı nedir?", "correct": "Boo", "wrong": ["Goo", "Moo", "Doo"], "category": "animasyon", "movie": "Monsters, Inc."},
    {"question": "Monsters Inc. filminin sonunda enerji kaynağı ne olarak değişir?", "correct": "Çocukların kahkahaları", "wrong": ["Çocukların şarkıları", "Çocukların dansları", "Çocukların alkışları"], "category": "animasyon", "movie": "Monsters, Inc."},

    # --- The Incredibles (5) ---
    {"question": "İnanılmaz Aile filminde babanın süper kahraman adı nedir?", "correct": "Mr. Incredible", "wrong": ["Elastigirl", "Frozone", "Syndrome"], "category": "animasyon", "movie": "The Incredibles"},
    {"question": "İnanılmaz Aile'de annenin süper gücü nedir?", "correct": "Vücudunu esnetebilir", "wrong": ["Görünmez olabilir", "Süper hızlı koşabilir", "Ateş çıkarabilir"], "category": "animasyon", "movie": "The Incredibles"},
    {"question": "İnanılmaz Aile'de kötü karakterin adı nedir?", "correct": "Syndrome", "wrong": ["Underminer", "Screenslaver", "Bomb Voyage"], "category": "animasyon", "movie": "The Incredibles"},
    {"question": "İnanılmaz Aile'de Dash'in süper gücü nedir?", "correct": "Süper hız", "wrong": ["Süper güç", "Görünmezlik", "Uçabilme"], "category": "animasyon", "movie": "The Incredibles"},
    {"question": "İnanılmaz Aile'de Edna Mode ne tasarlar?", "correct": "Süper kahraman kostümleri", "wrong": ["Silahlar", "Araçlar", "Maskeler"], "category": "animasyon", "movie": "The Incredibles"},

    # --- Ratatouille (3) ---
    {"question": "Ratatouille filminde aşçılık yapan farenin adı nedir?", "correct": "Remy", "wrong": ["Emile", "Django", "Gusteau"], "category": "animasyon", "movie": "Ratatouille"},
    {"question": "Ratatouille filminde olaylar hangi şehirde geçer?", "correct": "Paris", "wrong": ["Roma", "Londra", "Madrid"], "category": "animasyon", "movie": "Ratatouille"},
    {"question": "Ratatouille'de korkulan yemek eleştirmeninin adı nedir?", "correct": "Anton Ego", "wrong": ["Auguste Gusteau", "Skinner", "Colette"], "category": "animasyon", "movie": "Ratatouille"},

    # --- WALL-E (3) ---
    {"question": "WALL-E filminde WALL-E'nin görevi nedir?", "correct": "Çöp toplamak ve sıkıştırmak", "wrong": ["Bitki yetiştirmek", "Bina inşa etmek", "Yol temizlemek"], "category": "animasyon", "movie": "WALL-E"},
    {"question": "WALL-E'de insanlar nerede yaşar?", "correct": "Uzaydaki dev bir gemide (Axiom)", "wrong": ["Yeraltı şehirlerinde", "Mars'ta", "Ay'da"], "category": "animasyon", "movie": "WALL-E"},
    {"question": "WALL-E'nin aşık olduğu robotun adı nedir?", "correct": "EVE", "wrong": ["AUTO", "M-O", "GO-4"], "category": "animasyon", "movie": "WALL-E"},

    # --- Up (3) ---
    {"question": "Yukarı Bak filminde Carl Fredricksen evi nasıl uçurur?", "correct": "Balonlarla", "wrong": ["Roketle", "Helikopterle", "Sihirle"], "category": "animasyon", "movie": "Up"},
    {"question": "Yukarı Bak filminde Carl nereye ulaşmaya çalışır?", "correct": "Cennet Şelalesi (Paradise Falls)", "wrong": ["Amazon Ormanı", "Niagara Şelalesi", "Angel Şelalesi"], "category": "animasyon", "movie": "Up"},
    {"question": "Yukarı Bak filminde Carl'ın yanında seyahat eden küçük izcinin adı nedir?", "correct": "Russell", "wrong": ["Kevin", "Dug", "Muntz"], "category": "animasyon", "movie": "Up"},

    # --- Brave (2) ---
    {"question": "Cesur filminde Merida hangi silahta ustadır?", "correct": "Ok ve yay", "wrong": ["Kılıç", "Mızrak", "Balta"], "category": "animasyon", "movie": "Brave"},
    {"question": "Cesur filminde Merida'nın annesi neye dönüşür?", "correct": "Ayıya", "wrong": ["Kurda", "Kartala", "Geyiğe"], "category": "animasyon", "movie": "Brave"},

    # --- Inside Out (5) ---
    {"question": "Ters Yüz filminde ana karakterin adı nedir?", "correct": "Riley", "wrong": ["Joy", "Sadness", "Emily"], "category": "animasyon", "movie": "Inside Out"},
    {"question": "Ters Yüz'de sarı renkteki duygu karakteri hangisidir?", "correct": "Neşe (Joy)", "wrong": ["Öfke (Anger)", "Tiksinme (Disgust)", "Korku (Fear)"], "category": "animasyon", "movie": "Inside Out"},
    {"question": "Ters Yüz'de Riley'nin hayali arkadaşının adı nedir?", "correct": "Bing Bong", "wrong": ["Rainbow", "Sparkle", "Dream Boy"], "category": "animasyon", "movie": "Inside Out"},
    {"question": "Ters Yüz filminde kaç temel duygu karakteri vardır?", "correct": "5", "wrong": ["4", "6", "7"], "category": "animasyon", "movie": "Inside Out"},
    {"question": "Inside Out 2'de Riley'nin zihnine eklenen yeni duygu hangisidir?", "correct": "Kaygı (Anxiety)", "wrong": ["Utanç (Shame)", "Kıskançlık (Envy)", "Can sıkıntısı (Boredom)"], "category": "animasyon", "movie": "Inside Out 2"},

    # --- Soul (3) ---
    {"question": "Soul filminde Joe Gardner'ın mesleği nedir?", "correct": "Müzik öğretmeni / Piyanist", "wrong": ["Ressam", "Dansçı", "Aktör"], "category": "animasyon", "movie": "Soul"},
    {"question": "Soul filminde ruhların dünyaya gelmeden önce bulunduğu yer nedir?", "correct": "Büyük Öncesi (The Great Before)", "wrong": ["Cennet", "Ruhlar Vadisi", "Başlangıç Noktası"], "category": "animasyon", "movie": "Soul"},
    {"question": "Soul filminde Joe'nun mentor olduğu ruhun numarası nedir?", "correct": "22", "wrong": ["11", "33", "44"], "category": "animasyon", "movie": "Soul"},

    # --- Luca (2) ---
    {"question": "Luca filminde Luca aslında ne tür bir yaratıktır?", "correct": "Deniz canavarı", "wrong": ["İnsan", "Balık adam", "Siren"], "category": "animasyon", "movie": "Luca"},
    {"question": "Luca filminde olaylar hangi ülkede geçer?", "correct": "İtalya", "wrong": ["Yunanistan", "İspanya", "Fransa"], "category": "animasyon", "movie": "Luca"},

    # --- Turning Red (2) ---
    {"question": "Kırmızıya Dönüş filminde Mei Lee heyecanlanınca neye dönüşür?", "correct": "Dev kırmızı pandaya", "wrong": ["Kırmızı ejderhaya", "Kırmızı kediye", "Kırmızı tilkiye"], "category": "animasyon", "movie": "Turning Red"},
    {"question": "Turning Red filminde Mei'nin en sevdiği müzik grubu hangisidir?", "correct": "4*Town", "wrong": ["5ive", "B4-4", "O-Town"], "category": "animasyon", "movie": "Turning Red"},

    # --- Elemental (2) ---
    {"question": "Elemental filminde Ember hangi elementtendir?", "correct": "Ateş", "wrong": ["Su", "Toprak", "Hava"], "category": "animasyon", "movie": "Elemental"},
    {"question": "Elemental filminde Wade hangi elementtendir?", "correct": "Su", "wrong": ["Ateş", "Toprak", "Hava"], "category": "animasyon", "movie": "Elemental"},

    # --- Frozen (5) ---
    {"question": "Karlar Ülkesi filminde Elsa'nın süper gücü nedir?", "correct": "Buz ve kar yaratabilme", "wrong": ["Uçabilme", "Görünmez olabilme", "Ateş çıkarabilme"], "category": "animasyon", "movie": "Frozen"},
    {"question": "Karlar Ülkesi'nde kardan adamın adı nedir?", "correct": "Olaf", "wrong": ["Sven", "Kristoff", "Hans"], "category": "animasyon", "movie": "Frozen"},
    {"question": "Karlar Ülkesi'nin ünlü şarkısı hangisidir?", "correct": "Let It Go", "wrong": ["Do You Want to Build a Snowman?", "Into the Unknown", "Show Yourself"], "category": "animasyon", "movie": "Frozen"},
    {"question": "Karlar Ülkesi'nde Elsa'nın kız kardeşinin adı nedir?", "correct": "Anna", "wrong": ["Rapunzel", "Moana", "Merida"], "category": "animasyon", "movie": "Frozen"},
    {"question": "Karlar Ülkesi'nde kötü adam olduğu ortaya çıkan prens kimdir?", "correct": "Hans", "wrong": ["Kristoff", "Olaf", "Sven"], "category": "animasyon", "movie": "Frozen"},

    # --- Moana (3) ---
    {"question": "Moana filminde yarı tanrı Maui'yi kim seslendirir?", "correct": "Dwayne Johnson", "wrong": ["Jason Momoa", "Chris Hemsworth", "Jack Black"], "category": "animasyon", "movie": "Moana"},
    {"question": "Moana filminde Moana'nın görevi nedir?", "correct": "Te Fiti'nin kalbini yerine koymak", "wrong": ["Yeni bir ada bulmak", "Deniz canavarını yenmek", "Kayıp hazineyi bulmak"], "category": "animasyon", "movie": "Moana"},
    {"question": "Moana filminde Maui'nin büyülü silahı nedir?", "correct": "Dev balık kancası", "wrong": ["Trident", "Büyülü mızrak", "Sihirli bumerang"], "category": "animasyon", "movie": "Moana"},

    # --- Encanto (3) ---
    {"question": "Encanto filminde Mirabel'in özel yanı nedir?", "correct": "Ailede sihirli gücü olmayan tek kişidir", "wrong": ["En güçlü sihre sahiptir", "Görünmez olabilir", "Hayvanlarla konuşabilir"], "category": "animasyon", "movie": "Encanto"},
    {"question": "Encanto filminde büyülü evin adı nedir?", "correct": "Casita", "wrong": ["La Casa", "Madrigal Evi", "Encanto Sarayı"], "category": "animasyon", "movie": "Encanto"},
    {"question": "Encanto'nun ünlü şarkısı 'We Don't Talk About ___' nasıl devam eder?", "correct": "Bruno", "wrong": ["Mirabel", "Abuela", "Luisa"], "category": "animasyon", "movie": "Encanto"},

    # --- Coco (5) ---
    {"question": "Coco filminde Miguel'in tutkusu nedir?", "correct": "Müzik", "wrong": ["Resim", "Dans", "Yemek"], "category": "animasyon", "movie": "Coco"},
    {"question": "Coco filminde ölüler diyarına giriş hangi gün olur?", "correct": "Ölüler Günü (Día de los Muertos)", "wrong": ["Cadılar Bayramı", "Yılbaşı", "Paskalya"], "category": "animasyon", "movie": "Coco"},
    {"question": "Coco filminde Miguel'in idol aldığı müzisyenin adı nedir?", "correct": "Ernesto de la Cruz", "wrong": ["Héctor Rivera", "Chicharrón", "Pepita"], "category": "animasyon", "movie": "Coco"},
    {"question": "Coco filminde ölülerin tamamen yok olması neye bağlıdır?", "correct": "Yaşayanlar tarafından unutulma", "wrong": ["İskeletlerinin kırılması", "Fotoğraflarının yakılması", "İsimlerinin silinmesi"], "category": "animasyon", "movie": "Coco"},
    {"question": "Coco filminin geçtiği ülke hangisidir?", "correct": "Meksika", "wrong": ["İspanya", "Kolombiya", "Küba"], "category": "animasyon", "movie": "Coco"},

    # --- Zootopia (5) ---
    {"question": "Zootopia filminde Judy Hopps'un mesleği nedir?", "correct": "Polis memuru", "wrong": ["Dedektif", "İtfaiyeci", "Doktor"], "category": "animasyon", "movie": "Zootopia"},
    {"question": "Zootopia'da Judy Hopps hangi hayvandır?", "correct": "Tavşan", "wrong": ["Fare", "Kedi", "Sincap"], "category": "animasyon", "movie": "Zootopia"},
    {"question": "Zootopia'da Nick Wilde hangi hayvandır?", "correct": "Tilki", "wrong": ["Kurt", "Çakal", "Rakun"], "category": "animasyon", "movie": "Zootopia"},
    {"question": "Zootopia'da Flash hangi hayvandır ve nerede çalışır?", "correct": "Tembel hayvan, motorlu araçlar dairesinde", "wrong": ["Çita, postanede", "Kaplumbağa, bankada", "Koala, kütüphanede"], "category": "animasyon", "movie": "Zootopia"},
    {"question": "Zootopia filminde hayvanları saldırgan yapan madde nedir?", "correct": "Gece Kükürten (Night Howler) çiçeği", "wrong": ["Zehirli su", "Kimyasal gaz", "Radyoaktif madde"], "category": "animasyon", "movie": "Zootopia"},

    # --- Tangled (3) ---
    {"question": "Karmakarışık filminde Rapunzel'in özel yeteneğinin kaynağı nedir?", "correct": "Uzun saçları", "wrong": ["Gözleri", "Gözyaşları", "Sesi"], "category": "animasyon", "movie": "Tangled"},
    {"question": "Karmakarışık'ta Rapunzel'i kulede tutan kişi kimdir?", "correct": "Mother Gothel", "wrong": ["Cadı", "Üvey anne", "Kötü kraliçe"], "category": "animasyon", "movie": "Tangled"},
    {"question": "Karmakarışık'ta hırsız erkek karakterin adı nedir?", "correct": "Flynn Rider (Eugene Fitzherbert)", "wrong": ["Jack Frost", "Prince Adam", "Kristoff"], "category": "animasyon", "movie": "Tangled"},

    # --- Wreck-It Ralph (3) ---
    {"question": "Oyunbozan Ralph filminde Ralph hangi oyunun kötü karakteridir?", "correct": "Fix-It Felix Jr.", "wrong": ["Sugar Rush", "Hero's Duty", "Pac-Man"], "category": "animasyon", "movie": "Wreck-It Ralph"},
    {"question": "Oyunbozan Ralph'te Vanellope hangi oyunda yarışır?", "correct": "Sugar Rush", "wrong": ["Mario Kart", "Candy Crush", "Pac-Man"], "category": "animasyon", "movie": "Wreck-It Ralph"},
    {"question": "Oyunbozan Ralph'te oyun karakterleri mesai sonrası nerede buluşur?", "correct": "Oyun Merkezi'ndeki elektrik kabloları / Prize bağlantısı", "wrong": ["Gizli bir odada", "İnternette", "Bulut sunucuda"], "category": "animasyon", "movie": "Wreck-It Ralph"},

    # --- Big Hero 6 (3) ---
    {"question": "6 Süper Kahraman filminde şişme robotun adı nedir?", "correct": "Baymax", "wrong": ["Hiro", "Wasabi", "GoGo"], "category": "animasyon", "movie": "Big Hero 6"},
    {"question": "Big Hero 6'da Baymax'ın asıl amacı nedir?", "correct": "Sağlık bakımı ve yardım robotu", "wrong": ["Savaş robotu", "Ev temizlik robotu", "Fabrika robotu"], "category": "animasyon", "movie": "Big Hero 6"},
    {"question": "Big Hero 6 filminde olaylar hangi hayali şehirde geçer?", "correct": "San Fransokyo", "wrong": ["Neo Tokyo", "New Shanghai", "Los Tokyoles"], "category": "animasyon", "movie": "Big Hero 6"},

    # --- Spirited Away (3) ---
    {"question": "Ruhların Kaçışı filminde Chihiro'nun banyo evinde çalışırken aldığı yeni ad nedir?", "correct": "Sen", "wrong": ["Chi", "Haku", "Yuki"], "category": "animasyon", "movie": "Spirited Away"},
    {"question": "Ruhların Kaçışı filminin yönetmeni kimdir?", "correct": "Hayao Miyazaki", "wrong": ["Isao Takahata", "Makoto Shinkai", "Mamoru Hosoda"], "category": "animasyon", "movie": "Spirited Away"},
    {"question": "Ruhların Kaçışı'nda banyo evini yöneten cadının adı nedir?", "correct": "Yubaba", "wrong": ["Zeniba", "Kamaji", "No-Face"], "category": "animasyon", "movie": "Spirited Away"},

    # --- My Neighbor Totoro (2) ---
    {"question": "Komşum Totoro filminde Totoro hangi tür yaratıktır?", "correct": "Orman ruhu", "wrong": ["Ayı", "Dev kedi", "Tanuki"], "category": "animasyon", "movie": "My Neighbor Totoro"},
    {"question": "Komşum Totoro'da kız kardeşlerin uçmak için bindikleri şey nedir?", "correct": "Kedi Otobüsü (Catbus)", "wrong": ["Uçan halı", "Dev kuş", "Bulut"], "category": "animasyon", "movie": "My Neighbor Totoro"},

    # --- Princess Mononoke (2) ---
    {"question": "Prenses Mononoke filminde San kimdir?", "correct": "Kurtlar tarafından büyütülmüş bir insan kızı", "wrong": ["Bir tanrıça", "Bir orman perisi", "Bir prenses"], "category": "animasyon", "movie": "Princess Mononoke"},
    {"question": "Prenses Mononoke'de Ashitaka'nın laneti nereden gelir?", "correct": "Lanetli bir yaban domuzundan", "wrong": ["Bir şeytandan", "Bir cadıdan", "Bir ejderhadan"], "category": "animasyon", "movie": "Princess Mononoke"},

    # --- Howl's Moving Castle (2) ---
    {"question": "Yürüyen Şato filminde Sophie hangi lanete uğrar?", "correct": "Yaşlı bir kadına dönüşür", "wrong": ["Taşa dönüşür", "Görünmez olur", "Sesini kaybeder"], "category": "animasyon", "movie": "Howl's Moving Castle"},
    {"question": "Yürüyen Şato filminde şatonun kalbini oluşturan ateş cinin adı nedir?", "correct": "Calcifer", "wrong": ["Turnip", "Markl", "Heen"], "category": "animasyon", "movie": "Howl's Moving Castle"},

    # --- Puss in Boots (3) ---
    {"question": "Çizmeli Kedi: Son Dilek filminde Puss in Boots kaç canı kalmıştır?", "correct": "Son canı (1)", "wrong": ["3 canı", "5 canı", "2 canı"], "category": "animasyon", "movie": "Puss in Boots: The Last Wish"},
    {"question": "Çizmeli Kedi filmlerinde Puss in Boots'un en yakın arkadaşı kimdir?", "correct": "Humpty Dumpty", "wrong": ["Shrek", "Eşek", "Kitty Softpaws"], "category": "animasyon", "movie": "Puss in Boots"},
    {"question": "Çizmeli Kedi: Son Dilek'te Ölüm karakteri hangi hayvan kılığındadır?", "correct": "Kurt", "wrong": ["Kartal", "Yılan", "Karga"], "category": "animasyon", "movie": "Puss in Boots: The Last Wish"},

    # --- The Boss Baby (2) ---
    {"question": "Patron Bebek filminde bebeğin özelliği nedir?", "correct": "Takım elbiseli bir iş insanı gibi davranır", "wrong": ["Süper güçleri vardır", "Uçabilir", "Görünmez olabilir"], "category": "animasyon", "movie": "The Boss Baby"},
    {"question": "Patron Bebek filminde Boss Baby'nin sesini kim seslendirmiştir?", "correct": "Alec Baldwin", "wrong": ["Seth Rogen", "Jack Black", "Steve Carell"], "category": "animasyon", "movie": "The Boss Baby"},
]
