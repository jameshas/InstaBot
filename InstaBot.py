from src import InstaBotFunctions

# Set Instagram Bot Mode
botMode = 2

# Initialise Instagram Bot
IB = InstaBotFunctions.InstaBot(
    username="",
    password="",
    reachTargetTime=24,
    followTarget=800,
    unfollowTarget=800,
    unfollowType=3,
    concurrentUnfollow=1,
    followingFloor=500,
    followingCeil=7000,
    likeTarget=600,
    mediaMaxLike=150,
    mediaMinLike=3,
    commentTarget=500,
    commentArray=["{{e|E}xactily |{{j|J}ust |}}{{w|W}here|{w|W}hereabouts} {was|is}{ |  }{this|that} {great|amazing|brilliant|lovely|gorgeous|awesome|fantastic|dope|sweet|terrific|excellent|cool|impressive|perfect} {pic|picture|photo|image|shot|post} {taken|captured}{ |}{!|!!|!!!|?|??|???|!?|?!|.|🤔|🤔🤔|😮|😮😮😮|}", \
                  "{{w|W}hat|{w|W}hich} {cam|camera|phone|device|📷|📱}{ |  }{did you use|was used} to {take|capture|snap} this {pic|picture|photo|image|shot|post}{ |}{{?|??|???}|{!|!!|!!!}}{🤔|🤔🤔|}", \
                  "{i|I} {absolutely | definitely |completely |totally |really |utterly |entirely |simply |actually |genuinely |}{{love|💚|💙|💜|💛|❤️}|adore|like} {this|your|that|all of this|this kind of|this unique|this type of}{ |  }{pic|picture|photo|snap|shot|image|post}{ |}{{!|!!|!!!}|{😍|😍😍|😍😍😍}|{😮|😮😮}|}", \
                  "{{t|T}his|{y|Y}our} {pic|picture|photo|snap|shot|image|post}{ |  }is {great|amazing|brilliant|lovely|gorgeous|awesome|fantastic|dope|sweet|terrific|excellent|cool|impressive|perfect}{{, | }{thanks|thank you|thank-you}{ for {the share|sharing|posting}|}|}{ |}{💚|💙|💜|💛|❤️}{😍|😍😍|😍😍😍|😮|😮😮|😮😮😮|🔥|🔥🔥|🔥🔥🔥}", \
                  "{{g|G}reat|{a|A}wesome|{f|F}antastic|{a|A}mazing|{d|D}ope|{s|S}weet|{b|B}rilliant|{l|L}ovely|{g|G}orgeous|{t|T}errific|{e|E}xcellent|{c|C}ool|{i|I}mpressive|{p|P}erfect} {pic |picture |photo |snap |shot |image |post |}{bro|brother|dude|man}{ 😍|}{ , |, | }{{keep it {up|going}}|{{keen|hope|excited} to see {you post |some |}more {pics |snaps |shots |}like this}}{ |}{!|!!|!!!|}{{👍|👍👍|👍👍👍}|{🔥|🔥🔥|🔥🔥🔥}}{{🙌|🙌🙌|🙌🙌🙌|}|{😍|😍😍|😍😍😍|}}", \
                  "{{r|R}eally |{j|J}ust |}{{l|L}ove|{l|L}oving|❤️} {this|your} {great |amazing |brilliant |lovely |awesome |fantastic |dope |sweet |terrific |excellent |}{page|profile|account} {{and {your|its|the} {awesome |great |brilliant |amazing |sweet |dope |fantastic |terrific |excellent |cool |perfect |}{posts|content|pics|pictures|photos|images|snaps|uploads}}|}{ |}{!|!!|}{{😍|😍😍|😍😍😍}|{🔥|🔥🔥|🔥🔥🔥}|{👍|👍👍|👍👍👍}}"],
    blacklistFile="engagementBlacklist.txt",
    usernameRegexList=["second", "stuff", "art", "project", "love", "life", "food", "blog", \
                       "free", "photo", "graphy", "travel", "art", "shop", "store", "sex", "bag", \
                       "toko", "online", "jam", "fashion", "corp", "market", "sosis", "salon", \
                       "skin", "care", "cloth", "tech", "rental", "beauty", "express", "luxury", \
                       "collection", "impor", "preloved", "follow", "follower", "gain", ".id", \
                       "_id", "_tv", ".tv", "directory", "watches", "capture", "millionaire", \
                       "global", "world", "studio", "official", "inspiration", "motivation", \
                       "believe", "positive", "guidance", "automotive", "architecture", "money" \
                       "riches", "signature", "celebration", "diary", "home", "infinite", "car", \
                       "billion", "gratitude", "graphic", "jewelry", "design", "magazine", \
                       "journey", "elegant", "vip", "vape", "animal", "insurance", "bank", \
                       ".com", "_com", ".org", "_org", ".net", "_net", ".biz", "_biz", "build", \
                       "fact", "nutrition", "workout", "weight", "lifestyle", "boutique", "hotel", \
                       "realtor", "realty", "service", "bot", "property", "society", "estate", \
                       "agent", "trend", "wealth", "makeup", "channel", "fitness", "update", \
                       "management", "style", "page", "tutor", "organic", "business", "cosmetics", \
                       "aviation", "aesthetic", "watch", "gallery", "mafia", "gourmet", "recipe", \
                       "excellence", "supreme", "diamond", "daily", "shoes", "study", "flowers", \
                       "elite", "outlet", "luxurious", "depression", "healing", "construction", \
                       "trend", "kitchen", "addicted", "castle", "motivate", "gentleman", "vegan" \
                       "producer", "fabric", "consult", "yoga", "furniture", "america", "concept", \
                       "million", "vacation", "doctor", "lavish", "adventure", "promotion", ".gg", \
                       "media", "bikini", "fantasy", "iphone", "residence", "jewels", "delicate", \
                       "beach", "landscape", "refinement", "urban", "bucketlist", "redhot", \
                       "fanpage", "fan_page", "accessor", "interior", "home", "floors", \
                       "flooring", "carpet", "lounge", "concierge", "production", "social", \
                       "exotic", "network", "connoisseur", "revenue", "gentlemen", "enterprise", \
                       "original", "motors", "properties", "propertys", "account", "garage", "vibe"],
    usernameScrapeList=["example1", "example2"],
    tagList=["example1", "example2"],
    maxEngagementsPerUser=100,
    maxEngagementsPerTag=5,
    errorLimit=3,
    errorCooldown=10)

# Main Loop
while True:
    try:
        if botMode == 1:
            IB.modeScrapeTags()
        elif botMode == 2:
            IB.modeScrapeLikers()
        elif botMode == 3:
            IB.modeScrapeFollowers()
        elif botMode == 4:
            IB.modeMassUnfollow(7500)
        elif botMode == 5:
            IB.blacklistHandler("engagementBlacklist.txt", "a", exitOnCompletion=1)
    except KeyboardInterrupt:
        IB.invokeExit()
    except Exception as exceptionInf:
        print("\nERR: Main Loop Exception:\n      %s\n" % (str(exceptionInf)))





'''
========== Modes ==========
Mode 1: Scrape Tags
    Scrape recent media from tags defined in tagList and engage with users
    who posted the media (like, comment, follow).
Mode 2: Scrape Likers
    Scrape recent media from users defined in usernameScrapeList and engage
    with users who liked the media (follow).
Mode 3: Scrape Followers
    Scrape followers from users defined in usernameScrapeList and engage with
    these users (follow).
Mode 4: Mass Unfollow
    Unfollow users 'en masse'.
    Takes unfollowType:
        1. Unfollow users who do not follow back.
        2. Unfollow users who have followed back.
        3. Unfollow users indiscriminately.
Mode 5: Save Following
    Dump user ID's of users currently following the logged in account. This
    is to enable blacklisting users who have already been engaged with after
    unfollowing them.

Rate Limits:
    API is most likely in "Sandbox" mode.
    Rate Limits are "Sliding 1hr Window"
    Total Requests: 500/hr, 12000/day (Can Spam 100 before cooldown)
    Relationships Endpoint: 30/hr, 720/day
    Likes Endpoint: 30/hr, 720/day
    Comments Endpoint: 30/hr, 720/day

API Error Codes:
    Error 439: API (Too many Requests [Unknown])
    Error 429: API (Too many Requests [Sliding 1hr Window])
    Error 404: API (Does not exist [Not Found])
    Error 400: API (Bad request [Malformed])
'''
