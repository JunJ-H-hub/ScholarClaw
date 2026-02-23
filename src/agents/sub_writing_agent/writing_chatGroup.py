from src.core.model_client import create_default_client
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from src.agents.sub_writing_agent.writing_agent import create_writing_agent
from src.agents.sub_writing_agent.retrieval_agent import create_retrieval_agent
from src.agents.sub_writing_agent.review_agent import create_review_agent
from src.core.prompts import selector_prompt

def create_writing_group():
    model_client = create_default_client()

    text_termination = TextMentionTermination("APPROVE")
    
    writing_agent = create_writing_agent()
    review_agent = create_review_agent()
    retrieval_agent = create_retrieval_agent()

    task_group = SelectorGroupChat(
        [writing_agent,retrieval_agent,review_agent],
        model_client=model_client,
        termination_condition=text_termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=False,  # Allow an agent to speak multiple turns in a row.
    )
    return task_group
