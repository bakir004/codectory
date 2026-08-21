const messages = [
  "You’re doing purr-fectly—remember to stretch like a cat!",
  "Today is a good day to follow your curiosity.",
  "Make time for a cozy nap and a little play.",
  "Stay pawsitive: small steps still move you forward."
];

const messageButton = document.querySelector("#message-button");
const messageOutput = document.querySelector("#message-output");
let messageIndex = 0;

if (messageButton && messageOutput) {
  messageButton.addEventListener("click", () => {
    messageOutput.textContent = messages[messageIndex];
    messageIndex = (messageIndex + 1) % messages.length;
  });
}
