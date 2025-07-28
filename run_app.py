import streamlit.web.cli as stcli
import os
import sys

if __name__ == "__main__":
    # Determine the path to app.py within the PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        bundle_dir = sys._MEIPASS
    else:
        # Running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    app_path = os.path.join(bundle_dir, "app.py")

    # Set the STREAMLIT_SERVER_SCRIPT_PATH environment variable
    # This tells Streamlit where to find the main script within the bundle
    os.environ["STREAMLIT_SERVER_SCRIPT_PATH"] = app_path
    
    # Streamlit will now find the script via the environment variable
    # We need to pass the script path as a TARGET argument as well
    sys.argv = [
        "streamlit",
        "run",
        app_path, # Add app_path back as the TARGET argument
        "--global.developmentMode=false",
    ]
    
    # Run streamlit
    os.environ["STREAMLIT_SERVER_MAX_UPLOAD_SIZE"] = "5120"
    sys.exit(stcli.main())