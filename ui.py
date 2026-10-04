from nicegui import ui
import requests

API_URL = "http://localhost:8005"

questions = []
page_body = ui.column()

def api_get(path):
    try:
        # Attempt to send GET request to API
        response = requests.get(f"{API_URL}{path}", timeout=5)
        # If we get an error code back, raise an exception
        response.raise_for_status()
        # Otherwise, GET was successful so return response data
        return response.json()
    except requests.RequestException as e:
        # GET request was unsuccessful
        # Send an alert with error details to the UI and return empty list
        ui.notify(f"Could not reach API: {e}", type="negative")
        return []

def api_post(path, data):
    try:
        # Attempt to send POST request to API with data payload
        response = requests.post(f"{API_URL}{path}", json=data, timeout=5)
        # If we get an error code back, raise an exception
        response.raise_for_status()
        # Otherwise, POST was successful so return True
        return True
    except requests.RequestException as e:
        # POST request was unsuccessful
        # Send an alert with error details to the UI and return False
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False

# TODO: Create api_delete function that attempts to send a DELETE request to the API.
# The request method should use the string f"{API_URL}{path}/{id}" to access the correct path,
# where id refers to the id number of the question to be deleted. 
def api_delete(path, id):
    try:
        response = requests.delete(f"{API_URL}{path}/{id}", timeout=5)
        
        response.raise_for_status()
        
        return response.json()
    except requests.RequestException as e:      
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False


# TODO: Create api_put function that attempts to send a PUT request to the API.
# The request method should use the string f"{API_URL}{path}/{id}" to access the correct path,
# where id refers to the id number of the question to be deleted. The data passed as an argument
# to this function must be sent with the request so that the API knows the updated values to add 
# to the dataset (similar to how data is sent in api_post).
def api_put(path, id, data):
    try:
        response = requests.put(f"{API_URL}{path}/{id}", json=data, timeout=5)
        
        response.raise_for_status()

        return response.json()
    except requests.RequestException as e:
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False

# TODO: Add edit and delete buttons dynamically to each question card. 
def render_question(question):
    with ui.card() .classes("cursor-pointer hover:bg-blue-100/50") as card:
        card.on("click", lambda: toggle_answer(question["id"]))
        ui.label("Question:").classes("font-bold")
        ui.label(question["q"])
        ui.label("Answer:").classes("font-bold").bind_visibility_from(question["state"], "show_answer")
        ui.label(question["a"]).classes("text-green font-bold").bind_visibility_from(question["state"], "show_answer")

        with ui.row():
            ui.button("Edit", on_click=lambda: open_edit_dialog(question), color="primary")
            ui.button("Delete", on_click=lambda: delete_question(question["id"]), color="negative")

def delete_question(id):
    if (api_delete("/delete", id)):
        render_page()

def open_edit_dialog(question):
    with ui.dialog() as dialog, ui.card():
        ui.label("Edit Question")
        new_q = ui.textarea(label="Question", value=question["q"])
        new_a = ui.textarea(label="Answer", value=question["a"])
        
        with ui.row():
            ui.button("Cancel", on_click=dialog.close, color="grey-7")
            ui.button('Update question', color="positive", on_click=lambda: [
                dialog.close(),
                api_put("/update", question["id"], {
                    "question": new_q.value,
                    "answer": new_a.value
                }),
                render_page()
            ])
    dialog.open()

def toggle_answer(id):
    # since now deleting, id will be different then the index of questions
    for question in questions:
        if question["id"] == id:
            question["state"]["show_answer"] = not question["state"]["show_answer"]

def add_new_question(question, answer):
    api_post("/add", {"question": question, "answer": answer})
    render_page()

def render_text_inputs():
    ui.label("Add Question").classes("text-xl font-bold")
    with ui.card():
        new_question_input = ui.input(label="New question").props("clearable")
        new_answer_input = ui.input(label="New answer").props("clearable")
        add_question_btn = ui.button(text="Add question", on_click=lambda: add_new_question(
            question=new_question_input.value,
            answer=new_answer_input.value
        )).classes("bg-green text-white")

def init_page():
    render_page()

def render_page():
    global questions
    questions = api_get("/questions")
    page_body.clear()
    with page_body:
        with ui.row():
            with ui.column():
                ui.label("All Questions").classes("text-xl font-bold")
                with ui.card() as card:
                    for question in questions:
                        question["state"] = {"show_answer": False}
                        render_question(question)
            with ui.column():
                render_text_inputs()
    

init_page()
ui.run(port=8084, title="HCI Review Application")