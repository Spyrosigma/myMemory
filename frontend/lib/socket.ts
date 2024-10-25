import { io, Socket } from 'socket.io-client';

let socket: Socket | null = null;

export const initializeSocket = () => {
  if (!socket) {
    // Replace with your deployed backend URL
    const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ;
    // const BACKEND_URL = 'http://localhost:5000/';

    
    socket = io(BACKEND_URL, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 10000
    });
  }
  return socket;
};

export const getSocket = () => {
  if (!socket) {
    return initializeSocket();
  }
  return socket;
};