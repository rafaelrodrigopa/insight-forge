from app.providers.linkedin import LinkedInAuth, LinkedInPublisher


auth = LinkedInAuth()

profile = auth.get_profile()

print(profile)


publisher = LinkedInPublisher()

result = publisher.publish_text(
    text="Teste publicado pelo Insight Forge 🚀",
    person_id=profile["sub"]
)

print(result)