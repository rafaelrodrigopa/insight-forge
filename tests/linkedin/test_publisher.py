from app.providers.linkedin import LinkedInPublisher


publisher = LinkedInPublisher()


response = publisher.publish_text(
    "🚀 Teste publicado pelo Insight Forge"
)


print(response.status_code)
print(response.json())