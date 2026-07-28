from app.agents.collector import CollectorAgent

collector = CollectorAgent()

response = collector.collect(
    """
    Business Intelligence é...
    """
)

print(response)