import json

post = {
    "name": "мой пост вк",
    "post": "рандомный текст поста",
    "link_group": "https://vk.com",
}

def getPostsFromFile(filename):
    with open(filename, "r", encoding="utf-8") as openfile:
        json_posts = json.load(openfile)
    return json_posts


def savePostInFile(filename, post):
    posts = getPostsFromFile(filename)
    posts += [post]
    with open(filename, "w", encoding="utf-8") as outfile:
        json.dump(posts, outfile, ensure_ascii=False)

def savePostsInFile(filename, posts):
    with open(filename, "w", encoding="utf-8") as outfile:
        json.dump(posts, outfile, ensure_ascii=False)

def getPostById(filename, postId):
    posts = getPostsFromFile(filename)
    for i in range(len(posts)):
        if posts[i]['id'] == postId:
            return posts[i]
        
def changePostById(filename,post):
    posts = getPostsFromFile(filename)
    for i in range(len(posts)):
        if posts[i]['id'] == post["id"]:
            posts[i] = post
        
    savePostsInFile(filename,posts)

def deletePostById(filename,postId):
    posts = getPostsFromFile(filename)
    
    posts_filter = []
    for i in range(len(posts)):
        if posts[i]['id'] != postId:
            posts_filter.append(posts[i])

    savePostsInFile(filename,posts_filter)