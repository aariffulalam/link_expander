# Link Expander API
This is a FastAPI-based project for expanding shortened URLs.

# Project Setup and Usage

## Development Environment

This project is configured to use a development container in Visual Studio Code. Follow the steps below to set up and run the application:

### Prerequisites
- Install [Visual Studio Code](https://code.visualstudio.com/).
- Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

### Steps to Set Up

1. **Open the Project in VS Code**
   - Clone the repository to your local machine.
   - Open the project folder in Visual Studio Code.

2. **Open in Dev Container**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS) to open the Command Palette.
   - Search for and select `Dev Containers: Reopen in Container`.

3. **Set Up Environment Variables**
   - Create a `.env` file in the root directory of the project.
   - Add the required environment variables to the `.env` file. 
   example:
     ```env
      AWS_DEFAULT_REGION=your-region
      AWS_ACCESS_KEY_ID=your-access-key-id
      AWS_SECRET_ACCESS_KEY=your-secret-access-key
      SNS_LEHLAH_EXPAND_EMAIL_ARN=your-sns-arn
     ```
4. **Install Dependencies**
   - Once inside the dev container, open a terminal in VS Code.
   - Run the following command to install the required dependencies:
     ```bash
     pip install -r requirements.txt
     ```

5. **Run the FastAPI Application**
   - Start the application using the following command:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
     ```
   - The application will be accessible at `http://127.0.0.1:8000` by default.

## Additional Information
- For more details on the project structure and functionality, refer to the source code and comments.
- If you encounter any issues, please check the logs or contact the project maintainers.