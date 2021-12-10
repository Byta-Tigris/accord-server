# **INSTAGRAM CREATOR INSIGHTS**

### Permissions
    - pages_read_engagement
    - instagram_basic
    - pages_show_list
    - business_management
    - ads_management
    - instagram_manage_insights
    - pages_read_user_content

## **IG User Meta Datas (More Data than Display API could provide)**
- ### **API** : IG Graph API
- ### **Permissions**
    - pages_read_engagement
    - instagram_basic
    - pages_show_list
    - business_management
    - ads_management
- ### **Request**
```curl
GET https://graph.facebook.com/v3.2/{ig-user-id}
    ?fields={fields}
    &access_token={access_token}
```
- ### **Fields**
  - biography
  - id [Public id of the user]
  - ig_id
  - followers_count
  - follows_count
  - media_count
  - profile_picture_url
  - username
  - website


## **IG User Insight**
- ### **API** : IG Graph API
- ### **Permissions**
    - pages_read_engagement
    - instagram_basic
    - instagram_manage_insights
    - pages_show_list
    - business_management
    - ads_management
- ### **Request**
```curl
GET https://graph.facebook.com/v3.2/{ig-user-id}/insights
    ?metric={metric}
    &period={period}
    &since={since}
    &untill={untill}
    &access_token={access_token}
```
- ### **Periods**
  - lifetime
  - day
  - week
  - days_28
- ### **Metrics**
  - audience_city :: lifetime
  - audience_country :: lifetime
  - audience_gender_age :: lifetime
  - audience_locale :: lifetime
  - follower_count :: day
  - email_contacts :: day
  - get_direction_clicks :: day
  - impressions :: day,week, days_28
  - online_followers :: lifetime
  - phone_call_clicks :: day
  - profile_views :: day
  - reach :: day, week, days_28
  - text_message_clicks :: day
  - website_clicks :: day

- ### **Since & Untill (Range)**
Since will take the start unix time, i.e number of seconds passed till that time on unix timecount

- ### **Response**
  ```curl
  "data":[
      {
      "name": "impressions",
      "period": "day",
      "values": [
        {
          "value": 4,
          "end_time": "2017-05-04T07:00:00+0000"
        },
        {
          "value": 66,
          "end_time": "2017-05-05T07:00:00+0000"
        }
      ],
      "title": "Impressions",
      "description": "Total number of times this profile has been seen",
      "id": "17841400008460056/insights/impressions/day"
    },
    {
      "name": "reach",
      "period": "day",
      "values": [
        {
          "value": 3,
          "end_time": "2017-05-04T07:00:00+0000"
        },
        {
          "value": 36,
          "end_time": "2017-05-05T07:00:00+0000"
        }
      ],
      "title": "Reach",
      "description": "Total number of unique accounts that have seen this profile",
      "id": "17841400008460056/insights/reach/day"
    },
    {
      "name": "profile_views",
      "period": "day",
      "values": [
        {
          "value": 0,
          "end_time": "2017-05-04T07:00:00+0000"
        },
        {
          "value": 2,
          "end_time": "2017-05-05T07:00:00+0000"
        }
      ],
      "title": "Profile Views",
      "description": "Total number of unique accounts that have viewed this profile within the specified period",
      "id": "17841400008460056/insights/profile_views/day"
    }
  ]
  ```

## **Get All Stories**
- ### **API** : IG Graph API
- ### **Permissions**
  - instagram_basic
  - instagram_manage_insights
  - pages_read_engagement
  - pages_show_list
  - business_management
  
- ### **Request**
  ```curl 
  GET https://graph.facebook.com/{ig-user_id}/stories
  ```
- ### **Response**
  ```curl
  {
      "data": [
          {
              "id": ....
          },
          ....
      ]
  }
  ```


## **IG Media Insight**
- ### **API** : IG Graph API
- ### **Permissions**
    - pages_read_engagement
    - instagram_basic
    - instagram_manage_insights
    - pages_show_list
    - business_management
    - ads_management
- ### **Request**
```curl
GET https://graph.facebook.com/v12.0/{ig-user-id}/insights
    ?metric={metric}
    &access_token={access_token}
```
- ### **Metrics**
  - **Photo and Video Metrics**
    - engagement
    - impressions
    - reach
    - saved
    - video_views
  - **Album Metrics**
    - carousel_album_engagement
    - carousel_album_impressions
    - carousel_album_reach
    - carousel_album_saved
    - carousel_album_video_views
  - **Story Metrics**
    - exits :: Number of times someone exited the the story
    - impressions
    - reach
    - replies
    - taps_forward
    - taps_back


- ### **Response**
  ```curl
  "data":[
      {
      "name": "impressions",
      "period": "day",
      "values": [
        {
          "value": 4,
        }
      ],
      "title": "Impressions",
      "description": "Total number of times this profile has been seen",
      "id": "17841400008460056/insights/impressions/day"
    },
    {
      "name": "reach",
      "period": "day",
      "values": [
        {
          "value": 3
        },
        
      ],
      "title": "Reach",
      "description": "Total number of unique accounts that have seen this profile",
      "id": "17841400008460056/insights/reach/day"
    },
  ]
  ```