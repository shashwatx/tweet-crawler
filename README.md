# Introduction

Fetches tweets for a given handle using the Twitter API.


## Required packages

Package | Version | Description
---- | ----|-------
[coloredlogs](https://pypi.org/project/coloredlogs/)|7.3| Logging
[click](https://pypi.org/project/click/) |7.0| Command line args
[time](https://docs.python.org/2/library/time.html) |n/a| Time related functions
[csv](https://docs.python.org/2/library/csv.html) |1.0| CSV operations
[os](https://docs.python.org/2/library/os.html) |n/a| File system utils 
[logging](https://docs.python.org/2/library/logging.html) | 0.5.1.2 | Logging

## Show Usage 
```
python driver.py --help
```

### Example
```
python driver.py -u 123123123 -o data/ -c conf.json
```

conf.json
```
{
    "apikeys": {
        "blah": {
            "app_key": "APP_KEY",
            "app_secret": "APP_SECRET"
        }
    }
}
```
## JSON Manipulation


1. Filter all tweets to get tweets of type "_handle_ responds to mentions"
```
cat handle.json | jq '.[] | if .in_reply_to_status_id_str!=null then {id: .id_str, text: .full_text, date: .created_at, responseTo: .in_reply_to_status_id_str } else null end '  | grep -v "null" | sed -e 's/}/},/' > handle_responds_to_mentions.json
```

2. (BONUS) For each message, find how many responds the handle made.
```
cat handle_responds_to_mentions.json | jq '.[] | .responseTo' | sort | uniq -c | sort -k1,1 -nr | head
```

3. For each tweet of type "handle responds to mentions" get the id of mention and call twurl to get the corresponding text
```
cat handle_responds_to_mentions.json | jq '.[] | .responseTo' | sort | uniq | xargs -I {} sh -c 'echo {}; ./twurlScript.sh {}; sleep 2'
```


