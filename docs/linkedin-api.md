# LinkedIn API Integration Setup

## Overview

Este documento descreve todas as etapas necessárias para configurar a integração com a API do LinkedIn utilizando OAuth 2.0.

---

# 1. Criar aplicação no LinkedIn Developer Portal

Acesse:

https://www.linkedin.com/developers/

Crie uma nova aplicação.

Após criar a aplicação, serão disponibilizados:

- Client ID
- Client Secret

Essas credenciais serão utilizadas no fluxo OAuth 2.0.

---

# 2. Configurar Redirect URI

No painel da aplicação:

```
Auth
└── Authorized redirect URLs
```

Adicionar uma URL de callback.

Para ambiente local:

```
http://localhost:8000/callback
```

Essa URL será utilizada pelo LinkedIn para retornar o Authorization Code após a autorização do usuário.

---

# 3. Configurar variáveis de ambiente

Criar o arquivo `.env`:

```env
CLIENT_ID_LINKEDIN=
CLIENT_SECRET_LINKEDIN=
LINKEDIN_AUTH_CODE=
LINKEDIN_ACCESS_TOKEN=
```

O arquivo `.env` nunca deve ser versionado.

Adicionar no `.gitignore`:

```gitignore
.env
```

---

# 4. Fluxo OAuth 2.0

O LinkedIn utiliza o fluxo Authorization Code.

Fluxo completo:

```
Usuário
   |
   v
Authorization URL
   |
   v
Authorization Code
   |
   v
Access Token
   |
   v
LinkedIn API
```

Diferente de APIs como Gemini, o LinkedIn não utiliza apenas uma API Key para autenticação.

---

# 5. Gerar Authorization Code

Criar uma URL de autorização:

```
https://www.linkedin.com/oauth/v2/authorization
```

Parâmetros necessários:

```
response_type=code
client_id=CLIENT_ID
redirect_uri=REDIRECT_URI
scope=openid profile email
```

Exemplo:

```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=CLIENT_ID&redirect_uri=http://localhost:8000/callback&scope=openid%20profile%20email
```

Após o usuário autorizar a aplicação, o LinkedIn retorna:

```
http://localhost:8000/callback?code=AUTH_CODE
```

O parâmetro `code` será utilizado na próxima etapa.

---

# 6. Trocar Authorization Code por Access Token

Endpoint:

```
POST https://www.linkedin.com/oauth/v2/accessToken
```

Payload:

```json
{
  "grant_type": "authorization_code",
  "code": "AUTH_CODE",
  "client_id": "CLIENT_ID",
  "client_secret": "CLIENT_SECRET",
  "redirect_uri": "REDIRECT_URI"
}
```

Resposta esperada:

```json
{
  "access_token": "...",
  "expires_in": 5183999,
  "refresh_token": "...",
  "token_type": "Bearer"
}
```

O Access Token será utilizado para realizar chamadas na API.

---

# 7. Testar autenticação

Endpoint:

```
GET https://api.linkedin.com/v2/userinfo
```

Header:

```
Authorization: Bearer ACCESS_TOKEN
```

Exemplo:

```python
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}
```

Resposta esperada:

```json
{
  "sub": "user_id",
  "name": "User Name",
  "email": "user@email.com",
  "picture": "profile_image_url"
}
```

---

# 8. Problemas encontrados durante a configuração

## Application tokens

Erro:

```
This application is not allowed to create application tokens
```

Causa:

Foi utilizado o fluxo:

```
client_credentials
```

Esse fluxo não é permitido para essa aplicação LinkedIn.

Solução:

Utilizar:

```
authorization_code
```

---

## Invalid Access Token

Erro:

```
INVALID_ACCESS_TOKEN
```

Possíveis causas:

- Token copiado incorretamente
- Token expirado
- Token revogado
- Variável de ambiente não carregada corretamente

---

# 9. Estrutura dos testes

Arquivos utilizados:

```
tests/
│
├── test_linkedin.py
├── test_linkedin_oauth.py
└── test_linkedin_profile.py
```

Responsabilidades:

## test_linkedin.py

Validação inicial da conexão com a aplicação LinkedIn.

## test_linkedin_oauth.py

Realiza a troca do Authorization Code pelo Access Token.

## test_linkedin_profile.py

Valida uma chamada autenticada utilizando o Access Token.