# Notes on Standard Search API for Searching Tweets

## API Endpoint
```
https://api.twitter.com/1.1/search/tweets.json
```

## Limits
Source: [Official Docs](https://developer.twitter.com/en/docs/basics/rate-limits)

### search/tweets 
Requests per 15 min: 450
Supported History: 7 days 

## Example

### curl
__Note__: You must generate and pass the _oauthfields_ separately. 

```
curl --request GET \
--url 'https://api.twitter.com/1.1/search/tweets.json?q=from%3Atwitterdev&result_type=mixed&count=2' \
--header 'authorization: OAuth oauth\_consumer\_key="consumer-key-for-app", oauth\_nonce="generated-nonce", oauth\_signature="generated-signature", oauth\_signature\_method="HMAC-SHA1", oauth\_timestamp="generated-timestamp", oauth\_token="access-token-for-authed-user", oauth\_version="1.0"'
```
### twurl
* Install _twurl_
```
apt-get install -y twurl
```
* Setup auth
```
twurl authorize --consumer-key ${consumer_key} --consumer-secret ${consumer_secret}
```
* Use
```
query_term=$(rawurlencoded "vueling or iberia or easyjet")
twurl /1.1/search/tweets.json?q=${query_term}&result_type=recent&count=15&lang=es
```


