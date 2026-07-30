import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.providers.linkedin import LinkedInProfile, LinkedInPublisher

try:
    profile = LinkedInProfile()
    data = profile.get_profile()
    print("PROFILO LINKEDIN OBTIDO COM SUCESSO!")
    print("Nome:", data.get("name"))
    print("ID (sub):", data.get("sub"))
    print("URN:", f"urn:li:person:{data.get('sub')}")
except Exception as e:
    print("ERRO AO OBTER PERFIL LINKEDIN:")
    print(e)
