import streamlit as st
from typing import List, Dict
import re
from openai import OpenAI
import os
from datetime import datetime

class HiringAssistant:
    def __init__(self):
        # Initialize session state
        if 'conversation_stage' not in st.session_state:
            st.session_state.conversation_stage = 'greeting'
        if 'candidate_info' not in st.session_state:
            st.session_state.candidate_info = {}
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
            
        # Get API key from Streamlit secrets or environment variable
        self.api_key = self.get_api_key()
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            st.error("OpenAI API key not found. Please set it up to continue.")
            st.stop()

    def get_api_key(self) -> str:
        """Get OpenAI API key from various sources."""
        # Try to get API key from Streamlit secrets
        try:
            return st.secrets["OPENAI_API_KEY"]
        except KeyError:
            pass
        
        # Try to get API key from environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            return api_key
        
        # If no API key is found, try to get it from session state or user input
        if 'openai_api_key' not in st.session_state:
            st.session_state.openai_api_key = None
            
        if st.session_state.openai_api_key is None:
            st.session_state.openai_api_key = st.text_input(
                "Enter your OpenAI API key:",
                type="password",
                help="Get your API key from https://platform.openai.com/account/api-keys"
            )
            
        return st.session_state.openai_api_key

    def get_system_prompt(self) -> str:
        """Generate the system prompt based on the current conversation stage."""
        base_prompt = """You are an AI hiring assistant for TalentScout, a technology recruitment agency. 
        Your role is to professionally and courteously interview candidates while gathering essential information.
        Maintain a friendly yet professional tone. Ask one question at a time.
        Current conversation stage: {stage}
        """
        
        stage_specific_prompts = {
            'greeting': "Greet the candidate warmly and introduce yourself as TalentScout's AI hiring assistant.",
            'name': "Ask for the candidate's full name politely.",
            'email': "Request the candidate's email address and ensure it's in a valid format.",
            'phone': "Ask for the candidate's phone number in a professional manner.",
            'experience': "Inquire about the candidate's years of professional experience.",
            'position': "Ask about the desired position they're interested in.",
            'location': "Ask about their current location.",
            'tech_stack': "Request their technical skills and experience, asking them to list their tech stack.",
            'questions': "Generate relevant technical questions based on their tech stack. Be thorough but not overwhelming."
        }
        
        return base_prompt.format(stage=st.session_state.conversation_stage) + "\n" + stage_specific_prompts.get(st.session_state.conversation_stage, "")

    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))

    def generate_technical_questions(self, tech_stack: List[str]) -> str:
        """Generate technical questions using LLM based on the candidate's tech stack."""
        prompt = f"""Generate 3-5 technical interview questions for each of the following technologies: {', '.join(tech_stack)}
        
        Requirements:
        1. Questions should assess both theoretical knowledge and practical experience
        2. Include a mix of basic and advanced concepts
        3. Focus on real-world applications and problem-solving
        4. Avoid overly generic questions
        5. Format the response clearly with technology names as headers
        
        Current tech stack: {tech_stack}"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical interviewer with expertise in various technologies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content

    def process_user_input(self, user_input: str) -> str:
        """Process user input using LLM based on the current conversation stage."""
        # Add user's message to conversation history
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        
        # Handle exit commands
        if user_input.lower() in ['exit', 'quit', 'bye']:
            st.session_state.conversation_stage = 'farewell'
            return "Thank you for your time! We will review your application and get back to you soon."

        # Create messages for LLM
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            *st.session_state.conversation_history
        ]

        # Get LLM response
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )
        
        llm_response = response.choices[0].message.content
        
        # Update conversation history
        st.session_state.conversation_history.append({"role": "assistant", "content": llm_response})
        
        # Update conversation stage based on current stage and validation
        if st.session_state.conversation_stage == 'email' and user_input:
            if not self.validate_email(user_input):
                return "Please provide a valid email address."
            st.session_state.candidate_info['email'] = user_input
            st.session_state.conversation_stage = 'phone'
            
        elif st.session_state.conversation_stage == 'phone' and user_input:
            if not self.validate_phone(user_input):
                return "Please provide a valid phone number."
            st.session_state.candidate_info['phone'] = user_input
            st.session_state.conversation_stage = 'experience'
            
        elif st.session_state.conversation_stage == 'tech_stack' and user_input:
            tech_stack = [tech.strip() for tech in user_input.split(',')]
            st.session_state.candidate_info['tech_stack'] = tech_stack
            st.session_state.conversation_stage = 'questions'
            return self.generate_technical_questions(tech_stack)
            
        # Update other stages
        stage_progression = {
            'greeting': 'name',
            'name': 'email',
            'experience': 'position',
            'position': 'location',
            'location': 'tech_stack'
        }
        
        if st.session_state.conversation_stage in stage_progression:
            st.session_state.conversation_stage = stage_progression[st.session_state.conversation_stage]
            
        return llm_response

def main():
    st.title("TalentScout Hiring Assistant")
    
    try:
        # Initialize the hiring assistant
        assistant = HiringAssistant()
        
        # Display conversation history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Initial greeting
        if not st.session_state.messages:
            greeting = assistant.process_user_input("start")
            with st.chat_message("assistant"):
                st.markdown(greeting)
            st.session_state.messages.append({"role": "assistant", "content": greeting})
        
        # Chat input
        if user_input := st.chat_input("Type your message here..."):
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            try:
                # Generate and display assistant response
                response = assistant.process_user_input(user_input)
                with st.chat_message("assistant"):
                    st.markdown(response)
                
                # Add assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error processing response: {str(e)}")
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please make sure you have provided a valid OpenAI API key.")

if __name__ == "__main__":
    main()