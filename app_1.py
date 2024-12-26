from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
import os
from bs4 import BeautifulSoup
import streamlit as st

# Streamlit App
st.title("HTML to Twig and SCSS Converter")

# Input OpenAI API Key
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def extract_css_and_replace_with_variables(css_content, variables_content):
        """Converts CSS styles to SCSS and replaces values with SCSS variables."""
        try:
            # Create a message for SCSS conversion and variable replacement
            message = [
                SystemMessage(
                    content=f"""You are a CSS-to-SCSS converter and variable replacer. Here is the task:
                    1. Use the following SCSS variables: \n{variables_content}
                    2. Replace all matching colors and fonts in the CSS with the SCSS variables.
                    3. Ensure the output SCSS is clean, modular, and maintains its functionality."""
                ),
                HumanMessage(content=css_content)
            ]

            # Generate SCSS response
            scss_response = llm(message)
            return scss_response.content
        except Exception as e:
            print(f"Error processing CSS to SCSS: {e}")
            return None

    def create_html_to_twig_conversion_message(html_content):
        """Generates a message to convert HTML content into Twig."""
        return [
            SystemMessage(
                content="""You are an HTML-to-Twig converter. I will provide you with an HTML file's content, and your task is to convert it into a Twig file. Ensure that:
                - All static text is replaced with meaningful Twig variables.
                - Dynamic content is wrapped using Twig's syntax (e.g., {{ variable }}).
                - Repeated elements use loops (e.g., {% for item in collection %}).
                - Conditional elements use Twig logic (e.g., {% if condition %}).
                - All attributes (e.g., href, src, alt) are dynamically handled where applicable.
                - Twig syntax is correctly validated and error-free.
                - The overall structure and styling of the HTML file remain intact.
                - Provide explanations of Twig variables in the following commented format:
                <!--
                ### Explanation of Twig Variables:
                - `{{ variable_name }}`: Description of the variable.
                -->"""
            ),
            HumanMessage(content=html_content)
        ]

    def convert_html_to_twig_with_scss(html_content, variables_content):
        """Converts an HTML file content into a Twig file and extracts SCSS styles."""
        # Extract SCSS from the HTML content
        scss_content = extract_css_and_replace_with_variables(html_content, variables_content)

        # Convert HTML to Twig
        messages = create_html_to_twig_conversion_message(html_content)
        try:
            twig_response = llm(messages)  # Send the messages to the LLM
            twig_content = twig_response.content
            return twig_content, scss_content
        except Exception as e:
            print(f"Error generating Twig or SCSS file: {e}")
            return None, None

    # File uploaders
    html_file = st.file_uploader("Upload HTML File", type=["html"], key="html_file")
    css_file = st.file_uploader("Upload CSS File (Optional)", type=["css"], key="css_file")
    variables_file = st.file_uploader("Upload SCSS Variables File", type=["scss"], key="variables_file")

    if (html_file or css_file) and variables_file:
        variables_content = variables_file.read().decode("utf-8")

        if html_file:
            html_content = html_file.read().decode("utf-8")
            twig_content, scss_content = convert_html_to_twig_with_scss(html_content, variables_content)

            if twig_content and scss_content:
                st.subheader("Twig Output")
                st.code(twig_content, language="twig")

                st.subheader("SCSS Output")
                st.code(scss_content, language="scss")

                st.download_button("Download Twig File", data=twig_content, file_name="output.twig", mime="text/plain")
                st.download_button("Download SCSS File", data=scss_content, file_name="styles.scss", mime="text/plain")

        if css_file:
            css_content = css_file.read().decode("utf-8")
            scss_content = extract_css_and_replace_with_variables(css_content, variables_content)

            if scss_content:
                st.subheader("SCSS Output from CSS")
                st.code(scss_content, language="scss")

                st.download_button("Download SCSS File", data=scss_content, file_name="styles_from_css.scss", mime="text/plain")
