# InstaBot
A python3 bot for automating various methods of Instagram engagement for the purpose of growing an account's following.

## Getting Started

## Bot Modes
#### Mode 1: Scrape Tags
- Scrape recent media from tags defined in tagList and engage with users who posted the media (like, comment, follow).

#### Mode 2: Scrape Likers
- Scrape recent media from users defined in usernameScrapeList and engage with users who liked the media (follow).

#### Mode 3: Scrape Followers
- Scrape followers from users defined in usernameScrapeList and engage with these users (follow).

#### Mode 4: Mass Unfollow
- Unfollow users 'en masse'.
- Takes unfollowType:
  - Type 1: Unfollow users who do not follow back.
  - Type 2: Unfollow users who have followed back.
  - Type 3: Unfollow users indiscriminately.

#### Mode 5: Save Following
- Dump user ID's of users currently following the logged in account. This is to enable blacklisting users who have already been engaged with after unfollowing them.


## Instagram Private API Notes
#### Rate Limits:
- API is most likely in "Sandbox" mode.
- Rate Limits are "Sliding 1hr Window"
- Total Requests: 500/hr, 12000/day (Can Spam 100 before cooldown)
- Relationships Endpoint: 30/hr, 720/day
- Likes Endpoint: 30/hr, 720/day
- Comments Endpoint: 30/hr, 720/day

#### API Error Codes:
- Error 439: API (Too many Requests [Unknown])
- Error 429: API (Too many Requests [Sliding 1hr Window])
- Error 404: API (Does not exist [Not Found])
- Error 400: API (Bad request [Malformed])
