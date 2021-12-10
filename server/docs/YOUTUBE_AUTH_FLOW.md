# YOUTBE AUTH FLOW

## Authorizing Creator Channel[Frontend]

### Request
- url: https://accounts.google.com/o/oauth2/v2/auth
- scope [**Required**] :https://www.googleapis.com/auth/youtube.force-ssl
- redirect_uri [**Required**]
- response_type [**Required**]: code
- client_id [**Required**]: __client_id__
- state : Random string value to avoid cross-site forgery
- include_granted_scopes: true
  
```curl
GET https://accounts.google.com/o/oauth2/v2/auth?
    scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.readonly&
    access_type=offline&
    include_granted_scopes=true&
    state=__state__&
    redirect_uri=http%3A%2F%2Flocalhost%2Foauth2callback&
    response_type=code&
    client_id=__client_id__
```

### Response
- **onSucess** : https://redirect__url?code=___code___
- **onFailure** : https://redirect__url?error=access_denied

## Exchanging code with tokens

### Request [POST]
- url : https://oauth2.googleapis.com/token
- client_id
- client_secret
- code
- grant_type: authorization_code
- redirect_uri

### Response
- acess_token
- expires_in (secs)
- refresh_token
- scope
- token_type

## Refreshing the token

### Request [POST]
- url : https://oauth2.googleapis.com/token
- client_id
- client_secret
- grant_type: refresh_token
- refresh_token

### Response
- access_token
- expires_in
- scope
- token_type