# Client Layer - Code Explanation

This directory contains the **Client Layer** (Frontend) of the StreamLink application. It is a React application built with Vite and TypeScript. It provides the user interface for logging in, joining rooms, and participating in video calls (WebRTC) and text chat.

## File Breakdown

### 1. `src/App.tsx`
**Purpose:** The main component that sets up routing.
- **Logic:**
    - Uses `react-router-dom` to navigate between pages.
    - Defines routes: `/` (Login), `/rooms` (Room List), `/room/:roomId` (Chat Room).
    - **`PrivateRoute` Component:** Wraps protected routes. It checks if a `token` exists in `localStorage`. If not, it redirects the user back to the Login page.

### 2. `src/api.ts`
**Purpose:** Configures the HTTP client (Axios) for communicating with the Management Layer.
- **Logic:**
    - Creates an Axios instance with the base URL of the Management Layer.
    - **Interceptor:** Automatically adds the `Authorization: Bearer <token>` header to every request if a token is saved in `localStorage`.

### 3. `src/hooks/useWebRTC.ts`
**Purpose:** A custom React Hook that encapsulates *all* the complex logic for real-time communication (WebSocket + WebRTC). This is the "brain" of the video call.
- **Functions & Logic:**
    - **`useWebSocket`**: Connects to the Signaling Layer. Handles `onOpen` (connection success) and `onClose` (disconnection/kicks).
    - **`startLocalVideo`**: Requests access to the user's camera and microphone using the browser's `navigator.mediaDevices.getUserMedia` API.
    - **`createPeerConnection(targetUserId)`**: Creates a new `RTCPeerConnection` for a specific peer.
        - Sets up ICE servers (STUN) to bypass firewalls.
        - Handles `onicecandidate`: Sends network pathway info to the peer via WebSocket.
        - Handles `ontrack`: Receives the peer's video/audio stream and attaches it to a video element.
    - **Signal Handling (`useEffect` with `lastMessage`)**: Listens for WebSocket messages:
        - `existing_users`: Received on join. Triggers connection to all users already in the room.
        - `user_joined`: A new user entered. We initiate a call (Offer).
        - `offer` / `answer`: The core WebRTC handshake steps.
        - `candidate`: Network information exchange.
        - `chat`: Receives a text message.
        - `user_left`: Cleans up the peer connection and removes their video.

### 4. `src/pages/ChatRoom.tsx`
**Purpose:** The main page for the video call interface.
- **Logic:**
    - Uses `useWebRTC` hook to get the state (peers, messages, video streams).
    - Fetches room details (e.g., "Created By") from the API to determine if the current user is the admin.
    - **`handleBlockUser`**: Allows an admin to ban a user. Sends an API request to the Management Layer.
    - Renders the `UserList`, `VideoGrid`, and `ChatSidebar`.

### 5. `src/components/VideoGrid.tsx`
**Purpose:** Displays the video feeds.
- **Logic:**
    - Renders the Local Video (You).
    - Maps through the `peers` list to render Remote Videos for every connected user.
    - Uses a callback `setRemoteRef` to allow the underlying WebRTC logic to attach the media stream directly to the DOM element.

### 6. `src/components/ChatSidebar.tsx`
**Purpose:** Displays the chat container.
- **Logic:**
    - Shows a list of messages (bubbles). Differentiates between "mine" (right) and "theirs" (left).
    - Contains the input form to send new messages.

### Connections
- **Client -> Management Layer**: HTTP requests (Login, Rooms, Ban).
- **Client -> Signaling Layer**: WebSocket connection (Video signaling, Chat).
- **Client -> Client (Peer-to-Peer)**: Direct encrypted media stream (Video/Audio) established via WebRTC.
