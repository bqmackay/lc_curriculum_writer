import praw
import time
import os
from decouple import config

from langchain.tools import tool
# from langchain.llms import Ollama
from crewai import Agent, Task, Process, Crew

from langchain.agents import load_tools

class BrowserTool:
    @tool("Scrape reddit content")
    def scrape_reddit(max_comments_per_post=7):
        """Usefule to scrape a reddit content"""
        print("opened reddit")
        reddit = praw.Reddit(
            client_id=config('REDDIT_CLIENT_ID'),
            client_secret=config('REDDIT_CLIENT_SECRET'),
            user_agent="user-agent",
        )
        subreddit = reddit.subreddit("iOSProgramming")
        scraped_data = []
        
        for post in subreddit.hot(limit=12):
            post_data = {"title": post.title, "url": post.url, "comments": []}

            try:
                post.comments.replace_more(limit=0)
                comments = post.comments.list()
                if max_comments_per_post is not None:
                    comments = comments[:7]
                
                for comment in comments:
                    post_data["comments"].append(comment.body)

                scraped_data.append(post_data)
            except praw.exceptions.APIException as e:
                print(f"API Exception: {e}")
                time.sleep(60)

        return scraped_data
    
def some_func():

    human_tools = load_tools(["human"])

    api = os.environ.get("OPENAI_API_KEY")

    writer = Agent(
        role="Curriculum Writer",
        goal="Write curriculum for full stack software engineers learning about generative AI and how to build products with it",
        backstory="""You are an seasoned writer for techincal documents. You are writing reading material that teaches other software engineers
        who may not have a lot of python experience how to become generative AI engineers. Your content focuses on presenting big overviews of why the particular topic
        is beneficial, and then you explain each component and present any fundamental coding syntax as you go. Your writing tone tends to be conversations, instructive, and humorous.
        """,
        verbose=True,
        allow_delegation=False,
    )

    editor = Agent(
        role="Curriculum Editor",
        goal="Edit reading material ensuring the text is instructive, doesn't have gaps that would be difficult to connect for intermediate students, and the examples are inclusive to all backgrounds.",
        backstory="""You are an expert editor with years of editing technical reading material. You are experienced in 4CID methodology, and understadn the importance of 
        whole task overviews to provide context to the learner. This reading should have a instructive, informative, encouraging, and occasionally humorous tone. """,
        verbose=True,
        allow_delegation=False,
    )

    sme = Agent(
        role="Generative AI Expert and SME",
        goal="Ensures that all material is technically accurate. Suggest edits back to the curriculum writer of things that need to be updated to be techincally accurate.",
        backstory="""
        You are an expert in generative AI and buildling AI products in production. Your background includes machine learning and full stack developing 
        leveraging mainly Python. You have built many generative AI products and have a sense for what is needed to make a full stack AI product work, and what skills are needed
        to do so.
        """,
        verbose=True,
        allow_delegation=False,
        tools=[BrowserTool().scrape_reddit] + human_tools,
    )

    task1 = Task(
        # Analyze job postings to determine what a software engineer needs to know to get a senior generative AI position. Write an outline of all the skills needed.
        description="""
        Gather the top five liked posts from the last week on reddit. For each post, go into the thread and get the top upvoted comments that are serious and not jokes. 
        Summarize your findings as if you were writting a newsletter.
        """,
        agent=sme
    )

    # task2 = Task(
    #     description="""Take the outline from task1 and write 
    #     """,
    #     agent=writer
    # )

    crew = Crew(
        agents=[writer, editor, sme],
        tasks=[task1],
        verbose=2,
        process=Process.sequential,
    )


    result = crew.kickoff()
    print("##################")
    print(result)
    return result


    

if __name__ == '__main__':
    # test1.py executed as script
    # do something
    some_func()