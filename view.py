#Imports from 3rd parties
from flask          import Flask
from flask          import request
from flask          import Response
from flask          import jsonify
from flask          import make_response
from flask          import render_template
from flask          import redirect
from flask          import send_from_directory
from flask          import url_for

#Imports from this repository
from sheet_helpers  import init, create_sheet, append
from predict        import predict

INPUT_ACTION_SAVE_SUCCESS_MESSAGE = "Settings saved successfully."
app = Flask(__name__)

@app.route("/", methods=["GET"])
def task():
    """
        Root view for the flask app. Set cookies 
    """
    prompt_success          = request.cookies.get("prompt_success", "")
    prompt_failure          = request.cookies.get("prompt_failure", "")
    sheet_ready             = request.cookies.get("sheet_ready", "")
    sheet_link              = request.cookies.get("sheet_link", "")

    resp_kwargs             = {"prompt_success"     : prompt_success,
                            "prompt_failure"     : prompt_failure,
                            "sheet_ready"        : sheet_ready,
                            "sheet_link"         : sheet_link}
                   
    resp_output             = make_response(render_template("index.html", **resp_kwargs))  

    resp_output.set_cookie("prompt_success", "", expires=0)
    resp_output.set_cookie("prompt_failure", "", expires=0)
    resp_output.set_cookie("sheet_ready", "", expires=0)
    resp_output.set_cookie("sheet_link", "", expires=0)

    return resp_output

@app.route("/templates/<path:path>")
def send_templates(path):
    """
        Serving static asset content from /templates/
    """

    return send_from_directory("templates", path)

@app.route("/action/save", methods=["POST"])
def action_save():
    """
        Process the provided file and set the cookies for sheet url
    """
    sheet_name      = request.form["sheet_name"]
    image_file      = request.files["box_file"].read().decode("utf-8").split("\n")
    sheet_service   = init()
    sheet_id        = create_sheet(sheet_name, sheet_service)
    to_be_append    = predict(image_file)
    sheet_link      = "https://docs.google.com/spreadsheets/d/" + str(sheet_id)
    resp_output     = make_response(redirect("/"))


    append(sheet_id, sheet_service, to_be_append)
    resp_output.set_cookie("prompt_success", INPUT_ACTION_SAVE_SUCCESS_MESSAGE)
    resp_output.set_cookie("sheet_ready", "SHEET READY")
    resp_output.set_cookie("sheet_link", sheet_link)

    return resp_output

if __name__ == "__main__":
    app.run()