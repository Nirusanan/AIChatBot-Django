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
