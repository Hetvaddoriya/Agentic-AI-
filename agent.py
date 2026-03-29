from langchain.chat_models import ChatOpenAI

def get_response(user_input):
    llm = ChatOpenAI(temperature=0)

    prompt = f"""
    You are a smart timetable assistant.
    Help user schedule tasks, find free time, or manage study.

    User: {user_input}
    """

    return llm.predict(prompt)