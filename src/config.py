"""Configuration: sources, brand keywords, signal keywords, exclusion rules."""

SOURCES = {
    # Tier 1: 食品安全 (5 sources)
    "tier1_shibao": {
        "name": "食安观察网",
        "url": "https://www.shibao315.com/rss",
        "tier": 1,
    },
    "tier1_samr": {
        "name": "国家市场监督管理总局",
        "url": "http://www.samr.gov.cn/rss",
        "tier": 1,
    },
    "tier1_nicai": {
        "name": "中国食品安全网",
        "url": "http://www.caqs.gov.cn/rss",
        "tier": 1,
    },
    "tier1质检网": {
        "name": "质检网",
        "url": "http://www.zhijainet.com/rss",
        "tier": 1,
    },
    "tier1_food": {
        "name": "食品伙伴网",
        "url": "https://www.foodmate.net/rss",
        "tier": 1,
    },
    # Tier 2: 竞争对手 (6 sources)
    "tier2_bakery": {
        "name": "烘焙头条",
        "url": "https://www.bakery.com/rss",
        "tier": 2,
    },
    "tier2_taoli": {
        "name": "桃李面包",
        "url": "http://www.taoli-bread.com.cn/news/rss",
        "tier": 2,
    },
    "tier2_dali": {
        "name": "达利食品集团",
        "url": "http://www.dali-food.com/news/rss",
        "tier": 2,
    },
    "tier2_breadtalk": {
        "name": "BreadTalk",
        "url": "https://www.breadtalk.com/news/rss",
        "tier": 2,
    },
    "tier2_xfxb": {
        "name": "幸福西饼",
        "url": "http://www.xfxb.net/news/rss",
        "tier": 2,
    },
    "tier2_momo": {
        "name": "墨茉点心局",
        "url": "http://www.momo-dianxin.com/news/rss",
        "tier": 2,
    },
    # Tier 3: 行业横向 (5 sources)
    "tier3_industry": {
        "name": "食品行业网",
        "url": "https://www.foodindustry.com/news/rss",
        "tier": 3,
    },
    "tier3_cia": {
        "name": "中国食品工业协会",
        "url": "http://www.cia.org.cn/rss",
        "tier": 3,
    },
    "tier3_baking": {
        "name": "中国烘焙协会",
        "url": "http://www.bakingchina.org/news/rss",
        "tier": 3,
    },
    "tier3_retail": {
        "name": "新零售内参",
        "url": "https://www.newretail.cn/rss",
        "tier": 3,
    },
    "tier3_36kr": {
        "name": "36氪食品",
        "url": "https://36kr.com/feed/group/food",
        "tier": 3,
    },
}

# Brand keywords for filtering
BRAND_KEYWORDS = {
    "宾堡/Bimbo": ["宾堡", "Grupo Bimbo", "Bimbo"],
    "桃李": ["桃李", "Taoli"],
    "达利": ["达利", "Dali"],
    "盼盼": ["盼盼", "Panpan"],
    "义利": ["义利", "Yili"],
    "BreadTalk": ["BreadTalk", "面包新语"],
    "泸溪河": ["泸溪河"],
    "幸福西饼": ["幸福西饼", "XFXB"],
    "墨茉点心局": ["墨茉", "Momo"],
}

# Signal keywords: indicate news value
SIGNAL_KEYWORDS = {
    "正向扩展": ["投资", "投产", "拓店", "扩张", "建厂", "融资", "上市", "新品发布", "合作"],
    "负向风险": ["召回", "下架", "抽检不合格", "处罚", "减持", "关店", "裁员", "亏损"],
    "产品创新": ["新品", "低GI", "健康化", "升级", "配方", "研发"],
    "市场动态": ["市场份额", "销量", "营收", "增长", "下降", "促销", "营销"],
    "政策监管": ["市场监管总局", "食药监局", "抽检", "标准", "法规", "政策", "禁用", "超标"],
    "行业活动": ["春糖", "糖酒会", "博览会", "研讨会", "大会", "论坛", "报告"],
}

# Exclusion rules: noise that is not valuable
EXCLUDE_KEYWORDS = [
    "与本项目无关的泛行业新闻",
    "天气/自然灾害类",
    "纯属股票价格波动无实质新闻",
]

# Content categories (5 major categories, each with 3 sub-columns)
CATEGORIES = [
    ("烘焙行业动态", "竞品扩张、投资、建厂"),
    ("产品与创新", "新品发布、配方升级、健康化"),
    ("渠道与市场", "渠道打法、营销策略、消费趋势"),
    ("食品安全监管", "政策、抽检、投诉、直播监管"),
    ("行业与展会", "大会、博览会、研讨会、报告"),
]
