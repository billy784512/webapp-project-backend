import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import axios from 'axios';

const app = express();
const server = createServer(app);
const io = new Server(server, {
    cors: { origin: '*' }
});

// Map<room_id, Set<socket.id>>
const roomPreparedStatus = new Map();

// Map<room_id, Map<user_id, base64_str>>
const submissionCache = new Map();

io.on('connection', (socket) => {
    console.log(`Client connected: ${socket.id}`);

    socket.on('enter-room', (data) => {
        const { room_id } = data;
        socket.join(room_id)

        if (!roomPreparedStatus.has(room_id)) {
            roomPreparedStatus.set(room_id, new Set());
            console.log(`New room created: ${room_id}`);
        }
    })

    socket.on('prepare', (data) => {
        const { room_id, user_id } = data;
        const preparedSet = roomPreparedStatus.get(room_id);
        preparedSet.add(socket.id);

        io.to(room_id).emit('prepare-update', {
            sender: socket.id,
            message: {
                user_id: user_id,
                prepared: true
            }
        })

        console.log(`[${room_id}] ${socket.id} prepared (${preparedSet.size}/${io.sockets.adapter.rooms.get(room_id)?.size})`);
    })

    socket.on('check-prepare', (data) => {
        const { room_id } = data;
        const room = io.sockets.adapter.rooms.get(room_id);
        const totalUsers = room ? room.size : 0;
        const preparedSet = roomPreparedStatus.get(room_id);

        console.log(`[${room_id}] check-prepare: ${preparedSet?.size ?? 0}/${totalUsers}`);

        if (preparedSet.size === totalUsers){
            io.to(room_id).emit("all-prepared", { room_id });
            console.log(`All users in room ${room_id} are prepared!`);
        }
    })

    socket.on('disconnecting', () => {
        for (const room_id of socket.rooms) {
            if (room_id === socket.id) continue;

            const preparedSet = roomPreparedStatus.get(room_id);
            if (preparedSet) {
                preparedSet.delete(socket.id);
            }

            const room = io.sockets.adapter.rooms.get(room_id);
            if (room) {
                const allSocketIds = Array.from(room);
                const opponentId = allSocketIds.find(id => id !== socket.id);

                if (opponentId) {
                    io.to(opponentId).emit('opponent-disconnected', {
                        room_id,
                    });

                    const opponentSocket = io.sockets.sockets.get(opponentId);
                    if (opponentSocket) {
                        opponentSocket.leave(room_id);
                        console.log(`Opponent ${opponentId} removed from room ${room_id}`);
                    }
                }
            }

            roomPreparedStatus.delete(room_id);
            console.log(`Room ${room_id} cleaned due to ${socket.id} disconnecting`);
        }
    });

    socket.on("stroke", (data) => {
        io.to(data.room_id).emit("receive-stroke", {
            sender: socket.id,
            message: {
                user_id: data.user_id,
                color: data.color,
                path: data.path,
                brushSize: data.brushSize,
                isEraser: data.isEraser,
                operationTimestamp: data.operationTimestamp,
                operationType: data.operationType,
            },
        });
    });

    socket.on("submit", async (data) => {
        const { room_id, user_id, base64_str } = data;

        if (!submissionCache.has(room_id)) {
            submissionCache.set(room_id, new Map());
        }

        const roomSubmissions = submissionCache.get(room_id);
        roomSubmissions.set(user_id, base64_str);

        console.log(`[${room_id}] Received submission from ${user_id} (${roomSubmissions.size}/2)`);

        // 如果兩人都提交了
        if (roomSubmissions.size === 2) {
            const orderedSubmissions = Array.from(roomSubmissions.entries()); 
            const base64_strs = orderedSubmissions.map(([_, base64]) => base64);
            const user_ids = orderedSubmissions.map(([user_id]) => user_id);

            try {
                const response = await axios.post("http://127.0.0.1:8080/game/submit", {
                    room_id,
                    base64_strs
                });

                const scores = response.data.scores;

                const winnerIndex = scores[0] >= scores[1] ? 0 : 1;
                const winnerUserId = user_ids[winnerIndex];

                io.to(room_id).emit("submit-result", {
                    winner: winnerUserId,
                    scores: {
                        [user_ids[0]]: scores[0],
                        [user_ids[1]]: scores[1]
                    }
                });

                console.log(`[${room_id}] Winner: ${winnerUserId}`);

            } catch (error) {
                console.error(`[${room_id}] Error comparing drawings:`, error.message);
                io.to(room_id).emit("submit-error", {
                    message: "Failed to compare submissions."
                });
            } finally {
                submissionCache.delete(room_id);
            }
        }
    });

    socket.on('disconnect', () => {
        console.log(`Client disconnected: ${socket.id}`);
    });    
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Server listening at:`);
    console.log(` - HTTP  : http://localhost:${PORT}`);
    console.log(` - WS    : ws://localhost:${PORT}`);
});
