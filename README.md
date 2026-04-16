Nexus HR Assist is an HR assistant chatbot designed for Nexus Innovations employees that uses Retrieval-Augmented Generation (RAG) technology. It is a full-stack application combining modern NLP/LLM capabilities with a web-based chat interface to make HR information easily accessible to employees through conversational AI.

## Implementation
The implementation of this intelligent chatbot system combines:
- RAG (Retrieval-Augmented Generation): Retrieves relevant HR information from a knowledge base and uses it to generate accurate, context-aware responses
- HR assistance: Helps employees with HR-related queries, policies, benefits, procedures, and other employee-related questions
- Conversational interface: Provides a chat-based interface for natural interaction

## Prerequisites

- Azure subscription
- Azure AI Foundry access enabled
- Python 3.9+

## Setup

- Create a Foundry hub project
- Create an Azure AI Search service and connect it to the hub project
- Create a `.env` file (copy from `.envcopy`) and populate the secrets
- Create a virtual environment and install the requirements
- Place documents for RAG retrieval under the `/assets` folder
- Run ingestion and document indexing:
  ```bash
  python create_search_index.py
  ```

## How to run the Nexus HR assistant chat on terminal
```bash
python chat_with_hr_assistant.py --query "<your question>"
```

### Examples

```bash
python chat_with_hr_assistant.py --query "What are the standard office hours?"
```

💬The standard business hours at Nexus Innovations are from 9:00 AM to 5:00 PM, Monday through Friday. Punctuality and consistent attendance during these hours are essential for the company's collective success.  


```bash
python chat_with_hr_assistant.py --query "Can I eat ice cream at office?"
```

💬The policy documents do not specifically mention whether eating ice cream in the office is allowed. 

Generally, workplace guidelines emphasize maintaining a professional and clean environment. If you want to eat ice cream at your desk or in common areas, you may want to ensure it does not create messes or disrupt others. 

For a definitive answer, please check with your manager or Human Resources.  


```bash
python chat_with_hr_assistant.py --query "Can I borrow leaves?"
```   

💬The policy excerpts I have do not specifically mention the option to borrow leaves (i.e., taking leave in advance of accrual). For detailed information on borrowing leave or any exceptions to regular accrual use, please contact Human Resources directly. 

If you want, I can provide general best practices related to leave borrowing, but for Nexus Innovations’ exact rules, HR is the best resource.  


```bash
python chat_with_hr_assistant.py --query "What is the policy on Parental Leave?"
```

💬I don't have the details on Parental Leave in the policy excerpts I have. For your specific situation, please contact Human Resources. I couldn’t find the answer to your query, however according to my knowledge, many companies offer parental leave to support employees after the birth or adoption of a child, often including a certain number of paid or unpaid weeks. HR can provide you with Nexus Innovations' exact provisions if available.  


```bash
python chat_with_hr_assistant.py --query "How long can I avail sick leaves wihtout doctors receipt?"
```

💬According to the Nexus Innovations leave policy, employees must provide a doctor's note or other medical documentation for sick leave absences of three or more consecutive days, or for a pattern of absences that suggests verification is needed. Therefore, you can avail sick leave for up to two consecutive days without a doctor's receipt. For longer absences, medical documentation is required.  

```bash
python chat_with_hr_assistant.py --query "Can you make some fashion recommendations??"
```

💬Nexus Innovations follows a business casual dress code, reflecting a professional and polished appearance suitable for our work environment. 

Here are some general fashion recommendations aligned with our dress code:
- For tops, consider button-down shirts, blouses, or neat sweaters.
- Pair these with slacks, chinos, or knee-length skirts.
- Avoid overly casual items such as ripped jeans, t-shirts, or athletic wear.
- Footwear should be clean and professional, like loafers, flats, or dress shoes.
- Keep accessories understated and appropriate for a professional setting.

If you need guidance specific to your role or office location, feel free to consult your manager or Human Resources.

## How to run the the Nexus HR assistant chat app

```bash
uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 8000

streamlit run streamlit_app.py
```
