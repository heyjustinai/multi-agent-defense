import streamlit as st
import requests
import base64
from dotenv import load_dotenv
import os
# Set page title and header
st.title("OpsAI: War Audio Transcription & Translation")

print(os.getenv("GROQ_API_KEY"))  # Should print the key

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print("API Key:", api_key)

uploaded_files = st.file_uploader("Choose a files", accept_multiple_files=True)

if uploaded_files:
    file_data_list = []
    for uploaded_file in uploaded_files:
        audio_data = uploaded_file.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        file_data_list.append((uploaded_file.name, audio_base64))

if "response_history" not in st.session_state:
    st.session_state.response_history = []

if st.button("Process Audio"):
    if uploaded_files:  # Ensure files are uploaded
        try:
            with st.spinner('Processing audio...'):
                response = requests.post(
                    "http://localhost:8000/api/process_audio",
                    json={"file_data": file_data_list}
                )

                if response.status_code == 200:
                    st.success("Processing audio was successful!")

                    results = response.json()["result"]
                    for idx, uploaded_file in enumerate(uploaded_files):
                        transcription = results[idx]['transcription']
                        translation = results[idx]['translation']

                        # Add to session state history
                        st.session_state.response_history.append({
                            "file_name": uploaded_file.name,
                            "file_type": uploaded_file.type,
                            "transcription": transcription,
                            "translation": translation
                        })

                        # Define output filename for translation text file
                        output_filename = f"{uploaded_file.name}_translation.txt"

                        # Save translation to .txt file
                        with open(output_filename, "w", encoding="utf-8") as f:
                            #f.write(f"Transcription:\n{transcription}\n\n")
                            f.write(f"Translation:\n{translation}")

                        # Provide a download button for the generated file
                        with open(output_filename, "rb") as file:
                            st.download_button(
                                label="Download Translation",
                                data=file,
                                file_name=output_filename,
                                mime="text/plain"
                            )
                        st.info(f"Translation saved to {output_filename}")

                else:
                    st.error(f"Error: {response.status_code}")

        except requests.exceptions.ConnectionError as e:
            st.error(f"Failed to connect to the server. Make sure the FastAPI server is running.")
    else:
        st.warning("Please upload a file before submitting.")


# if st.button("Process Audio"):
#     if uploaded_file:
#         try:
#             with st.spinner('Processing audio...'):
#                 response = requests.post(
#                     "http://localhost:8000/api/process_audio",
#                     json={"file_data": file_data_list}
#                 )

#                 if response.status_code == 200:
#                     st.success("Processing audio was successful!")

#                     results = response.json()["result"]
#                     for idx, uploaded_file in enumerate(uploaded_files):
#                         st.session_state.response_history.append({
#                             "file_name": uploaded_file.name,
#                             "file_type": uploaded_file.type,
#                             "transcription": results[idx]['transcription'],
#                             "translation": results[idx]['translation']
#                     })
#                 else:
#                     st.error(f"Error: {response.status_code}")

#         except requests.exceptions.ConnectionError as e:
#             st.error(f"Failed to connect to the server. Make sure the FastAPI server is running.")
#     else:
#         st.warning("Please upload a file before submitting.")

# if st.session_state.response_history:
#     st.subheader("Audio Processing History")
#     for i, item in enumerate(st.session_state.response_history, 1):
#         st.markdown(f"**Run {i}:**")
#         st.markdown(f"**File Name:** {item['file_name']}")
#         st.markdown(f"**File Type:** {item['file_type']}")
#         st.markdown(f"**Transcription:** {item['transcription']}")
#         st.markdown(f"**Translation:** {item['translation']}")
#         st.markdown("---")
        