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
import networkx as nx 
import matplotlib.pyplot as plt
import numpy as np
import itertools
import pickle





class TumblrEngine():
    
    def __init__(self, apiDetails):
        self.OAuth_Consumer_Key = apiDetails["OAuth_Consumer_Key"] 
        self.OAuth_Consumer_Secret = apiDetails["OAuth_Consumer_Secret"]
        # Creating an instance for the TumblrRestClient class()
        self.tumblrClient = pytumblr.TumblrRestClient(self.OAuth_Consumer_Key)
        self.df = None
        self.df_json = None
        self.tagNames = ["bonespo", "thinner is better", "anor3×14", "tw ana diary", "m34nspo", "i wanna be weightless", "fatspo"]
        self.hashtags = ["bonespo", "thinner is better", "anor3×14", "tw ana diary", "m34nspo", "i wanna be weightless", "fatspo"]
        self.pairs = {pair: 0 for pair in itertools.combinations(self.tagNames, 2)}
        self.adjacency_matrix = np.zeros((len(self.tagNames), len(self.tagNames)))


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
                        "tags" : post["tags"]
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
    


    
    def generateAdjacencyMatrix(self, blogName, tagName, timestamp):

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
        for post in blogPosts:
            tags = post['tags']
            data[j] = {
                    "tag" : tagName,
                    "blog_name" : post["blog_name"],
                    "post_url" : post["post_url"],
                    "num_likes" : post["note_count"],
                    "tags" : post["tags"]
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

            pairs_in_post = {pair for pair in itertools.combinations(tags, 2) if pair in self.pairs}
            for pair in pairs_in_post:
                self.pairs[pair] += 1

        postList.append(data)

        for i, hashtag in enumerate(self.tagNames):
            for j in range(i+1, len(self.tagNames)):
                pair = (hashtag, self.tagNames[j])
                if pair in self.pairs:
                    self.adjacency_matrix[i, j] = self.pairs[pair]
                    self.adjacency_matrix[j, i] = self.pairs[pair]  # it's a symmetric matrix

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
        self.df.to_csv('./Data/TumblrData.csv', index=False)


    def generateDataFrame(self, jsonData):
        current_tag_name = jsonData[0]["tag"]
        df_json = pd.json_normalize(jsonData)
        df_json.to_csv(f"./Data/TumblrData_{current_tag_name}", index=False)
        print(f"Generated the CSV FIle: TumblrData_{current_tag_name} for the tag -> {current_tag_name} in Data Dir!")

        return (df_json, current_tag_name)
    


    def getAllTags(self, jsonData):
        
        networkOfTags = set()
        tagList = []

        for i in range(len(jsonData)):
            for tag in jsonData[i]["tags"]:
                networkOfTags.add(tag)

        for tag in networkOfTags:
            self.hashtags.append(tag)

        print("Generated a list of all the tags used in all the posts related to ED!")


    def getAdjacencyMat(self, jsonData):
        # Create a dictionary to keep track of pairs
        self.pairs = {pair: 0 for pair in itertools.combinations(self.hashtags, 2)}
        self.adjacency_matrix = np.zeros((len(self.hashtags), len(self.hashtags)))

        print("Iterating through the jsonData and populating the Adjacency Matrix ...")
        for i in range(len(jsonData)):
            pairs_in_post = {pair for pair in itertools.combinations(jsonData[i]["tags"], 2) if pair in self.pairs}
            for pair in pairs_in_post:
                self.pairs[pair] += 1

        for i, hashtag in enumerate(self.hashtags):
            for j in range(i+1, len(self.hashtags)):
                pair = (hashtag, self.hashtags[j])
                if pair in self.pairs:
                    self.adjacency_matrix[i, j] = self.pairs[pair]
                    self.adjacency_matrix[j, i] = self.pairs[pair]  # it's a symmetric matrix



    def drawNetworkHastags(self, jsonData, current_tag):

        networkOfTags = set()
        tagList = []
        for i in range(len(jsonData)):
            for tag in jsonData[i]["tags"]:
                networkOfTags.add(tag)

        for tag in networkOfTags:
            tagList.append({
                "current_tag" : current_tag,
                "new_tag": tag
            })

        df = pd.json_normalize(tagList)

        G = nx.from_pandas_edgelist(df, source='current_tag', target='new_tag', create_using=nx.DiGraph)

        # Set the figure size
        fig, ax = plt.subplots(figsize=(10, 8))

        # Customize the node and edge colors, sizes, and styles
        node_color = 'red'
        edge_color = 'blue'
        node_size = 200
        edge_width = 1
        node_shape = 'o'
        edge_style = 'dotted'

        # Draw the graph with labels
        nx.draw(G, with_labels=True, node_color=node_color, edge_color=edge_color,
                node_size=node_size, width=edge_width, node_shape=node_shape,
                style=edge_style)

        # Set the axis limits and turn off the axis labels
        ax.set_xlim([-1.2, 1.2])
        ax.set_ylim([-1.2, 1.2])
        ax.set_xticks([])
        ax.set_yticks([])

        # Add a title to the plot
        plt.title(f"Network of Hashtags --> {current_tag}")

        # Display the plot
        plt.show()

        # plt.savefig(f"./Plots/{current_tag}.png", dpi = 300, bbox_inches = "tight")


