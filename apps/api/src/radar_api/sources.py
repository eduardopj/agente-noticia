RSS_FEEDS = [
    # Brasil - tecnologia, mercado, ciencia aplicada e cultura digital.
    {
        "name": "Canaltech",
        "url": "https://canaltech.com.br/rss/",
        "type": "press_br",
        "category": "brasil_tecnologia",
    },
    {
        "name": "Tecnoblog",
        "url": "https://tecnoblog.net/feed/",
        "type": "press_br",
        "category": "brasil_tecnologia",
    },
    {
        "name": "Olhar Digital",
        "url": "https://olhardigital.com.br/feed/",
        "type": "press_br",
        "category": "brasil_tecnologia",
    },
    {
        "name": "TecMundo",
        "url": "https://news.google.com/rss/search?q=site%3Atecmundo.com.br%20tecnologia%20OR%20IA%20OR%20seguran%C3%A7a&hl=pt-BR&gl=BR&ceid=BR:pt-419",
        "type": "press_br",
        "category": "brasil_tecnologia",
    },
    {
        "name": "G1 Tecnologia",
        "url": "https://g1.globo.com/rss/g1/tecnologia/",
        "type": "press_br",
        "category": "brasil_tecnologia",
    },
    {
        "name": "Folha Tecnologia",
        "url": "https://feeds.folha.uol.com.br/tec/rss091.xml",
        "type": "press_br",
        "category": "brasil_tecnologia",
    },
    {
        "name": "Baguete",
        "url": "https://www.baguete.com.br/rss.xml",
        "type": "press_br",
        "category": "brasil_negocios_tech",
    },
    # Fontes primarias de IA e desenvolvimento.
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/news/rss.xml",
        "type": "primary",
        "category": "ia_global",
    },
    {
        "name": "Google DeepMind Blog",
        "url": "https://deepmind.google/blog/rss.xml",
        "type": "primary",
        "category": "ia_global",
    },
    {
        "name": "Google AI",
        "url": "https://blog.google/technology/ai/rss/",
        "type": "primary",
        "category": "ia_global",
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "type": "primary",
        "category": "open_source",
    },
    {
        "name": "GitHub Blog",
        "url": "https://github.blog/feed/",
        "type": "primary",
        "category": "devtools",
    },
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "type": "press",
        "category": "ia_global",
    },
    # Mundo - tecnologia, startups, devtools, chips, seguranca e ciencia aplicada.
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "type": "press",
        "category": "tecnologia_global",
    },
    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "type": "press",
        "category": "tecnologia_global",
    },
    {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "type": "press",
        "category": "tecnologia_global",
    },
    {
        "name": "Wired",
        "url": "https://www.wired.com/feed/rss",
        "type": "press",
        "category": "tecnologia_global",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "type": "press",
        "category": "ia_global",
    },
    {
        "name": "NVIDIA Blog",
        "url": "https://blogs.nvidia.com/feed/",
        "type": "primary",
        "category": "hardware_ia",
    },
    {
        "name": "BleepingComputer",
        "url": "https://www.bleepingcomputer.com/feed/",
        "type": "press",
        "category": "seguranca",
    },
    # YouTube via RSS oficial do YouTube.
    {
        "name": "YouTube - Codigo Fonte TV",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCFuIUoyHB12qpYa8Jpxoxow",
        "type": "video",
        "category": "video_brasil",
    },
    {
        "name": "YouTube - Gustavo Guanabara / Curso em Video",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCrWvhVmt0Qac3HgsjQK62FQ",
        "type": "video",
        "category": "video_brasil",
    },
    {
        "name": "YouTube - Fabio Akita",
        "youtube_handle": "Akitando",
        "type": "video",
        "category": "video_brasil",
    },
    {
        "name": "YouTube - Filipe Deschamps",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCU5JicSrEM5A63jkJ2QvGYw",
        "type": "video",
        "category": "video_brasil",
    },
    {
        "name": "YouTube - Mano Deyvin",
        "youtube_handle": "manodeyvin",
        "type": "video",
        "category": "video_brasil",
    },
    {
        "name": "YouTube - Fireship",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCsBjURrPoezykLs9EqgamOA",
        "type": "video",
        "category": "video_global",
    },
    {
        "name": "YouTube - Two Minute Papers",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCbfYPyITQ-7l4upoX8nvctg",
        "type": "video",
        "category": "video_global",
    },
    {
        "name": "YouTube - Google Developers",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC_x5XG1OV2P6uZZ5FSM9Ttw",
        "type": "video",
        "category": "video_global",
    },
]

ARXIV_QUERIES = [
    "cat:cs.AI",
    "cat:cs.LG",
    "cat:cs.CL",
    "cat:cs.CV",
    'all:"large language model"',
    'all:"AI agents"',
    'all:"neural networks"',
    'all:"machine learning"',
]

ACADEMIC_SEARCH_QUERIES = [
    "artificial intelligence",
    "machine learning",
    "large language models",
    "AI agents",
    "neural networks",
    "computer vision",
    "natural language processing",
    "software engineering AI",
    "cybersecurity artificial intelligence",
    "educational technology artificial intelligence",
]

ACADEMIC_PUBLISHERS = [
    "Association for Computing Machinery",
    "ACM",
    "IEEE",
    "Institute of Electrical and Electronics Engineers",
    "Springer Nature",
    "Elsevier",
    "AAAI",
    "MIT Press",
]

ACADEMIC_RSS_FEEDS = [
    {
        "name": "Communications of the ACM",
        "url": "https://cacm.acm.org/feed/",
        "type": "paper",
        "category": "academico",
    },
    {
        "name": "IEEE Spectrum",
        "url": "https://spectrum.ieee.org/feeds/feed.rss",
        "type": "academic_press",
        "category": "academico",
    },
    {
        "name": "Nature Machine Intelligence",
        "url": "https://www.nature.com/natmachintell.rss",
        "type": "paper",
        "category": "academico",
    },
    {
        "name": "Nature Technology",
        "url": "https://www.nature.com/subjects/technology.rss",
        "type": "paper",
        "category": "academico",
    },
    {
        "name": "MIT Press - Artificial Intelligence",
        "url": "https://direct.mit.edu/rss/site_1000041/1000059.xml",
        "type": "paper",
        "category": "academico",
    },
]
