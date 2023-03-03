'''
Author : Sudesh Kumar S.
GitHub: https://github.com/sudeshkumarsk
email: sudesh.skofficial@gmail.com / santhosh@usc.edu
Project Name : Auditing Web Content to identify Eating Disorders.
Developed with python 3.8 using Conda virtual environment.

'''

# Importing all necessary packages and libraries
import pytumblr

# The main tumblrEngine() which can be used to scrap data from tumblr micro-blogging site
class TumblrEngine():
    
    def __init__(self, apiDetails):
        self.OAuth_Consumer_Key = apiDetails["OAuth_Consumer_Key"] 
        self.OAuth_Consumer_Secret = apiDetails["OAuth_Consumer_Secret"]
        # Creating an instance for the TumblrRestClient class()
        self.tumblrClient = pytumblr.TumblrRestClient(self.OAuth_Consumer_Key)


    # User-defined function to extract blog_name and id for the top 20 posts that come up from the passed timestamp.
    def getTaggedPostsUserData(self, tagName, timestamp):

        # The response object to be returned when we don't find any blogs with the passed tag name.
        result = {
            "status" : False,
            "response" : "",
            "length" : 0,
            "timestamp" : 0
        }

        # Finding posts with the tag passed by the user.
        taggedPosts = self.tumblrClient.tagged(tagName, before=timestamp)

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
        result["timestamp"] = taggedPosts[-1]["timestamp"]

        return result



    def getPostsData(self, blogName, id):
        pass
