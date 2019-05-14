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

Use jq

