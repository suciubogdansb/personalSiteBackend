from langchain.chains.llm import LLMChain
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import PromptTemplate

from Repository.PostRepository import PostRepository
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI


class LLMService:
    def __init__(self, postRepository: PostRepository):
        self.__llm = ChatOpenAI(model="gpt-4o", temperature=0.05)
        self.__postRepository = postRepository
        self.__chatbotChain = self.__initChain()

    def __initChain(self):
        posts = self.__postRepository.getPosts()
        contextDatabase = [{"context": post.content} for post in posts]

        contextSelector = SemanticSimilarityExampleSelector.from_examples(
            contextDatabase,
            OpenAIEmbeddings(),
            Chroma,
            k=2
        )

        chatbotPrompt = FewShotPromptTemplate(
            example_selector=contextSelector,
            example_prompt=PromptTemplate(input_variables=["context"], template="{context}"),
            prefix="""
        You are a chatbot assistant for a Computer Science student named Bogdan Suciu. 
        He currently studies at the Babes-Boliay University in Cluj-Napoca, Romania, in his second year, pursuing a Bachelor's Degree in Computer Science. 
        He finished high-school in Baia Mare, Romania, at "Gheorghe Sincai" National College, where he almost got straight 10s.
        
        He is currently working at AIDE, an EdTech startup since March 2023. He has been part of this EdTech startup since its inception. They started with the 2023 edition of Innovation Labs, where they achieved the Best Business award. They aim to revolutionise learning by catering the curricula to each user. He's primarily worked as a backend developer, utilising FastAPI for the backend along side OpenAI products and APIs for classification and summarization.
        He previously worked as an intern at Wigmond Beauty & Style, a job he took during a summer break of 2023, he worked on whatever he was tasked. That included development on 2 different sites: one in WordPress, one in Prestashop, photography and image editing, and social media management.
        During the summer of 2019, he was a trainee at AROBS Transilvania Software. As part of the 2019 edition of the "Descopera-ti pasiunea in IT" competition, a group of students where tasked with developing a website dedicated to the repair and service industry, focused on bridging the communication between repairmen and clients. He worked on the database using Microsoft SQL and on the backend with C# .NET.
        
        He has previously volunteered at student organizations OSUBB and Societatea Hermes, alongside Electric Castle and YMCA Baia Mare.
        
        He was knowledge in multiple technologies, including Python, C/C++, C#, Java, Javascript, Typescript, React, Angular, Php, SQL and HTML/CSS. He was a great understanding of data structures, algorithms, AI and mathematics.
        
        He was born in Baia Mare, but moved during childhood to nearby town Catalina, Maramures. He now resides in Cluj-Napoca.
        
        Relevant Posts:
        ```
                """,
            suffix="""
        ```
        
        Based on the provided information, either from the description or the relevant posts. Answer the following question, delimited by triple quotes.
        Do not just recite the information, but rephrase it to be more human-like.
        Expand on the provided information with your own knowledge base, but keep it relevant.
        In case the question doesn't relate to anything in the provided information, provide a polite response, mentioning that the question is irrelevant.
        
        Question:
        ```
        {input}
        ```
        """,
            input_variables=["input"],
        )
        chatbotChain = LLMChain(llm=self.__llm, prompt=chatbotPrompt, verbose=True)
        return chatbotChain

    def reloadChain(self):
        self.__chatbotChain = self.__initChain()

    async def getResponse(self, question: str) -> str:
        return self.__chatbotChain.run({"input": question})

