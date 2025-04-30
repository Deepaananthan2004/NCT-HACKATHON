function generateKeys() {
    fetch('/generate_keys')
      .then(res => res.json())
      .then(data => {
        document.getElementById('pubKey').innerText = data.public_key;
        document.getElementById('privKey').innerText = data.private_key;
        document.getElementById('uploadKey').value = data.public_key;
      })
      .catch(err => console.error('Error:', err));
  }
  
  document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    fetch('/upload', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.ipfs_url) {
        document.getElementById('uploadStatus').innerText = "✅ File Uploaded: " + data.ipfs_url;
      } else {
        document.getElementById('uploadStatus').innerText = "❌ Upload Failed";
      }
    });
  });
  
  document.getElementById('downloadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const privKey = document.getElementById('privateKey').value;
    fetch('/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ private_key: privKey })
    })
    .then(res => res.json())
    .then(data => {
      if (data.ipfs_url) {
        document.getElementById('downloadStatus').innerHTML =
          `✅ File Found: <a href="${data.ipfs_url}" target="_blank">${data.filename}</a>`;
      } else {
        document.getElementById('downloadStatus').innerText = "❌ File Not Found";
      }
    });
  });  