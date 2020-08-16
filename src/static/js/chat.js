function conversationListItemOnClick(event) {
  var conversationListItemDom = event.target;

  // get the main li element (conversation list item)
  while (
    !conversationListItemDom.classList.contains(
      "chat__conversations__list__item"
    )
  ) {
    conversationListItemDom = conversationListItemDom.parentElement;
  }

  var username = conversationListItemDom.getAttribute("data-username");

  loadChat(username);
}

function loadChat(username) {
  window.location.pathname = "/chat/user/" + username + "";
}

function htmlToElement(html) {
  var template = document.createElement("template");
  html = html.trim(); // Never return a text node of whitespace as the result
  template.innerHTML = html;
  return template.content.firstChild;
}

function initChat() {
  scrollToBottom("chat-messages-container");

  const conversationIdDom = document.getElementById("conversation-id");
  const toUserUsernameDom = document.getElementById("to-user-username");

  if (!conversationIdDom || !toUserUsernameDom) {
    return;
  }

  const conversationId = JSON.parse(
    document.getElementById("conversation-id").textContent
  );
  const toUserUsername = JSON.parse(
    document.getElementById("to-user-username").textContent
  );

  const chatSocket = new WebSocket(
    "ws://" +
      window.location.host +
      "/ws/chat/conversations/" +
      conversationId +
      "/" +
      toUserUsername +
      "/"
  );

  chatSocket.onmessage = function (e) {
    let data = JSON.parse(e.data);
    data = JSON.parse(data.message);

    const chatContainerDom = document.querySelector(".chat__messages");
    const divTag = document.createElement("div");
    const pTag1 = document.createElement("p");
    const pTag2 = document.createElement("p");

    divTag.classList.add("chat__messages__item");
    if (data.sender !== toUserUsername) {
      divTag.classList.add("chat__messages__item__right");
    }
    pTag2.classList.add("chat__messages__item__date");

    pTag1.innerText = data.text;
    pTag2.innerText = data.created_at;

    divTag.appendChild(pTag1);
    divTag.appendChild(pTag2);

    chatContainerDom.appendChild(divTag);

    scrollToBottom("chat-messages-container");
  };

  chatSocket.onclose = function (e) {
    console.error("Chat socket closed unexpectedly");
  };

  document.querySelector("#chat-message-submit").onclick = function (e) {
    const csrfMiddlewareToken = document.getElementsByName(
      "csrfmiddlewaretoken"
    )[0].value;
    const messageInputDom = document.querySelector("#chat-message-input");
    const message = messageInputDom.value;

    var xhr = new XMLHttpRequest();

    xhr.open("POST", "/chat/user/" + toUserUsername + "/send/", true);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("text=" + message + "&csrfmiddlewaretoken=" + csrfMiddlewareToken);

    xhr.onload = function () {
      if (xhr.status == 200) {
      }
    };

    messageInputDom.value = "";
  };
}

function scrollToBottom(id) {
  var div = document.getElementById(id);
  div.scrollTop = div.scrollHeight - div.clientHeight;
}

initChat();
