# Notes on Issue fixing
Attemtping to use the api/v1/media/{media_id}/likers to get the likes

## First Attempt
```python
context.get_json(path=path, params={}, session=session)
*** instaloader.exceptions.ConnectionException: JSON Query to /api/v1/media/3400279570307938503/likers/: 403 Forbidden - "fail" status, message "CSRF token missing or incorrect" when accessing https://www.instagram.com//api/v1/media/3400279570307938503/likers/
```

### Fix to Error
```python
session.headers.update({'X-CSRFToken': session.cookies.get_dict()['csrftoken']})
```

## Second Attempt
```python
context.get_json(path=path, params={}, session=session)
*** instaloader.exceptions.QueryReturnedBadRequestException: 400 Bad Request - "fail" status, message "useragent mismatch" when accessing https://www.instagram.com//api/v1/media/3400279570307938503/likers/
```

### Attempted fix
```python
session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
```

## Solutions:
1. Try to use get_iphone_json
2. Figure out how to mirror the browser request that gets the likes



# Temporary Workaround
Use requests with a Session taken from the instaloadercontext, and then update the cookies and headers so that we can make /api/v1/ requests
and pass information from the instaloader instance when we can