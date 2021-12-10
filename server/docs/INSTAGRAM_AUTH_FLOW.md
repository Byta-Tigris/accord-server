# INSTAGRAM AUTHORIZATION FLOW

### Permissions
- instagram_graph_user_profile
- instagram_graph_user_media

## **Authorization from Creator**
- ### **API** : IG Display API
- ### **Requirements**
  - Client Id {Instagram-app-id}
  - Redidrect Uri
  - Scope
  - Response Type

- ### **Request [Frontend]**
``` curl 
https://api.instagram.com/oauth/authorize
    ?client_id=124545....
    &redirect_uri=https://furthetic.com/creator/auth
    &scope=user_profile,user_media
    &response_type=code
```
- ### **Response**
    The browser will redirect the user to the provided **redirect_uri** along with special parameters in the url
    - ### _**On Successful Authorization**_
        ```curl
        https://furthetic.com/creator/auth
            ?code=AFJ...#_
        ```
        Here __**#_**__ signifies the end of code and it must be removed from the code when in use
    - ### _**On Failed Authorization**_
        ```curl
        https://furthetic.com/creator/auth
            ?error=access_denied
            &error_response=user_denied
            &error_description=The+user+denied+your+request
        ```

## Exchanging Code For a Short-Live Token
- ### **API** : IG Display API
- ### **Requirements**
    - Client Id
    - Client Secret
    - code
    - Grant Type
    - Redirect Uri

- ### **Request**
``` curl 
https://api.instagram.com/oauth/authorize
    ?client_id=124545....
    &client_secret=eb9c7...
    &grant_type=authorization_code
    &redirect_uri=https://furthetic.com/creator/auth
    &code=AQBx-hBsH3....
```
- ### **Response**
  - ### **On Sucess**
        
        {
            "access_token":"IGQVJ...",
            "user_id" : 17841515484454545454187
        }
        
  - ### **On Failure**
        {
            "error_type": "OAuthException",
            "code": 400,
            "error_message": "Matching code was not found or was already used"
        }

## Exchanging Short-Lived Token with Long-Lived Token
Short Lived tokens are replaced with Long-Lived Token, with validity of 60 days and can be refreshed after 24 hours
- ### **API**: IG Display API
- ### **Permissions**
  - instagram_graph_user_profile
- ### **Request**
    ```curl
    GET https://graph.instagram.com/access_token
        ?grant_type=ig_exchange_token
        &client_secret={instagram-app-secret}
        &access_token={short-lived_access_token}
    ```
- ### **Response**
  ```curl
  {
    "access_token":"{long-lived-user-access-token}",
    "token_type": "bearer",
    "expires_in": 5183944  // Number of seconds until token expires
  }
  ```

## Refreshing a Long-Lived Token
- ### **Request**
    ```curl
    GET https://graph.instagram.com/refresh_access_token
        ?grant_type=ig_refresh_token
        &access_token={long-lived_access_token}
    ```
- ### **Response**
  ```curl
  {
    "access_token":"{long-lived-user-access-token}",
    "token_type": "bearer",
    "expires_in": 5183944  // Number of seconds until token expires
  }
  ```

## Get User Profiles
- ### **API**: IG Display API
- ### **Permissions**
  - instagram_graph_user_profile
  - instagram_graph_user_media
- ### **Request**
    ```curl
    GET https://graph.instagram.com/me
        ?fields={fields}
        &access_token={long-lived_access_token}
    ```
- ### **Fields**
    - account_type
    - id
    - media_count
    - username
- ### **Response**
  ```curl
  {
    "id": "jdfshgkfjhg",
    "username": ...
    ....
  }
  ```

## Get User Media
- ### **API**: IG Display API
- ### **Permissions**
  - instagram_graph_user_profile
  - instagram_graph_user_media
- ### **Request**
    ```curl
    GET https://graph.instagram.com/me/media
        ?fields={fields}
        &access_token={long-lived_access_token}
    ```
- ### **Fields**
  - caption
  - id
  - media_type
  - media_url
  - permalink
  - thumbnail_url
  - timestamp
  - username
- ### **Response**
  ```curl
  {
    "data": [
        {
            "id": "dshgkhfg",
            "caption": "dfgkjfg"
            ...
        }
        ...
    ],
    "paging":{
        "cursors": {
            "after": "dfg...",
            "before": "dsgh...",
        },
        "next": "https:/graph.faceb...."
    }
  }
  ```

  ## Get Media Data
- ### **API**: IG Display API
- ### **Permissions**
  - instagram_graph_user_media
- ### **Request**
    ```curl
    GET https://graph.instagram.com/{media_id}
        ?fields={fields}
        &access_token={long-lived_access_token}
    ```
- ### **Fields**
  - caption
  - id
  - media_type
  - media_url
  - permalink
  - thumbnail_url
  - timestamp
  - username
- ### **Response**
  ```curl
  {
    "id": ....
    ....
  }
  ```