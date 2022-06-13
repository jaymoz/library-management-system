let loc = window.location
let wsStart = 'ws://'
let input_message = $('#input_message')
let message_body = $('#message_body')
let send_message_form = $('#send-message-form')
let USER_ID = $('#user_id').val()
if(location.protocol == 'https')
{
    wsStart = 'wss://'
}
let endpoint = wsStart + loc.host + loc.pathname
var socket = new WebSocket(endpoint)

document.querySelector('#input_message').focus();
document.querySelector('#input_message').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};
socket.onopen = async function (e)
{
    console.log('open', e)
    document.querySelector('#chat-message-submit').onclick = function(e) {
        e.preventDefault();
        let messageInputDom = document.querySelector('#input_message');
        let message = messageInputDom.value;
        let send_to = get_active_other_user_id();
        let thread_id = get_active_thread_id();
        let data = {
            'message' : message,
            'sent_by' : USER_ID,
            'send_to' : send_to,
            'thread_id' : thread_id
        }
        data = JSON.stringify(data)
        socket.send(data)
        messageInputDom.value = '';
    };
    // send_message_form.on('submit', function(e)
    // {
    //     e.preventDefault()
    //     let message = input_message.val()
    //     let data = {
    //         'message': message
    //     }
    //     data = JSON.stringify(data)
    //     socket.send(data)
    //     $(this)[0].reset()

    // })
}
socket.onmessage = async function (e)
{

    let data = JSON.parse(e.data)
    let message = data['message']

    document.querySelector('#message_body').value += (message)

}
socket.onerror = async function (e)
{
    console.log('error', e)
}
socket.onclose = async function (e)
{
    console.log('close', e)
}

function newMessage(message)
{
    
    if ($.trim(message) == '')
    {
        return false;
    }

    message_body.animate({
        scrollTop: $(document).height()
    }, 100);
    console.log(input_message);
    input_message.val(null);
}

function get_active_other_user_id(){
    let other_user_id = $('.messages-wrapper.is_active').attr('other-user-id')
    other_user_id = $.trim(other_user_id)
    return other_user_id
}

function get_active_thread_id(){
    let chat_id = $('.messages-wrapper.is_active').attr('chat-id')
    let thread_id = chat_id.replace('chat_', '')
    return thread_id
}