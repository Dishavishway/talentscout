# TalentScout AI Hiring Assistant

An intelligent hiring assistant built with Streamlit and OpenAI's GPT-4, designed to conduct automated interviews with candidates.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Dishavishway/talentscout.git
cd talentscout
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
   - Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml`
   - Replace 'your-api-key-here' with your actual OpenAI API key
   - Never commit your actual API key to the repository

4. Run the application:
```bash
streamlit run hiring_assistant.py
```

## Features

- Interactive chat interface for conducting interviews
- Automated question generation based on candidate's tech stack
- Real-time validation of candidate information
- Progress tracking and conversation management
- Export functionality for interview data

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

