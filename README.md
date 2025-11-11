<div align="center">
  
  # 🧠 AIChatbot
  ### An advanced AI chatbot built with Django, Groq & OpenAI
</div>

An advanced AI chatbot application built using **Django**, integrating **Groq** and **OpenAI** models with tool calling capabilities such as web search, weather updates, and news retrieval.  
This project also includes user authentication, admin account management, and chat management functionalities.

---

## 🚀 Features

- 🔐 **User Authentication** — Secure signup and login system.  
- ✉️ **SMTP Mail Notifications** — Email alerts for account activation and important actions.  
- 🧑‍💼 **Admin Control** — Admin can accept or cancel user account activation requests.  
- 💬 **Chat Management** — Users can rename or delete their chat conversations.  
- 🤖 **AI Model Integration** — Supports **Groq** and **OpenAI** models for chatbot responses.  
- 🧰 **Tool Calling** — Integrates real-time tools like:
  - 🌐 Web Search  
  - ☀️ Weather Information  
  - 📰 News Updates  

---

## ⚙️ Installation and Run Application

Follow these steps to set up and run the Django chatbot application.

### **Step 1: Create and Activate Virtual Environment**

Create a virtual environment to isolate dependencies.
```bash
python -m venv venv
venv\Scripts\activate
```

### **Step 2: Clone the Repository**

Clone this repository from GitHub:
```bash
git clone https://github.com/Nirusanan/AIChatBot-Django.git
cd AIChatbot-Django
```

### **Step 3: Install Requirements**

Install the necessary dependencies.
```bash
pip install -r requirements.txt
```

### **Step 4: Create .env File**

Create a .env file in the project root directory and add your API key:
```bash
GROQ_API_KEY=your_groq_secret_key_here
OPENAI_API_KEY=your_openai_secret_key_here
SERPER_API_KEY=your_serper_secret_key_here
WEATHER_API_KEY=your_openweatherAPI_secret_key_here
EMAIL_HOST_USER=your_gmail
EMAIL_HOST_PASSWORD=your_gmail_app_passowrd_16_character
```

✅ Create Gmail App Password

🪪 Step 1 — Turn on 2-Step Verification

  * Go to 👉 https://myaccount.google.com/security
  * Under “Signing in to Google”, click “2-Step Verification”
  * Turn it ON

🔑 Step 2 — Generate App Password

Once 2-Step Verification is enabled:
  * Go again to 👉 https://myaccount.google.com/security
  * Under “Signing in to Google”, click “App passwords”
  * Re-enter your Google account password
  * Under Select app, choose Mail
  * Under Select device, choose Other (Custom name) → type Django → click Generate
  * Copy the 16-character app password

### **Step 5: Create Database Tables**

Run the following commands to create the required tables:
```bash
python manage.py makemigrations chatbot_app
python manage.py migrate
```

### **Step 6: Create a Superuser**

To access the admin panel and manage user activations, create a superuser:
```bash
python manage.py createsuperuser
```

### **Step 7: Run the Application**

Start the Django development server:
```bash
python manage.py runserver
```

Then visit:
👉 http://127.0.0.1:8000/

You can create your account via the signup page and log in with your credentials.

---

## 🧑‍💼 Accessing the Superuser Dashboard

Once your superuser account is created, visit:

👉 http://127.0.0.1:8000/admin/

Log in using the credentials you created with createsuperuser.
From here, you can:
* Approve or cancel new user activations.
* Manage chat records.
* Oversee chatbot activity and user details.

---

🧩 License

This project is licensed under the MIT License.
