from app.providers.linkedin import LinkedInProfile


profile = LinkedInProfile()

data = profile.get_profile()


print("Perfil LinkedIn:")
print(data)