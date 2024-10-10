document.addEventListener('DOMContentLoaded', function() {
  // Get the active tab's URL when the popup is opened
  chrome.tabs.query({ active: true, lastFocusedWindow: true }, function(tabs) {
    const currentTab = tabs[0];
    const urlInput = document.getElementById('url');

    // Set the current tab's URL in the input field
    urlInput.value = currentTab.url;
  });

  // Handle the 'Check' button click event
  document.getElementById('checkUrl').addEventListener('click', () => {
    const url = document.getElementById('url').value;
    const resultElement = document.getElementById('result');

    // Clear previous result
    resultElement.textContent = '';

    fetch('http://127.0.0.1:8000/check/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    })
      .then(response => response.json())
      .then(data => {
        const result = data.classification;
        resultElement.textContent = `Result: ${result}`;

        // Apply styles based on result
        if (result === 'Legitimate') {
          resultElement.style.color = 'green';
        } else {
          resultElement.style.color = 'red';
        }
      })
      .catch(error => {
        console.error('Error:', error);
        resultElement.textContent = 'Error: Unable to check URL';
        resultElement.style.color = 'red';
      });
  });
});
