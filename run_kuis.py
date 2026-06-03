import sys
from streamlit.web import cli  # type: ignore

if __name__ == '__main__':
    # Force execution of app.py with Streamlit args
    sys.argv = ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
    sys.exit(cli.main())
