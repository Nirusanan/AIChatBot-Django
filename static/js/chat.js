let new_chat_state = true;

window.addEventListener('beforeunload', function () {
    console.log('Page is being reloaded or closed');
    startNewChat()
});

window.addEventListener('load', function () {
    console.log('Page is newly opened or reloaded');
    startNewChat()
});

window.MathJax = {
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: true,
        packages: { '[+]': ['noerrors', 'newcommand', 'boldsymbol', 'ams'] }
    },
    svg: {
        fontCache: 'global'
    },
    loader: {
        load: ['[tex]/ams']
    }
};


$(document).ready(function () {
    console.log("Logout.js is loaded");
    console.log("Logout URL:", logoutUrl);
    console.log("Login URL:", loginUrl);
    $('#logoutButton').click(function (event) {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: logoutUrl,
            data: {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function () {
                window.location.href = loginUrl; 
            },
            error: function () {
                alert('Logout failed. Please try again.');
            }
        });
    });
});


// Function to get the CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to load chat details
function loadChatDetails(chatId) {
    fetch(`/api/chat/${chatId}/`)
        .then(response => response.json())
        .then(data => {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = '';
            data.conversation.forEach(message => {
                // Check role to append properly, assistant -> bot-message 
                const messageType = message.role === "user" ? 'user-message' : 'bot-message';
                appendMessage(message.content, messageType);
            });
        })
        .catch(error => console.error('Failed to fetch chat details:', error));
}


function display_previous_chat() {
    fetch('/api/chat_id_title/')
        .then(response => response.json())
        .then(data => {
            const labelsList = document.getElementById('labelsList');
            labelsList.innerHTML = ''; 

            // Sort the data by chat_id in descending order
            data.sort((a, b) => b.chat_id - a.chat_id);

            data.forEach(chat => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.textContent = chat.chat_title;
                a.href = "#";
                a.setAttribute('data-chat-id', chat.chat_uuid);
                a.addEventListener('click', function (e) {
                    e.preventDefault();
                    console.log(chat.chat_uuid);
                    loadChatDetails(chat.chat_uuid);
                });
                li.appendChild(a);
                labelsList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error fetching chat titles:', error);
        });
}


function startNewChat() {
    document.getElementById('chatMessages').innerHTML = '';

    // Send the special message to clear the conversations on the server
    $.ajax({
        url: '/api/chat/',
        method: 'POST',
        data: {
            message: 'New chat',
        },
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function (data) {
            console.log('Chat session reset successfully.');
            display_previous_chat();
            new_chat_state = true;
        },
        error: function (xhr) {
            console.error('Error resetting chat session: ' + xhr.statusText);
        }
    });

    // Optionally: Clear the userInput field
    document.getElementById('userInput').value = '';

}


// Event listener for chat title clicks
document.addEventListener('DOMContentLoaded', function () {
    const chatLinks = document.querySelectorAll('#labelsList a');
    chatLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault(); // Prevent the link from triggering a page reload
            const chatId = this.getAttribute('data-chat-id');
            loadChatDetails(chatId);
        });
    });
});


function sendMessage() {
    var input = document.getElementById("userInput");
    var message = input.value.trim();
    if (message !== "") {
        appendMessage(message, 'user-message'); // Display user's message in the chat UI
        input.value = "";
        input.focus();
        // Send data to Django server via AJAX
        // JavaScript part, ensure it's correctly calling your Django API
        $.ajax({
            url: '/api/chat/',
            method: 'POST',
            data: { message: message },
            headers: { 'X-CSRFToken': getCookie('csrftoken') }, // CSRF token is required for POST requests
            success: function (data) {
                appendMessage(data.response, 'bot-message');
                if (new_chat_state) {
                    display_previous_chat();
                }
                new_chat_state = false;
            },
            error: function (xhr) {
                appendMessage("Error: " + xhr.statusText, 'bot-message');
            }
        });

    }
}


function escapeHtml(text) {
    var map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function (m) {
        return map[m];
    });
}

function convertMarkdownBold(line) {
    return line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

function appendMessage(text, className) {
    var messageDiv = document.createElement("div");
    messageDiv.className = 'chat-message ' + className;

    var lines = text.split('\n');
    var formattedText = '';
    var isCodeBlock = false;
    var codeLanguage = '';
    var codeBlockContent = [];

    lines.forEach(line => {
        if (line.startsWith('```') && !isCodeBlock) {
            isCodeBlock = true;
            codeLanguage = line.substring(3).trim(); // Extract the language identifier
            return;
        }

        if (line.startsWith('```') && isCodeBlock) {
            var encodedContent = codeBlockContent.map(line =>
                line.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            ).join('\n');

            // Add a copy button to each code block
            formattedText += `
                    <div class="code-snippet">
                        <button class="copy-btn" onclick="copyCode(this)">Copy</button>
                        <pre><code class="${codeLanguage}">${encodedContent}</code></pre>
                    </div>
                    `;
            codeBlockContent = [];
            isCodeBlock = false;
            return;
        }

        if (isCodeBlock) {
            codeBlockContent.push(line);
            return;
        }

        line = escapeHtml(line);
        line = convertMarkdownBold(line);

        // Here, we use `<br>` for line breaks in user messages
        if (className === 'user-message') {
            formattedText += line + '<br>';
        } else {
            formattedText += '<p>' + line + '</p>';
        }
    });

    messageDiv.innerHTML = formattedText;

    var chatMessages = document.getElementById("chatMessages");
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);
    });

    if (window.MathJax) {
        MathJax.typesetPromise();
    }
}

function copyCode(button) {
    // Get the code text within the same code-snippet container as the button
    const codeSnippet = button.parentNode.querySelector('pre code');
    // Create a temporary textarea element to copy the text
    const tempInput = document.createElement('textarea');
    tempInput.value = codeSnippet.textContent;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
    // Notify user that the code has been copied
    button.textContent = 'Copied!';
    setTimeout(() => button.textContent = 'Copy', 2000);
}


// Event listener for pressing the Enter key in the textarea to send message
document.getElementById("userInput").addEventListener("keypress", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault(); // Prevent the default action to avoid line breaks in the textarea
        sendMessage();
    }
});