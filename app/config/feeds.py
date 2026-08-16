from typing import Dict, List


class FeedConfig:
    """
    Gerenciador do Pool de Feeds RSS categorizado por nicho técnico e mercado.
    """

    CATEGORIZED_FEEDS: Dict[str, List[Dict[str, str]]] = {
        "microsoft_analytics": [
            {
                "name": "Power BI & Microsoft Fabric News",
                "url": "https://news.google.com/rss/search?q=Power+BI+OR+Microsoft+Fabric",
                "priority_boost": 1.5,
            },
            {
                "name": "GCP Analytics (BigQuery & Dataform)",
                "url": "https://news.google.com/rss/search?q=BigQuery+OR+Dataform",
                "priority_boost": 1.5,
            },
            {
                "name": "Microsoft Research",
                "url": "https://www.microsoft.com/en-us/research/feed/",
                "priority_boost": 1.2,
            },
        ],
        "ia_data_science": [
            {
                "name": "Real Python",
                "url": "https://realpython.com/atom.xml",
                "priority_boost": 1.2,
            },
            {
                "name": "Google AI Blog",
                "url": "https://research.google/blog/rss/",
                "priority_boost": 1.2,
            },
            {
                "name": "AWS Machine Learning Blog",
                "url": "https://aws.amazon.com/blogs/machine-learning/feed/",
                "priority_boost": 1.2,
            },
            {
                "name": "NVIDIA Technical Blog",
                "url": "https://developer.nvidia.com/blog/feed",
                "priority_boost": 1.1,
            },
            {
                "name": "Hugging Face Blog",
                "url": "https://huggingface.co/blog/feed.xml",
                "priority_boost": 1.1,
            },
            {
                "name": "arXiv Computer Science AI",
                "url": "http://export.arxiv.org/rss/cs.AI",
                "priority_boost": 1.0,
            },
        ],
        "geral_tech": [
            {
                "name": "TecMundo",
                "url": "https://rss.tecmundo.com.br/feed",
                "priority_boost": 0.8,
            },
            {
                "name": "Canaltech",
                "url": "https://canaltech.com.br/rss/",
                "priority_boost": 0.8,
            },
        ],
        "negocios_mercado": [
            {
                "name": "InfoMoney",
                "url": "https://www.infomoney.com.br/feed/",
                "priority_boost": 0.8,
            },
            {
                "name": "Exame",
                "url": "https://exame.com/feed/",
                "priority_boost": 0.8,
            },
            {
                "name": "Valor Econômico",
                "url": "https://news.google.com/rss/search?q=site:valor.globo.com",
                "priority_boost": 0.8,
            },
            {
                "name": "Reuters Tech",
                "url": "https://news.google.com/rss/search?q=site:reuters.com+technology",
                "priority_boost": 0.9,
            },
            {
                "name": "Bloomberg Tech",
                "url": "https://news.google.com/rss/search?q=site:bloomberg.com+technology",
                "priority_boost": 0.9,
            },
        ],
    }

    @classmethod
    def get_all_feed_urls(cls) -> List[str]:
        """
        Retorna a lista completa de URLs de todos os feeds configurados no pool.
        """
        urls = []
        for category, feeds in cls.CATEGORIZED_FEEDS.items():
            for f in feeds:
                urls.append(f["url"])
        return urls

    @classmethod
    def get_all_feeds(cls) -> List[Dict[str, str]]:
        """
        Retorna todos os dicionários de feeds com metadados de nome e categoria.
        """
        all_feeds = []
        for category, feeds in cls.CATEGORIZED_FEEDS.items():
            for f in feeds:
                all_feeds.append({**f, "category": category})
        return all_feeds


feed_config = FeedConfig()
