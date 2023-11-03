# Jingle Scribble

Jingle Scribble is a delightful Python application that generates handwritten Christmas cards for your customers. It utilizes an existing handwriting synthesis model from [sjvasquez/handwriting-synthesis](https://github.com/sjvasquez/handwriting-synthesis) and a user-friendly textual interface from [Textualize/textual](https://github.com/Textualize/textual).

## Requirements
- Python 3.7
- [Pipenv](https://pipenv.pypa.io/en/latest/)
- OpenAI API Token (exported in the local environment as `OPENAI_API_TOKEN`)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/jingle-scribble.git
   cd jingle-scribble
   ``````

1. Install dependencies using Pipenv and activate the virtual environment:  
    ```bash
    pipenv install --dev
    pipenv shell
    ```
1. Set up your OpenAI API Token:
    ```bash
    export OPENAI_API_TOKEN=your_openai_api_token
    ```

1. Run the application:
    ```bash
    python main.py
    ```

## Usage
1. Launch the application by running `python main.py`.
2. Follow the on-screen prompts to generate personalized handwritten Christmas cards for your customers.

## Credits
- Handwriting Synthesis Model: sjvasquez/handwriting-synthesis
- User Interface: Textualize/textual

## Contributing
Feel free to contribute to this project by opening issues or pull requests. We welcome any suggestions or improvements.

## License
This project is licensed under the GPL 3.

