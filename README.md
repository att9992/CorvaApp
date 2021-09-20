Minimum Curvature Well Trajectory App
==========================
## Create a Virtual Environment

After cloning or downloading the repo, create a Python virtual environment with:

```
python -m venv .env
```

This will create the virtual environment in the project directory as `.env`
## Activate the Virtual Environment

Now activate the virtual environment. On macOS, Linux and Unix systems, use:

```
source .env/bin/activate
```

On Windows with `cmd.exe`:

```
.env\Scripts\activate.bat
```

Or Windows with PowerShell:

```
.\.env\Scripts\activate.ps1
```

## Install the dependencies 

Use `requirments.txt` file to install dependencies:

```
pip install -r requirements.txt
```

## Run app locally

Run the app locally:

```
streamlit run app.py
```