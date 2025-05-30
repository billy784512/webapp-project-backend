import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';

const app = express();
const server = createServer(app);
const io = new Server(server, {
    cors: { origin: '*' }
});

io.on('connection', (socket) => {
    console.log(`Client connected: ${socket.id}`);

    socket.on('enter-room', (data) => {
        socket.join(data.room_id)
    })

    socket.on('pick-color', (data) => {
        io.to(data.room_id).emit('receive-color', {
            sender: socket.id,
            message: {
                user_id: data.user_id,
                color: data.color
            }
        })
    })
    
    socket.on('stroke', (data) => {
        io.to(data.room_id).emit('receive-stroke', {
            sender: socket.id,
            message: {
                user_id: data.user_id,
                color: data.color,
                path: data.path  // array of {x, y}
            }
        });
    });

    socket.on('disconnect', () => {
        console.log(`Client disconnected: ${socket.id}`);
    });
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Server listening at http://localhost:${PORT}`);
});
