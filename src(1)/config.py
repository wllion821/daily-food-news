"""
Configuration: verified scrapable sources only (tested 2026-04-16).
Only sources that returned >0 article links are included.
"""

SOURCES = {
    # Tier 1: 食品安全 (1 source verified)
    "foodmate": {
        "name": "食品伙伴网",
        "url": "https://news.foodmate.net/",
        "tier": 1,
        "article_pattern": r"/\d{4}/\d{2}/\d+\.html",
    },
    # Tier 2: 竞争对手 (4 sources verified)
    "jiemian": {
        "name": "界面新闻",
        "url": "https://www.jiemian.com/",
        "tier": 2,
        "article_pattern": r"/article/\d+\.html",
    },
    "yicai": {
        "name": "第一财经",
        "url": "https://www.yicai.com/",
        "tier": 2,
        "article_pattern": r"/news/\d+\.html",
    },
    "tmtpost": {
        "name": "钛媒体",
        "url": "https://www.tmtpost.com/",
        "tier": 3,
        "article_pattern": r"/\d+\.html",
    },
    "itbear": {
        "name": "ITBear",
        "url": "https://www.itbear.com.cn/",
        "tier": 3,
        "article_pattern": r"/html/\d{4}-\d{2}/\d+\.html",
    },
}

BRAND_KEYWORDS = {
    "宾堡/Bimbo": ["宾堡", "Grupo Bimbo", "Bimbo", "宾堡集团"],
    "桃李": ["桃李", "Taoli", "桃李面包"],
    "达利": ["达利", "Dali", "达利食品", "达利集团"],
    "盼盼": ["盼盼", "Panpan", "盼盼食品"],
    "义利": ["义利", "Yili", "义利食品"],
    "BreadTalk": ["BreadTalk", "面包新语"],
    "泸溪河": ["泸溪河", "泸溪河桃酥"],
    "幸福西饼": ["幸福西饼", "XFXB"],
    "墨茉点心局": ["墨茉", "Momo", "墨茉点心"],
}

SIGNAL_KEYWORDS = {
    "正向扩展": ["投资", "投产", "拓店", "扩张", "建厂", "融资", "上市", "合作", "新建", "开工"],
    "负向风险": ["召回", "下架", "抽检不合格", "处罚", "减持", "关店", "裁员", "亏损", "投诉", "曝光", "造假"],
    "产品创新": ["新品", "低GI", "健康化", "升级", "配方", "研发", "创新", "首发"],
    "市场动态": ["市场份额", "销量", "营收", "增长", "下降", "促销", "营销", "渠道", "门店"],
    "政策监管": ["市场监管总局", "食药监局", "抽检", "标准", "法规", "政策", "禁用", "超标", "监管", "许可"],
    "行业活动": ["春糖", "糖酒会", "博览会", "研讨会", "大会", "论坛", "报告", "发布", "峰会"],
}

CATEGORIES = [
    ("烘焙行业动态", "竞品扩张、投资、建厂"),
    ("产品与创新", "新品发布、配方升级、健康化"),
    ("渠道与市场", "渠道打法、营销策略、消费趋势"),
    ("食品安全监管", "政策、抽检、投诉、直播监管"),
    ("行业与展会", "大会、博览会、研讨会、报告"),
]

MAX_ITEMS_PER_COLUMN = 5
