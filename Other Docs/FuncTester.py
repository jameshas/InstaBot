import time
from src import InstaPyAPI

IG = InstaPyAPI.InstaPyAPI()

IG.userLogin("user", "password")
time.sleep(5)

Likers = IG.getMediaLikers(1608440763589383838, 999999999)
print(len(Likers))
print(Likers[1])

time.sleep(5)
IG.userLogout()
