import time
from datetime import datetime
import vk_api
from configs.vktoken import vkTOKEN
from Bases.sqlExample import DataBase

vk_session = vk_api.VkApi(token=vkTOKEN)
vk = vk_session.get_api()
def getComm(id,post_id):
    id=id*-1
    return wall.getComments(owner_id=id,post_id=post_id)

def deleteposts(id):
    id = id * -1
    posts = vk.wall.get(owner_id=id, count=100)
    postsDel=000
    banwordsBase = DataBase('banwordsBase')
    banwords = banwordsBase.request('SELECT banword FROM banwords')
    for post in posts['items']:
        for banword in banwords:
            if (banword[0] in post['text']):
                vk.wall.delete(owner_id=id, post_id=post['id'])
                postsDel += 1
                b=1
                break

    return postsDel
def deletecomments(id):
    id = id * -1
    posts = vk.wall.get(owner_id=id, count=100)
    commDel=0
    banwordsBase = DataBase('banwordsBase')
    banwords = banwordsBase.request('SELECT banword FROM banwords')
    for post in posts['items']:
        comments = vk.wall.getComments(owner_id=id, post_id=post['id'])
        for comment in comments['items']:
            for banword in banwords:

                if (banword[0] in comment['text']):
                    vk.wall.deleteComment(owner_id=id, comment_id=comment['id'])
                    commDel += 1
    return commDel

