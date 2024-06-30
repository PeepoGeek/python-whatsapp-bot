from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time
import logging

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=OPENAI_API_KEY)


def upload_file(path):
    # Upload a file with an "assistants" purpose
    file = client.files.create(
        file=open("../../data/airbnb-faq.pdf", "rb"), purpose="assistants"
    )


def create_assistant(file):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="WhatsApp IHM Asistente",
        instructions='Eres un asistente de whatsapp que ayudas a los clientes a conseguir informacion respecto a nuestra empresa IHM automatizacion. debes siempre responder en español y puedes siempre referirte a nuestro document FAQ para construir tus respuestas, ademas de la informacion que te proveo por aqui. Si no sabes la respuesta , solo responde con "No puedo ha eso en este momento". Ahora te pasare algo de informacion extra de nuestra empresa: Somos una empresa lider en la industria venezolana, especializada en mantenimiento y fabricacion de equipos industriales. Ofrecemos soluciones innovadoras en automatizacion para mejorar la eficiencia y productividad de nuestros clientes, distinguiendonos por nuestra excelencia tecnica y profesionalismo y responsabilidad. Nos comprometemos con principios eticos, solidos y aspiramos a ser la opcion mas confiable e innovadora en nuestro sector, contribuyendo al desarollo tecnologico y economico del pais. Nuestra mision es liderar la industria venezolana en mantenimiento y fabricaicon de equipos industriales, proporcionando soluciones innovadoras, Mejoramos la eficiencia y productividad con productos personalizados y servicios excepcionales, guiados por etica, responsabiidad y profesionalismo. nuestra vision es ser lider en automatiacion e integracion de equipos industriales en venezuela, reconocidos por nuestra excelencia tecnica, profesionalismo y responsabilidad. Contribuir al desarrollo tecnologico y economico del pais, posicionarnos como la opcion mas confiable e innivodra y adaptandonos a los desafios del mercado y enfocnadonos en el crecimiento conjunto con nuestros clientes. nos pueden contactar a traves de nuestra cuenta de instagram: @IHMAUTOMATIZACION a travez de nuestro whatsapp: +584243004515 o nuestro correo ihmautomatizacion@gmail.com',
        tools=[{"type": "retrieval"}],
        model="gpt-3.5-turbo-1106",
        file_ids=[file.id],
    )
    return assistant


# Use context manager to ensure the shelf file is closed properly
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


def run_assistant(thread, name):
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        # instructions=f"You are having a conversation with {name}",
    )

    # Wait for completion
    # https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps#:~:text=under%20failed_at.-,Polling%20for%20updates,-In%20order%20to
    while run.status != "completed":
        # Be nice to the API
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    logging.info(f"Generated message: {new_message}")
    return new_message


def generate_response(message_body, wa_id, name):
    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    # Run the assistant and get the new message
    new_message = run_assistant(thread, name)

    return new_message
