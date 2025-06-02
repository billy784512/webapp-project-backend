import { io } from 'socket.io-client';

const SERVER_URL = 'ws://localhost:3000';
const ROOM_ID = 'test-room-999';

function createUser(user_id, autoDisconnect = false) {
  const socket = io(SERVER_URL);

  socket.on('connect', () => {
    console.log(`[${user_id}] ✅ Connected as ${socket.id}`);

    // Step 1: Enter room
    socket.emit('enter-room', { room_id: ROOM_ID });
    console.log(`[${user_id}] entered room: ${ROOM_ID}`);

    // Step 2: Send prepare after slight delay
    setTimeout(() => {
      socket.emit('prepare', { room_id: ROOM_ID, user_id });
      console.log(`[${user_id}] sent prepare`);
    }, 500);

    // Step 3: Start heartbeat to check-prepare
    const interval = setInterval(() => {
      socket.emit('check-prepare', { room_id: ROOM_ID });
      console.log(`[${user_id}] 🔄 check-prepare`);
    }, 1000);

    // Step 4: Listen for all-prepared
    socket.on('all-prepared', (data) => {
      console.log(`[${user_id}] 🎉 all-prepared: ${data.room_id}`);
      if (autoDisconnect) {
        console.log(`[${user_id}] will now disconnect (simulating quit)`);
        clearInterval(interval);
        socket.disconnect();
      }
    });

    // Step 5: Handle opponent disconnection
    socket.on('opponent-disconnected', (data) => {
      console.log(`[${user_id}] ❌ Opponent left room ${data.room_id}`);
      clearInterval(interval);
      socket.disconnect();
    });

    // Cleanup
    socket.on('disconnect', () => {
      console.log(`[${user_id}] 🔴 Disconnected`);
    });

    socket.on('connect_error', (err) => {
      console.error(`[${user_id}] Connection error: ${err.message}`);
    });
  });
}

// 模擬兩人
createUser('user-A');             // 留在房內觀察對手
createUser('user-B', true);       // 準備完後自動離開
