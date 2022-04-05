import logging
import random
import vk_api as vk

from environs import Env
from google.cloud import dialogflow
from vk_api.longpoll import VkLongPoll, VkEventType


LANGUAGE_CODE = "ru-RU"


def detect_intent_texts(project_id, session_id, text, language_code):
    """Returns the result of detect intent with texts as inputs.

    Using the same `session_id` between requests allows continuation
    of the conversation."""
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    if response.query_result.intent.is_fallback:
        return None
    else:
        return response.query_result.fulfillment_text


def echo(event, vk_api, project_id, session_id):
    bots_answer = detect_intent_texts(project_id, session_id,
                                      event.text, LANGUAGE_CODE)
    if bots_answer:
        vk_api.messages.send(
            user_id=event.user_id,
            message=bots_answer,
            random_id=random.randint(1,1000)
        )


if __name__ == '__main__':
    logging.basicConfig(
        format='%(levelname)s: %(name)s - %(message)s - %(asctime)s',
        level=logging.INFO)

    env = Env()
    env.read_env()

    vk_group_token = env.str('VK_TOKEN')
    project_id = env.str('PROJECT_ID')
    session_id = env.str('SESSION_ID')

    vk_session = vk.VkApi(token=vk_group_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api, project_id, session_id)










