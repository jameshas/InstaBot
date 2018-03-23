# InstaPyAPI Written by James H

import hmac
import uuid
import hashlib
import urllib.request
import json
import requests

class InstaPyAPI:
    '''
    InstaPyAPI Class uses Instagram's Private API to bring Instagram to Python
    These functions are designed for use as an Instagram Engagement bot, automating
    interactions such as follow for follow, like / comment recent media and follower targeting.
    '''

    def __init__(self):
        # -- Instagram Interaction URL's --
        # Account
        self.urlAPI = "https://i.instagram.com/api/v1/"
        self.urlLogin = "accounts/login/"
        self.urlLogout = "accounts/logout/"

        # Get Media
        self.urlMediaByTag = "feed/tag/{}/"
        self.urlMediaByUser = "feed/user/{}/"

        # Media / User Interaction
        self.urlLike = "media/{}/like/"
        self.urlComment = "media/{}/comment/"
        self.urlFollow = "friendships/create/{}/"
        self.urlUnfollow = "friendships/destroy/{}/"

        # User Information
        self.urlUserInfo = "users/{}/"
        self.urlUserFriendship = "friendships/show/{}/"
        self.urlUserFollowers = "friendships/{}/followers/"
        self.urlUserFollowing = "friendships/{}/following/"

        # Media Information
        self.urlMediaInfo = "media/{}/info/"
        self.urlMediaLikers = "media/{}/likers/"
        self.urlMediaCommenters = "media/{}/comments/"
        # ---------------------------------

        # Global Variables
        self.rSession = requests.Session()
        self.UUID = None
        self.loginUserID = None
        self.rankToken = None
        self.csrfToken = None

    def userLogin(self, userName, userPass):
        ''' Log into Instagram account
        Arguments:
            userName: Instagram username
            userPass: Instagram Password
        Returns:
            Bool: Login success (True) / Failure (False)
        '''

        self.log("INF: Login as user \"%s\" (Attempt)." % userName)

        # Generate UUID
        self.UUID = str(uuid.uuid4())

        # Generate Device ID
        md5Hash = hashlib.md5()
        md5Hash.update(userName.encode('utf-8') + userPass.encode('utf-8'))
        md5Hash2 = hashlib.md5()
        md5Hash2.update(md5Hash.hexdigest().encode('utf-8') + "12345".encode('utf-8'))
        deviceID = "android-" + md5Hash2.hexdigest()[:16]

        fetchHeaders = self.apiRequest('si/fetch_headers/?challenge_type=signup&guid=' + str(uuid.uuid4()).replace('-', ''), None)

        if fetchHeaders:
            requestData = json.dumps({'phone_id': str(uuid.uuid4()),
                                      '_csrftoken': fetchHeaders.cookies['csrftoken'],
                                      'username': userName,
                                      'guid': self.UUID,
                                      'device_id': deviceID,
                                      'password': userPass,
                                      'login_attempt_count': '0'
                                     })

            loginRequest = self.apiRequest(self.urlLogin, requestData)

            if loginRequest:
                self.loginUserID = json.loads(loginRequest.text)["logged_in_user"]["pk"]
                self.rankToken = "%s_%s" % (self.loginUserID, self.UUID)
                self.csrfToken = loginRequest.cookies["csrftoken"]

                self.log("INF: Login as user \"%s\" (Success)." % (userName))
                return True
            else:
                self.log("ERR: Login as user \"%s\" (Failure)." % (userName))
                return False

    def userLogout(self):
        ''' Logout of Instagram account
        Arguments:
            N/A
        Returns:
            Bool: Logout success (True) / Failure (False)
        '''

        self.log("INF: Logout (Attempt).")

        logoutRequest = self.apiRequest(self.urlLogout)

        if logoutRequest:
            self.log("INF: Logout (Success).")
            return True
        else:
            self.log("ERR: Logout (Failure).")
            return False

    def getUserInfo(self, userID):
        ''' Get various information from Instagram userID
        Get the private status, followers count, following count, following login user,
        login user following and media count.
        Arguments:
            userID: User ID / User Name of Instagram account to gather info from
        Returns:
            Dict: UserID, Username, Private, Business, Verified, MediaCount, FollowerCount, FollowingCount, LoginUser follow, Follow loginuser. (Success)
            None: (Failure)
        '''

        self.log("INF: Get info of user \"%s\" (Attempt)." % (userID))

        # Convert Username to userID
        if not str(userID).isdigit():
            userIDRequest = self.apiRequest(self.urlUserInfo.format(userID) + "usernameinfo/")

            if userIDRequest:
                userInfID = json.loads(userIDRequest.text)["user"]["pk"]
            else:
                self.log("ERR: Get info of user \"%s\" (Failure)." % (userID))
                return None
        else:
            userInfID = userID

        userInfRequest = self.apiRequest(self.urlUserInfo.format(userInfID) + "info/")
        userFriendshipRequest = self.apiRequest(self.urlUserFriendship.format(userInfID))

        if userInfRequest and userFriendshipRequest:
            userInfData = json.loads(userInfRequest.text)["user"]
            userFriendshipData = json.loads(userFriendshipRequest.text)

            userInfDict = {}
            userInfDict["userID"] = userInfData["pk"]
            userInfDict["userName"] = userInfData["username"]
            userInfDict["isPrivate"] = userInfData["is_private"]
            userInfDict["isBusiness"] = userInfData["is_business"]
            userInfDict["isVerified"] = userInfData["is_verified"]
            userInfDict["mediaCount"] = userInfData["media_count"]
            userInfDict["followerCount"] = userInfData["follower_count"]
            userInfDict["followingCount"] = userInfData["following_count"]
            userInfDict["meFollow"] = userFriendshipData["following"] or userFriendshipData["outgoing_request"]
            userInfDict["followMe"] = userFriendshipData["followed_by"] or userFriendshipData["incoming_request"]

            self.log("INF: Get info of user \"%s\" (Success)." % (userID))
            self.log("      User ID: %s\n      Username: %s\n      Private: %i\n      Business: %i\n      Verified: %i\n      Media: %i\n      Followers: %i\n      Following: %i\n      Me follow: %i\n      Follow me: %i" % \
                        (userInfDict["userID"], userInfDict["userName"], userInfDict["isPrivate"], userInfDict["isBusiness"], userInfDict["isVerified"], \
                        userInfDict["mediaCount"], userInfDict["followerCount"], userInfDict["followingCount"], userInfDict["meFollow"], userInfDict["followMe"]))

            return userInfDict
        else:
            self.log("ERR: Get info of user \"%s\" (Failure)." % (userID))
            return None

    def getUserFollowers(self, userID, amount=100):
        ''' Return the Followers of userID
        Args:
            userID: The User ID of the Instagram account to retrieve followers from.
            amount: Amount of UserID's to return
        Returns:
            List: Followers of userID in UserID format. (Success)
            None: (Failure)
        '''

        self.log("INF: Get followers of user \"%s\" (Attempt)." % (userID))

        nextMaxID = 0
        userFollowers = []

        while True:
            userFollowerRequest = self.apiRequest(self.urlUserFollowers.format(str(userID)) + ("?max_id=" + str(nextMaxID) if nextMaxID else ""))

            if userFollowerRequest:
                userFollowerData = json.loads(userFollowerRequest.text)

                for userObject in userFollowerData["users"]:
                    if len(userFollowers) != amount:
                        userFollowers.append(userObject["pk"])

                if "big_list" in userFollowerData and userFollowerData["big_list"] and userFollowerData["next_max_id"] and len(userFollowers) != amount:
                    nextMaxID = userFollowerData["next_max_id"]
                    continue
                else:
                    self.log("INF: Get followers of user \"%s\" (Success)." % (userID))
                    return userFollowers
            else:
                self.log("ERR: Get followers of user \"%s\" (Failure)." % (userID))
                return None

    def getUserFollowing(self, userID, amount=100):
        ''' Return the Followings of userID (Users that userID is following)
        Args:
            userID: The User ID of the Instagram account to retrieve followings from.
            amount: Amount of UserID's to return
        Returns:
            List: Followings of userID in UserID format. (Success)
            None: (Failure)
        '''

        self.log("INF: Get followings of user \"%s\" (Attempt)." % (userID))

        userFollowings = []
        userFollowingRequest = self.apiRequest(self.urlUserFollowing.format(str(userID)))

        if userFollowingRequest:
            userFollowingData = json.loads(userFollowingRequest.text)

            for userObject in userFollowingData["users"]:
                if len(userFollowings) != amount:
                    userFollowings.append(userObject["pk"])

            self.log("INF: Get followings of user \"%s\" (Success)." % (userID))
            return userFollowings
        else:
            self.log("ERR: Get followings of user \"%s\" (Failure)." % (userID))
            return None

    def userFollow(self, userID):
        ''' Follow Instagram User by UserID
        Arguments:
            UserID: Instagram ID of User to Follow
        Returns:
            Bool: Follow Success (True) / Failure (False)
        '''

        self.log("INF: Follow user \"%s\" (Attempt)." % (userID))

        requestData = json.dumps({'_uuid': self.UUID,
                                  '_uid': self.loginUserID,
                                  'user_id': userID,
                                  '_csrftoken': self.csrfToken
                                 })
        userFollowRequest = self.apiRequest(self.urlFollow.format(userID), requestData)

        if (
                userFollowRequest
                and (json.loads(userFollowRequest.text)["friendship_status"]["following"]
                or json.loads(userFollowRequest.text)["friendship_status"]["outgoing_request"])
            ):
            self.log("INF: Follow user \"%s\" (Success)." % (userID))
            return True
        else:
            self.log("ERR: Follow user \"%s\" (Failure)." % (userID))
            return False

    def userUnfollow(self, userID):
        ''' Unfollow Instagram user by UserID
        Arguments:
            UserID: Instagram ID of User to Unfollow
        Returns:
            Bool: Unfollow Success (True) / Failure (False)
        '''

        self.log("INF: Unfollow user \"%s\" (Attempt)." % (userID))

        requestData = json.dumps({'_uuid': self.UUID,
                                  '_uid': self.loginUserID,
                                  'user_id': userID,
                                  '_csrftoken': self.csrfToken
                                 })
        userUnfollowRequest = self.apiRequest(self.urlUnfollow.format(userID), requestData)

        if (
                userUnfollowRequest
                and not (json.loads(userUnfollowRequest.text)["friendship_status"]["following"]
                or json.loads(userUnfollowRequest.text)["friendship_status"]["outgoing_request"])
            ):
            self.log("INF: Unfollow user \"%s\" (Success)." % (userID))
            return True
        else:
            self.log("ERR: Unfollow user \"%s\" (Failure)." % (userID))
            return False

    def getMediaByTag(self, tagString, amount=10):
        ''' Get Media ID's by Tag (Recent posts using tag)
        Arguments:
            tagString: Tag to search for media
            amount: Amount of MediaID's to return
        Returns:
            List: Media ID's (Success)
            None: (Failure)
        '''

        self.log("INF: Get media by tag \"%s\" (Attempt)." % (tagString))

        nextMaxID = 0
        tagMedia = []

        while True:
            mediaRequest = self.apiRequest(self.urlMediaByTag.format(str(tagString)) + ("?max_id=" + str(nextMaxID) if nextMaxID else ""))

            if mediaRequest:
                mediaData = json.loads(mediaRequest.text)

                for mediaObject in mediaData["items"]:
                    if len(tagMedia) != amount:
                        tagMedia.append(mediaObject["pk"])

                if "more_available" in mediaData and mediaData["more_available"] and mediaData["next_max_id"] and len(tagMedia) != amount:
                    nextMaxID = mediaData["next_max_id"]
                    continue
                else:
                    self.log("INF: Get media by tag \"%s\" (Success)." % (tagString))
                    return tagMedia
            else:
                self.log("ERR: Get media by tag \"%s\" (Failure)." % (tagString))
                return None

    def getMediaByUser(self, userID, amount=10):
        ''' Get Media ID's from userID page
        Arguments:
            userID: Instagram ID of user to retrieve media from
            amount: Amount of MediaID's to return
        Returns:
            List: Media ID's (Success)
            None: (Failure)
        '''

        self.log("INF: Get media by user \"%s\" (Attempt)." % (userID))

        nextMaxID = 0
        userMedia = []

        while True:
            mediaRequest = self.apiRequest(self.urlMediaByUser.format(str(userID)) + ("?max_id=" + str(nextMaxID) if nextMaxID else ""))

            if mediaRequest:
                mediaData = json.loads(mediaRequest.text)

                for mediaObject in mediaData["items"]:
                    if len(userMedia) != amount:
                        userMedia.append(mediaObject["pk"])

                if "more_available" in mediaData and mediaData["more_available"] and mediaData["next_max_id"] and len(userMedia) != amount:
                    nextMaxID = mediaData["next_max_id"]
                    continue
                else:
                    self.log("INF: Get media by user \"%s\" (Success)." % (userID))
                    return userMedia
            else:
                self.log("ERR: Get media by user \"%s\" (Failure)." % (userID))
                return None

    def getMediaInfo(self, mediaID):
        ''' Get various information from Instagram mediaID
        Get the likes count, comments count, owner ID, owner username
        Arguments:
            mediaID: The unique media code for the image / video
        Returns:
            Dict: mediaID, mediaShortcode, media owner username, media owner ID, video?, login user liked?, likes, comments (Success)
            None: (Failure)
        '''

        self.log("INF: Get info of media \"%s\" (Attempt)." % (mediaID))

        requestData = json.dumps({'_uuid': self.UUID,
                                  '_uid': self.loginUserID,
                                  '_csrftoken': self.csrfToken,
                                  'media_id': mediaID
                                 })
        mediaInfRequest = self.apiRequest(self.urlMediaInfo.format(mediaID), requestData)

        if mediaInfRequest:
            mediaInfData = json.loads(mediaInfRequest.text)["items"][0]
            mediaInfDict = {}

            mediaInfDict["mediaID"] = mediaInfData["pk"]
            mediaInfDict["mediaShortcode"] = mediaInfData["code"]
            mediaInfDict["ownerUsername"] = mediaInfData["user"]["username"]
            mediaInfDict["ownerID"] = mediaInfData["user"]["pk"]
            mediaInfDict["isVideo"] = 1 if mediaInfData["media_type"] == 2 else 0
            mediaInfDict["userLiked"] = mediaInfData["has_liked"]
            mediaInfDict["likeCount"] = mediaInfData["like_count"]
            mediaInfDict["commentCount"] = mediaInfData["comment_count"] if "comment_count" in mediaInfData.keys() else 0
            mediaInfDict["commentDisabled"] = mediaInfData["comments_disabled"] if "comments_disabled" in mediaInfData.keys() else 0

            self.log("INF: Get info of media \"%s\" (Success)." % (mediaID))
            self.log("      Shortcode: %s\n      Owner username: %s\n      Owner ID: %s\n      Is video: %i\n      User liked: %i\n      Likes: %i\n      Comments: %i" % \
                        (mediaInfDict["mediaShortcode"], mediaInfDict["ownerUsername"], mediaInfDict["ownerID"], mediaInfDict["isVideo"], \
                        mediaInfDict["userLiked"], mediaInfDict["likeCount"], mediaInfDict["commentCount"]))

            return mediaInfDict
        else:
            self.log("ERR: Get info of media \"%s\" (Failure)." % (mediaID))
            return None

    def getMediaLikers(self, mediaID, amount=100):
        ''' Get the people who liked the mediaID
        Arguments:
            mediaID: The unique media code for the image / video
            amount: Amount of UserID's to return
        Returns:
            List: Likers in UserID format (Success)
            None: (Failure)
        '''

        self.log("INF: Get likers of media \"%s\" (Attempt)." % (mediaID))

        mediaLikers = []
        mediaLikersRequest = self.apiRequest(self.urlMediaLikers.format(mediaID))

        if mediaLikersRequest:
            likerData = json.loads(mediaLikersRequest.text)

            for userObject in likerData["users"]:
                if len(mediaLikers) != amount:
                    mediaLikers.append(userObject["pk"])

            self.log("INF: Get likers of media \"%s\" (Success)." % (mediaID))
            return mediaLikers
        else:
            self.log("ERR: Get likers of media \"%s\" (Failure)." % (mediaID))
            return None

    def getMediaCommenters(self, mediaID, amount=100):
        ''' Get the people who commented on the mediaID
        Arguments:
            mediaID: The unique media code for the image / video
            amount: Amount of UserID's to return
        Returns:
            List: Commenters in UserID format (Success)
            None: (Failure)
        '''

        self.log("INF: Get commenters of media \"%s\" (Attempt)." % (mediaID))

        nextMaxID = 0
        mediaCommenters = []

        while True:
            mediaCommentersRequest = self.apiRequest(self.urlMediaCommenters.format(mediaID) + ("?max_id=" + str(nextMaxID) if nextMaxID else ""))

            if mediaCommentersRequest:
                commenterData = json.loads(mediaCommentersRequest.text)

                for commentObject in commenterData["comments"]:
                    if len(mediaCommenters) != amount:
                        commenterID = commentObject["user_id"]

                        if commenterID not in mediaCommenters:  # Comment multiple times so filter
                            mediaCommenters.append(commenterID)

                if "has_more_comments" in commenterData and commenterData["has_more_comments"] and commenterData["next_max_id"] and len(mediaCommenters) != amount:
                    nextMaxID = commenterData["next_max_id"]
                    continue
                else:
                    self.log("INF: Get commenters of media \"%s\" (Success)." % (mediaID))
                    return mediaCommenters
            else:
                self.log("ERR: Get commenters of media \"%s\" (Failure)." % (mediaID))
                return None

    def mediaLike(self, mediaID):
        ''' Like Instagram media by ID
        Arguments:
            mediaID: Instagram ID of media to like
        Returns:
            Bool: Like Success (True) / Failure (False)
        '''

        self.log("INF: Like media \"%s\" (Attempt)." % (mediaID))

        requestData = json.dumps({'_uuid': self.UUID,
                                  '_uid': self.loginUserID,
                                  '_csrftoken': self.csrfToken,
                                  'media_id': mediaID
                                 })
        mediaLikeRequest = self.apiRequest(self.urlLike.format(mediaID), requestData)

        if mediaLikeRequest:
            self.log("INF: Like media \"%s\" (Success)." % (mediaID))

            return True
        else:
            self.log("ERR: Like media \"%s\" (Failure)." % (mediaID))
            return False

    def mediaComment(self, mediaID, commentString):
        ''' Comment Instagram media by ID
        Arguments:
            mediaID: Instagram ID of media to comment on
            commentString: String to insert as comment on media
        Returns:
            Bool: Comment Success (True) / Failure (False)
        '''

        self.log("INF: Comment \"%s\" on media \"%s\" (Attempt)." % (commentString, mediaID))

        requestData = json.dumps({'_uuid': self.UUID,
                                  '_uid': self.loginUserID,
                                  '_csrftoken': self.csrfToken,
                                  'comment_text': commentString
                                 })
        mediaCommentRequest = self.apiRequest(self.urlComment.format(mediaID), requestData)

        if mediaCommentRequest:
            self.log("INF: Comment \"%s\" on media \"%s\" (Success)." % (commentString, mediaID))

            return True
        else:
            self.log("ERR: Comment \"%s\" on media \"%s\" (Failure)." % (commentString, mediaID))
            return False

    def apiRequest(self, endpoint, postData=None):
        ''' Uses Requests Session to Get / Post to Instagram API
        Args:
            endpoint: API Endpoint to append.
            postData: Data to parse for Post request. If None, request will be in Get form.
        Returns:
            String: Post / Get request response. (Success)
            None: (Failure)
        '''

        igSigKey = '012a54f51c49aa8c5c322416ab1410909add32c966bbaa0fe3dc58ac43fd7ede'
        sigKeyVersion = '4'
        deviceProperties = {
            'manufacturer': 'Xiaomi',
            'model': 'HM 1SW',
            'android_version': 18,
            'android_release': '4.3'
        }

        self.rSession.headers.update({'Connection': 'close',
                                      'Accept': '*/*',
                                      'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                      'Cookie2': '$Version=1',
                                      'Accept-Language': 'en-US',
                                      'User-Agent': 'Instagram 9.2.0 Android ({android_version}/{android_release}; 320dpi; 720x1280; {manufacturer}; {model}; armani; qcom; en_US)'.format(**deviceProperties)
                                     })

        try:
            if postData is not None: # POST Request
                try:
                    parsedData = urllib.parse.quote(postData)
                except AttributeError:
                    parsedData = urllib.request.quote(postData)

                signedPostData = 'ig_sig_key_version=' + sigKeyVersion + '&signed_body=' + hmac.new(igSigKey.encode('utf-8'), postData.encode('utf-8'), hashlib.sha256).hexdigest() + '.' + parsedData
                reqResponse = self.rSession.post(self.urlAPI + endpoint, data=signedPostData)
            else: # GET Request
                reqResponse = self.rSession.get(self.urlAPI + endpoint, timeout=(5, 10))

            if reqResponse.status_code == 200 or reqResponse.status_code == 500:
                return reqResponse
            else:
                self.log("ERR: API Request Error (Failure). Code: %s." % (str(reqResponse.status_code)))
                return None
        except Exception as errorStr:
            self.log("ERR: API Request Exception (Failure). Exception Info: %s." % (str(errorStr)))
            return None

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
