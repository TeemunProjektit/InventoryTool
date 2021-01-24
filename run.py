# Import app object from the app module
from app import app

# Special variable __name__, launches the module only if it's executed as the main method.
# If imported, module is not launched automatically.
if __name__ == '__main__':
    app.run(debug=True)