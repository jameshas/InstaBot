import random
import time
import datetime
from src import InstaPyAPI
from src import SpinTax as spintax
IG = InstaPyAPI.InstaPyAPI()

class InstaBot:
    '''
    All Custom functions used by InstaBot using InstaPyAPI Base
    '''

    def __init__(self,
                 username="",
                 password="",
                 reachTargetTime=0,
                 followTarget=0,
                 unfollowTarget=0,
                 unfollowType=0,
                 concurrentUnfollow=0,
                 followingFloor=0,
                 followingCeil=0,
                 likeTarget=0,
                 mediaMaxLike=0,
                 mediaMinLike=0,
                 commentTarget=0,
                 commentArray=[],
                 blacklistFile="",
                 usernameRegexList=[],
                 usernameScrapeList=[],
                 tagList=[],
                 maxEngagementsPerUser=0,
                 maxEngagementsPerTag=0,
                 errorLimit=0,
                 errorCooldown=0):

        # Set Global Vars
        self.loginUsername = username
        self.reachTargetTime = reachTargetTime
        self.followTarget = followTarget
        self.unfollowTarget = unfollowTarget
        self.unfollowType = unfollowType
        self.concurrentUnfollow = concurrentUnfollow
        self.followingFloor = followingFloor
        self.followingCeil = followingCeil
        self.likeTarget = likeTarget
        self.mediaMaxLike = mediaMaxLike
        self.mediaMinLike = mediaMinLike
        self.commentTarget = commentTarget
        self.commentArray = commentArray
        self.blacklistFile = blacklistFile
        self.engagementBlacklist = []
        self.usernameScrapeList = usernameScrapeList
        self.usernameRegexList = usernameRegexList
        self.tagList = tagList
        self.maxEngagementsPerUser = maxEngagementsPerUser
        self.maxEngagementsPerTag = maxEngagementsPerTag
        self.errorLimit = errorLimit
        self.errorCooldown = errorCooldown

        self.actionDelayTime = {"Like": (self.reachTargetTime * 60 * 60) / self.likeTarget if self.likeTarget > 0 else 0, \
                                "Comment": (self.reachTargetTime * 60 * 60) / self.commentTarget if self.commentTarget > 0 else 0, \
                                "Follow": (self.reachTargetTime * 60 * 60) / self.followTarget if self.followTarget > 0 else 0, \
                                "Unfollow": (self.reachTargetTime * 60 * 60) / self.unfollowTarget if self.unfollowTarget > 0 else 0, \
                                "Request": (0), \
                                "Error": (self.errorCooldown * 60) if self.errorCooldown else 0}
        self.actionDelayNextTime = {"Like": 0, "Comment": 0, "Follow": 0, "Unfollow": 0, "Request": 0}
        self.actionSuccessCount = {"Like": 0, "Comment": 0, "Follow": 0, "Unfollow": 0, "Request": 0}
        self.actionErrorCount = {"Like": 0, "Comment": 0, "Follow": 0, "Unfollow": 0, "Request": 0}
        self.actionErrorTemp = {"Like": 0, "Comment": 0, "Follow": 0, "Unfollow": 0, "Request": 0}

        self.startTime = datetime.datetime.now().replace(microsecond=0)
        self.log(">>>  InstaBot v3.0 Initialised @ %s.  <<<\n" % (self.startTime.strftime("%H:%M %d/%m/%Y")))

        # Login to Instagram Account
        if not IG.userLogin(username, password):
            self.invokeExit()

    def modeScrapeTags(self):
        ''' Automate Instagram interactions by tags
        Tag Scraper mode uses an array of tags to search for new media. If
        new media is found and validated the bot will like and comment on the media.
        This is intended to replicate organic Instagram tag discovery.

        Args:
            N/A
        Returns:
            N/A
        '''

        if (len(self.tagList) > 0 and self.mediaMaxLike) and ((self.likeTarget) or (self.commentTarget and len(self.commentArray) > 0)):
            # Loop through each tag in tagList
            for currentTag in self.tagList:
                self.log("\nINF: Begin tag \"%s\" engagement." % (currentTag))
                tagEngagements = 0

                # Get Most Recent Media of Current Tag from tagList
                self.actionHandler("Request", "Wait")
                currentTagMedia = self.actionHandler("Request", IG.getMediaByTag(currentTag, 50))
                if not currentTagMedia:
                    continue

                # Loop Through Current Tag Media
                for currentMedia in currentTagMedia:
                    if tagEngagements >= self.maxEngagementsPerTag:
                        break
                    mediaEngaged = 0

                    # Get Current Media Info
                    self.actionHandler("Request", "Wait")
                    mediaInf = self.actionHandler("Request", IG.getMediaInfo(currentMedia))

                    if not mediaInf:
                        continue

                    if self.getMediaIsValid(mediaInf):
                        # Engage with media
                        if self.likeTarget and self.commentTarget:
                            # Get shortest wait time for next engagement
                            if self.actionHandler("Like", "Remaining") < self.actionHandler("Comment", "Remaining"):
                                # Like is closest interaction
                                self.actionHandler("Like", "Wait")
                                if self.actionHandler("Like", IG.mediaLike(currentMedia)):
                                    mediaEngaged = 1
                            else:
                                # Comment is closest interaction
                                randComment = spintax.spin(self.commentArray[random.randint(0, (len(self.commentArray) - 1))])
                                self.actionHandler("Comment", "Wait")
                                if self.actionHandler("Comment", IG.mediaComment(currentMedia, randComment)):
                                    mediaEngaged = 1
                        elif self.likeTarget:
                            # Like Only
                            self.actionHandler("Like", "Wait")
                            if self.actionHandler("Like", IG.mediaLike(currentMedia)):
                                mediaEngaged = 1
                        elif self.commentTarget:
                            # Comment Only
                            randComment = spintax.spin(self.commentArray[random.randint(0, (len(self.commentArray) - 1))])
                            self.actionHandler("Comment", "Wait")
                            if self.actionHandler("Comment", IG.mediaComment(currentMedia, randComment)):
                                mediaEngaged = 1

                        if mediaEngaged:
                            tagEngagements += 1
                            self.log("INF: Completed engagement %i/%i for tag \"%s\"." % (tagEngagements, self.maxEngagementsPerTag, currentTag))
        else:
            self.log("ERR: Bot parameters unsatisfactory for mode Scrape Tags.")
            self.invokeExit()

    def modeScrapeLikers(self):
        ''' Automate Instagram interactions by Media Likers
        Tag Scraper mode uses an array of users to search for recent media from. The
        bot will then engage with the likers of the media by following suitable likers.
        This mode is extremely effective at driving engagement if the users specified
        for media scraping are related to the botted account's niche.
        This is intended to replicate organic Instagram "follow for follow" engagement.

        Args:
            N/A
        Returns:
            N/A
        '''

        if len(self.usernameScrapeList) > 0 and self.maxEngagementsPerUser > 0 and self.followTarget > 0:
            # Follow Likers of Media From all Users in userNameScrapeList
            for currentUser in self.usernameScrapeList:
                # ----Before Commencing User Engagement Check Following Ceiling----
                if self.concurrentUnfollow and self.followingCeil and self.followingFloor:
                    self.actionHandler("Request", "Wait")
                    loginUserInf = self.actionHandler("Request", IG.getUserInfo(IG.loginUserID))

                    # Following Ceiling Met, Unfollow to meet Following Floor
                    if loginUserInf and loginUserInf["followingCount"] > self.followingCeil:
                        self.log("\nINF: Concurrent Unfollow (Start). Following: %i. Target: %i." % (loginUserInf["followingCount"], self.followingFloor))

                        followDiff = loginUserInf["followingCount"] - self.followingFloor
                        self.modeMassUnfollow(followDiff)

                        self.log("INF: Concurrent Unfollow (Finish).")

                # ----Begin User Engagement----
                self.log("\nINF: Begin user \"%s\" media likers engagement." % (currentUser))
                userEngagements = 0

                # Get Info of Current User from UsernameScrapeList
                self.actionHandler("Request", "Wait")
                currentUserInf = self.actionHandler("Request", IG.getUserInfo(currentUser))
                if not currentUserInf:
                    continue

                # Get 3 Most Recent Media of Current User from UsernameScrapeList
                self.actionHandler("Request", "Wait")
                currentUserMedia = self.actionHandler("Request", IG.getMediaByUser(currentUserInf["userID"], 3))
                if not currentUserMedia:
                    continue

                # Loop Through Current User Media
                for currentMedia in currentUserMedia:
                    if userEngagements >= self.maxEngagementsPerUser:
                        break

                    # Get Likers of Current User Media
                    self.actionHandler("Request", "Wait")
                    mediaLikersTemp = self.actionHandler("Request", IG.getMediaLikers(currentMedia, 5000))
                    if not mediaLikersTemp:
                        break

                    # Read Engagement Blacklist from File
                    if self.blacklistFile != "":
                        self.engagementBlacklist = self.blacklistHandler(self.blacklistFile, "r")

                    # Remove Blacklisted Likers of Current User Media
                    if len(self.engagementBlacklist) > 0:
                        initialUserCount = len(mediaLikersTemp)
                        mediaLikers = [x for x in mediaLikersTemp if x not in self.engagementBlacklist]
                        self.log("INF: Removed %i users from media likers who are blacklisted." % (initialUserCount - len(mediaLikers)))
                    else:
                        mediaLikers = mediaLikersTemp

                    # Shuffle The Likers of Current User media
                    random.shuffle(mediaLikers)

                    # Loop Through Likers of Current User Media
                    for mediaLiker in mediaLikers:
                        self.actionHandler("Request", "Wait")
                        mediaLikerInf = self.actionHandler("Request", IG.getUserInfo(mediaLiker))

                        if not mediaLikerInf:
                            continue

                        if self.getUserIsValid(mediaLikerInf):
                            # Follow User
                            self.actionHandler("Follow", "Wait")
                            if self.actionHandler("Follow", IG.userFollow(mediaLiker)):
                                userEngagements += 1

                                # Make sure to blacklist the user from future interactions
                                if self.blacklistFile != "":
                                    self.blacklistHandler(self.blacklistFile, "a", userList=[mediaLiker])

                                self.log("INF: Completed engagement %i/%i for user \"%s\"." % (userEngagements, self.maxEngagementsPerUser, currentUser))

                        if userEngagements >= self.maxEngagementsPerUser:
                            break
        else:
            self.log("ERR: Bot parameters unsatisfactory for mode Scrape Likers.")
            self.invokeExit()

    def modeScrapeFollowers(self):
        ''' Automate Instagram interactions by Followers
        Follower Scraper mode uses an array of users to retrieve followers of.
        The bot will then follow suitable followers of the user.
        This is intended to replicate organic Instagram "follow for follow" engagement.

        Args:
            N/A
        Returns:
            N/A
        '''
        pass

    def modeMassUnfollow(self, unfollowAmount, updateBlacklist=1):
        ''' Automate Instagram Unfollowing
        Mass unfollow mode will unfollow users of the botting account. This saves alot
        of time from having to manually unfollow and is also far more effective as
        filters can be applied to the users being unfollowed.

        Args:
            unfollowAmount: Amount of users to unfollow
            updateBlacklist: When true the userBlacklist file will be updated before unfollow begins
        Returns:
            N/A
        '''

        if self.unfollowTarget > 0:
            self.log("\nINF: Mass Unfollow (Start). Unfollow type: %i. Unfollow amount: %i." % (self.unfollowType, unfollowAmount))

            # Update Blacklist to add current following before unfollowing
            if updateBlacklist:
                self.blacklistHandler(self.blacklistFile, "a")

            # Begin gathering info to unfollow users
            self.actionHandler("Request", "Wait")
            loginUserFollowing = self.actionHandler("Request", IG.getUserFollowing(IG.loginUserID, 7500))
            loginUserFollowing.reverse()    # Sort following from oldest to newest

            if loginUserFollowing != None and len(loginUserFollowing) > 0:
                unfollowCount = 0

                for currentUser in loginUserFollowing:
                    if self.unfollowType == 1 or self.unfollowType == 2:
                        # Check user info before unfollowing
                        self.actionHandler("Request", "Wait")
                        currentUserInfo = self.actionHandler("Request", IG.getUserInfo(currentUser))

                        if self.unfollowType == 1 and currentUserInfo != None and not currentUserInfo["followMe"]:
                            # Unfollow users who do not follow back only.
                            self.actionHandler("Unfollow", "Wait")
                            if self.actionHandler("Unfollow", IG.userUnfollow(currentUser)):
                                unfollowCount += 1
                        elif self.unfollowType == 2 and currentUserInfo != None and currentUserInfo["followMe"]:
                            # Unfollow users who have followed back only.
                            self.actionHandler("Unfollow", "Wait")
                            if self.actionHandler("Unfollow", IG.userUnfollow(currentUser)):
                                unfollowCount += 1
                    elif self.unfollowType == 3:
                        # Unfollow users indiscriminately
                        self.actionHandler("Unfollow", "Wait")
                        if self.actionHandler("Unfollow", IG.userUnfollow(currentUser)):
                            unfollowCount += 1

                    if unfollowCount >= unfollowAmount:
                        self.log("INF: Mass Unfollow (Finish).")
                        break

                self.log("INF: Mass Unfollow (Finish).")
        else:
            self.log("ERR: Bot parameters unsatisfactory for mode Mass Unfollow.")
            self.invokeExit()

    def getUserIsValid(self, userInfo):
        ''' Check if user meets set criteria for engagements
        Addition to follow / following count is to avoid divide by 0 exception
        Args:
            userInfo: Dict of user information
        Returns:
            Bool: User meets criteria (True) / User does not meet criteria (False)
        '''

        try:
            userValidated = 0
            followerRatio = (userInfo["followerCount"] + 1) / (userInfo["followingCount"] + 1)

            if (
                    userInfo["userName"] != self.loginUsername
                    and userInfo["isBusiness"] != 1
                    and userInfo["mediaCount"] >= 9
                    and userInfo["meFollow"] != 1
                    and userInfo["followMe"] != 1
                    and userInfo["followerCount"] <= 1200
                    and followerRatio <= 2
                ):
                userValidated = 1

                # Username Filtering
                if len(self.usernameRegexList) > 0:
                    for badString in self.usernameRegexList:
                        if badString in userInfo["userName"]:
                            userValidated = 0
                            break

                # Blacklist Filtering
                if len(self.engagementBlacklist) > 0:
                    for badUserID in self.engagementBlacklist:
                        if badUserID == userInfo["userID"]:
                            userValidated = 0
                            self.log("INF: User \"%s\" is blacklisted." % (userInfo["userName"]))
                            break

            if userValidated:
                self.log("INF: User \"%s\" is valid." % (userInfo["userName"]))
                return True
            else:
                self.log("INF: User \"%s\" is not valid." % (userInfo["userName"]))
                return False
        except Exception as errorString:
            self.log("ERR: Check user \"%s\" valid exception. Exception Info: %s." % (userInfo["userName"], str(errorString)))
            return False

    def getMediaIsValid(self, mediaInfo):
        ''' Check if media meets set criteria for engagements
        Args:
            mediaInfo: Dict of media information
        Returns:
            Bool: Media meets criteria (True) / Media does not meet criteria (False)
        '''

        try:
            mediaValidated = 0

            if mediaInfo["userLiked"] != 1 and mediaInfo["ownerUsername"] != self.loginUsername and not mediaInfo["commentDisabled"]:
                if (
                        (mediaInfo["likeCount"] <= self.mediaMaxLike and mediaInfo["likeCount"] >= self.mediaMinLike)
                        or (self.mediaMaxLike == 0 and mediaInfo["likeCount"] >= self.mediaMinLike)
                        or (self.mediaMinLike == 0 and mediaInfo["likeCount"] <= self.mediaMaxLike)
                        or (self.mediaMinLike == 0 and self.mediaMaxLike == 0)
                    ):
                    mediaValidated = 1

            if mediaValidated:
                self.log("INF: Media \"%s\" is valid." % (mediaInfo["mediaShortcode"]))
                return True
            else:
                self.log("INF: Media \"%s\" is not valid." % (mediaInfo["mediaShortcode"]))
                return False

        except Exception as errorString:
            self.log("ERR: Check media \"%s\" valid exception. Exception Info: %s." % (mediaInfo["mediaShortcode"], str(errorString)))
            return False

    def actionHandler(self, action, status):
        if status is not False and status is not None and status != "Wait" and status != "Remaining":
            # No Error: Reset Temp Counter | Set Normal Delay
            self.actionSuccessCount[action] += 1
            self.actionErrorTemp[action] = 0

            randRange = (-10, 10) if self.actionDelayTime[action] > 100 else (-3, 3)
            randDelay = random.randint(randRange[0], randRange[1]) if self.actionDelayTime[action] != 0 else 0
            self.actionDelayNextTime[action] = time.time() + (self.actionDelayTime[action] + randDelay)
            return status
        elif status is False or status is None:
            # Error: Increase Counter | Error Logic
            self.actionErrorCount[action] += 1
            self.actionErrorTemp[action] += 1

            if self.actionErrorTemp[action] >= self.errorLimit:
                self.actionErrorTemp[action] = 0
                self.log("INF: Error limit (%i) reached for action \"%s\". Halting action for %imins." % (self.errorLimit, action, self.errorCooldown))

                self.actionDelayNextTime[action] = time.time() + self.actionDelayTime["Error"]
            else:
                randRange = (-10, 10) if self.actionDelayTime[action] > 100 else (-3, 3)
                randDelay = random.randint(randRange[0], randRange[1]) if self.actionDelayTime[action] != 0 else 0
                self.actionDelayNextTime[action] = time.time() + (self.actionDelayTime[action] + randDelay)
            return status
        elif status == "Wait":
            # Wait: Wait for next action
            if not self.actionDelayNextTime[action] <= time.time():
                interactionDelay = (self.actionDelayNextTime[action]) - time.time()
                self.log("INF: Waiting for \"%s\" delay to end. Remaining: %is." % (action, interactionDelay))
                time.sleep(interactionDelay)
            return status
        elif status == "Remaining":
            # Remaining: Return remaining delay time (in seconds)
            return (self.actionDelayNextTime[action]) - time.time()

    def blacklistHandler(self, fileName, action, userList=None, exitOnCompletion=0):
        ''' Handle UserID Blacklisting to / from file
        Blacklist Handler will write / read the list of user ID's following the
        botted account to a file to be used as an engagement blacklist for
        future engagements after a mass unfollowing.

        Args:
            fileName: Name of file to save / read list
            action: Can be "a" (append), "w" (overwrite), "r" (read & return as list)
            userList: Can use a list of userID's to blacklist rather than retrieving following
            exitOnCompletion: If true, exit after updating file
        Returns:
            list: List of UserID's in fileName blacklist (when action is "r")
        '''

        # Append Current Following to Blacklist File
        if action == "a":
            self.log("INF: Save user ID(s) to blacklist file (Attempt).")

            if userList != None:
                newIDs = userList
            else:
                self.actionHandler("Request", "Wait")
                newIDs = self.actionHandler("Request", IG.getUserFollowing(IG.loginUserID, 7500))

            if newIDs != None and len(newIDs) > 0:
                try:
                    with open(fileName, action + "+") as openFile:
                        existingIDs = []
                        openFile.seek(0)

                        # Read Existing ID's from File
                        for line in openFile:
                            existingIDs.append(int(line.strip()))

                        # Append New ID's to File, Ignoring Existing ID's
                        for userID in newIDs:
                            # Check if userID is already blacklisted
                            if len(existingIDs) > 0 and userID not in existingIDs:
                                # Append new blacklisted userID to file
                                openFile.write(str(userID) + "\n")
                            elif len(existingIDs) == 0:
                                # Write possibly old blacklisted user to file (Probably new file)
                                openFile.write(str(userID) + "\n")

                    self.log("INF: Save user ID(s) to blacklist file (Success).")
                except IOError:
                    self.log("ERR: Save user ID(s) to blacklist file (Exception)")
            else:
                self.log("ERR: Save user ID(s) to blacklist file (Failure).")

            # Exit After Appending / Writing to File
            if exitOnCompletion:
                self.invokeExit()

        # Read and Return UserID's from Blacklist File
        if action == "r":
            print("INF: Get engagement blacklist from file (Attempt).")
            userBlacklistTemp = []

            try:
                with open(fileName, action) as openFile:
                    for line in openFile:
                        userBlacklistTemp.append(int(line.strip()))

                    print("INF: Get engagement blacklist from file (Success).")
            except IOError:
                print("ERR: Get engagement blacklist from file (Failure).")

            return userBlacklistTemp

    def invokeExit(self):
        ''' Cleanup function to be run when exit cmd (CTRL+C) is sent
        Args:
            N/A
        Returns:
            N/A
        '''

        self.log("\n\nINF: Exit Invoked.")
        IG.userLogout()

        curTime = datetime.datetime.now().replace(microsecond=0)
        self.log("INF: [Action Success] | Like: %i | Comment: %i | Follow: %i | Unfollow: %i | Request: %i" % \
                        (self.actionSuccessCount["Like"], self.actionSuccessCount["Comment"], self.actionSuccessCount["Follow"], self.actionSuccessCount["Unfollow"], self.actionSuccessCount["Request"]))
        self.log("INF: [Action Failure] | Like: %i | Comment: %i | Follow: %i | Unfollow: %i | Request: %i" % \
                        (self.actionErrorCount["Like"], self.actionErrorCount["Comment"], self.actionErrorCount["Follow"], self.actionErrorCount["Unfollow"], self.actionErrorCount["Request"]))
        self.log("INF: Exit time: %s. Total working time %s." % \
                        (curTime.strftime("%H:%M %d/%m/%Y"), curTime - self.startTime))

        exit(1)

    def log(self, logString):
        ''' Prints logString to console
        Args:
            logString: String to print to console.
        Returns:
            N/A
        '''

        try:
            print(str(logString))
        except Exception as errorStr:
            print("ERR: Log Request Exception (Failure). Exception Info: %s." % (str(errorStr)))
