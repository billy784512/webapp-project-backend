
## Reverse Proxy Config (Nginx)
```bash
#OS: Ubuntu
cd /etc/nginx/sites-available
sudo touch tunnel
sudo vim tunnel # paste the code provided in repo
sudo ln -s /etc/nginx/sites-available/tunnel /etc/nginx/sites-enabled/tunnel
sudo nginx -t && sudo systemctl reload nginx
```

## Cloudflare Tunnel
```
cloudflared tunnel --url http://localhost:7788
```

## Sample Code for testing connection
```js
import axios from 'axios';
import { io } from 'socket.io-client';

const DOMAIN_NAME = '<cloudflare-tunnel-domain-name>'

async function testApi() {
  const url = `https://${DOMAIN_NAME}/api/heartbeat`;
  try {
    const response = await axios.get(url);
    console.log("✅ API Success:", response.data);
  } catch (err) {
    console.error("❌ API Failed:", err.message);
  }
}

function testWebSocket() {
  return new Promise((resolve, reject) => {
    const socket = io(`wss://${DOMAIN_NAME}`, {
      path: "/socket.io",
      transports: ['websocket'],
      timeout: 5000
    });

    socket.on('connect', () => {
      console.log("WebSocket Connected:", socket.id);
      setTimeout(() => {
        socket.disconnect();
        resolve();
      }, 5000);  // wait 5 seconds before disconnecting
    });

    socket.on('connect_error', (err) => {
      console.error("WebSocket Failed:", err.message);
      reject(err);
    });
  });
}

async function main() {
  console.log("Testing API...");
  await testApi();

  console.log("Testing WebSocket...");
  try {
    await testWebSocket();
  } catch (_) {}

  console.log("Done.");
}

main();
```