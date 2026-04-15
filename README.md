## How to run the Nexus HR assistant chat 
```python chat_with_hr_assistant.py --query "What are the standard office hours?"```

### Examples
✅ Script started
💬The standard business hours at Nexus Innovations are from 9:00 AM to 5:00 PM, Monday through Friday. Punctuality and consistent attendance during these hours are essential for the company's collective success.


```python chat_with_hr_assistant.py --query "Can I eat ice cream at office?"```

✅ Script started
💬The policy documents do not specifically mention whether eating ice cream in the office is allowed. 

Generally, workplace guidelines emphasize maintaining a professional and clean environment. If you want to eat ice cream at your desk or in common areas, you may want to ensure it does not create messes or disrupt others. 

For a definitive answer, please check with your manager or Human Resources.


```python chat_with_hr_assistant.py --query "Can I borrow leaves?"      ```   

✅ Script started
💬The policy excerpts I have do not specifically mention the option to borrow leaves (i.e., taking leave in advance of accrual). For detailed information on borrowing leave or any exceptions to regular accrual use, please contact Human Resources directly. 

If you want, I can provide general best practices related to leave borrowing, but for Nexus Innovations’ exact rules, HR is the best resource.


```python chat_with_hr_assistant.py --query "What is the policy on Parental Leave?"```

✅ Script started
💬I don't have the details on Parental Leave in the policy excerpts I have. For your specific situation, please contact Human Resources. I couldn’t find the answer to your query, however according to my knowledge, many companies offer parental leave to support employees after the birth or adoption of a child, often including a certain number of paid or unpaid weeks. HR can provide you with Nexus Innovations' exact provisions if available.


 ```python chat_with_hr_assistant.py --query "How long can I avail sick leaves wihtout doctors receipt?"```

✅ Script started
💬According to the Nexus Innovations leave policy, employees must provide a doctor's note or other medical documentation for sick leave absences of three or more consecutive days, or for a pattern of absences that suggests verification is needed. Therefore, you can avail sick leave for up to two consecutive days without a doctor's receipt. For longer absences, medical documentation is required.

## How to run the app

```uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 8000```

```streamlit run streamlit_app.py```