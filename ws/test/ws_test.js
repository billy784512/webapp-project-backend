import { io } from 'socket.io-client';

const SERVER_URL = 'ws://localhost:3000';
const ROOM_ID = 'test-room-999';

function createUser(user_id) {
  const socket = io(SERVER_URL);

  socket.on('connect', () => {
    console.log(`[${user_id}] Connected: ${socket.id}`);

    socket.emit('enter-room', { room_id: ROOM_ID });
    console.log(`[${user_id}] entered room: ${ROOM_ID}`);

    setTimeout(() => {
      socket.emit('prepare', { room_id: ROOM_ID, user_id });
      console.log(`[${user_id}] sent prepare`);
    }, 300);

    // Step 4: heartbeat check every 1s
    const heartbeatInterval = setInterval(() => {
      socket.emit('check-prepare', { room_id: ROOM_ID });
      console.log(`[${user_id}] 🧭 sent check-prepare`);
    }, 1000);

    socket.on('all-prepared', (data) => {
      console.log(`[${user_id}] ✅ all-prepared received for room ${data.room_id}`);
      clearInterval(heartbeatInterval);
      socket.disconnect();
    });
  });

  socket.on('prepare-update', (data) => {
    console.log(`[${user_id}] 🔄 prepare-update:`, data);
  });

  socket.on('disconnect', () => {
    console.log(`[${user_id}] Disconnected`);
  });

  socket.on('connect_error', (err) => {
    console.error(`[${user_id}] Connection error: ${err.message}`);
  });
}

// Start two users
createUser('user-A');
createUser('user-B');
