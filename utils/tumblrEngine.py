'''
Author : Sudesh Kumar S
GitHub: https://github.com/sudeshkumarsk
email: sudesh.skofficial@gmail.com / santhosh@usc.edu
Project Name : Auditing Web Content to identify Eating Disorders
Developed with python 3.8 using Conda virtual environment

'''

# Importing all necessary packages and libraries
import pytumblr
from bs4 import BeautifulSoup
import pandas as pd


class TumblrEngine():
    
    def __init__(self, apiDetails):
        self.OAuth_Consumer_Key = apiDetails["OAuth_Consumer_Key"] 
        self.OAuth_Consumer_Secret = apiDetails["OAuth_Consumer_Secret"]
        # Creating an instance for the TumblrRestClient class()
        self.tumblrClient = pytumblr.TumblrRestClient(self.OAuth_Consumer_Key)
        self.df = None


    # User-defined function to extract blog_name and id for the top 20 posts that come up from the passed timestamp.
    def getTaggedPostsUserData(self, tagName, timestamp):

        taggedPosts = ""
        result = {
            "status" : False,
            "response" : "",
            "length" : 0,
            "timestamp" : 0
        }

        if timestamp:
            taggedPosts = self.tumblrClient.tagged(tagName, before=timestamp)

        else:
            taggedPosts = self.tumblrClient.tagged(tagName)



        if len(taggedPosts) == 0:
            return result
        
        data = {}
        for i, post in enumerate(taggedPosts):
            data[i] = {
                "blog_name" : post["blog_name"],
                "user_id" : post["id"]
            }



        result["status"] = True
        result["length"] = len(taggedPosts)
        result["response"] = data
        result["timestamp"] = taggedPosts[-1]["timestamp"] - 1

        return result



    def getPostsData(self, blogName, tagName, timestamp):
        blogPosts = ""
        totalPosts = 0
        result = {
            "status" : False,
            "response" : "",
            "length" : 0,
            "timestamp" : 0
        }

        if timestamp:
            blogPosts = self.tumblrClient.posts(blogname = blogName, tag = tagName, before = timestamp, reblog_info=True, notes_info = True)

        else:
            blogPosts = self.tumblrClient.posts(blogname = blogName, tag = tagName, reblog_info=True, notes_info = True)
           
        if len(blogPosts) == 0:
            return result
        
        postList = []
        data = {}
        
        j = 0
        if ('posts' in blogPosts):
            for _, post in enumerate(blogPosts['posts']):
                if ('reblogged_from_id' in post):
                    data[j] = {
                        "tag" : tagName,
                        "blog_name" : post["blog_name"],
                        "post_url" : post["post_url"],
                        "num_likes" : post["note_count"],
                        # "content" : post["trail"][0]["content"]
                    }

                    num_replies = 0
                    for note in post['notes']:
                        if note['type'] == 'reply':
                            num_replies += 1

                    num_reblogs = 0
                    for note in post['notes']:
                        if note['type'] == 'reblog':
                            num_reblogs += 1

                    data[j]["num_replies"] = num_replies
                    data[j]["num_reblogs"] = num_reblogs
                    
                    if post['type'] == 'text':
                        # content = post['body']
                        content_html = post['body']
                        content_text = BeautifulSoup(content_html, 'html.parser').get_text()
                        content = content_text
                    elif post['type'] == 'photo':
                        # content = post['caption']
                        caption_html = post['caption']
                        caption_text = BeautifulSoup(caption_html, 'html.parser').get_text()
                        content = caption_text
                    else:
                        content = None  # Other types of posts are not supported

                    data[j]["content"] = content
                    j += 1
                    totalPosts += 1
                else:
                    pass
            postList.append(data)
            

        else:
            return result
        
        if len(postList[0]):
            result["status"] = True
            result["length"] = totalPosts
            result["response"] = postList        

        return result
    
    def initializeDataFrame(self):
        # Define the column names
        column_names = ["S.No", 'tagName', "blogName", 'postUrl', 'numLikes', 'numReplies', "numReblogs", 'content']

        # Create an empty dictionary with the column names as keys and empty lists as values
        data = {col_name: [] for col_name in column_names}

        # Create the DataFrame from the dictionary
        df = pd.DataFrame(data)

        self.df = df
    
    def createDataFrame(self, jsonData):
        
        for index, data in enumerate(jsonData):
            self.df = self.df.append({"S.No" : index+1, 'tagName': data["tag"], "blogName": data["blog_name"], 'postUrl': data["post_url"], 'numLikes': data["num_likes"], 'numReplies': data["num_replies"], "numReblogs" : data["num_reblogs"], 'content': data["content"]}, ignore_index=True)
            

        # Write the DataFrame to a CSV file
        self.df.to_csv('./TumblrData.csv', index=False)