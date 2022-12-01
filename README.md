## Instructions

1. Clone the repo.
2. Run `bash run_app.sh` in the root directory. This will create the Docker image, container, and start the container.
3. Enter the directory you want to be the root. 
3. Navigate to `localhost:8080` to view and use the API. 

## Testing
For now, this can only be run locally. 

1. Create a virtual environment. 
2. Run `pip install -r requirements.txt`
3. Uncomment `root_file_path = "test_root"` in `main.py`.
4. Run `pytest`
