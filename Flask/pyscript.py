from flask import Flask, render_template, jsonify
import time

# Initialize the Flask application
app = Flask(__name__)
print(app)
# --- YOUR SCRIPT'S LOGIC GOES HERE ---
# For this example, let's create a simple function that simulates your script's work.
# It could be anything: data processing, calculations, file operations, etc.
def run_my_script():
    """
    This function contains the core logic of your script.
    """
    print("Python script is now running...")
    # Simulate a task that takes 5 seconds
    time.sleep(5)
    result_data = {
        'status': 'Finished',
        'message': 'The Python script completed its task successfully!',
        'timestamp': time.ctime()
    }
    print("Python script has finished.")
    return result_data
# -----------------------------------------


# Route for the main page (serves the HTML)
@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')


# Route that the JavaScript will call to run your script
@app.route('/run-script')
def execute_script():
    """This endpoint runs your script and returns the result as JSON."""
    # Call the function that contains your script's logic
    result = run_my_script()
    # Return the result to the browser
    return jsonify(result)


# This is essential for running the app
if __name__ == '__main__':
    app.run(debug=True)