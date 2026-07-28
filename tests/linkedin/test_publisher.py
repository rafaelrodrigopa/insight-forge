from app.providers.linkedin import LinkedInPublisher


publisher = LinkedInPublisher()


response = publisher.publish_text(
    "🚀 Teste publicado pelo Insight Forge"
)


print(response.status_code)
if response.text:
    print(response.json())
else:
    print("Publicação criada com sucesso!")
    print("Post ID:", response.headers.get("X-RestLi-Id"))