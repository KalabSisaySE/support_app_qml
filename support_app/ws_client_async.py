import asyncio
import threading
import tkinter as tk
from tkinter import ttk
import websockets


class AsyncWebSocketClient:

    def __init__(self, uri, gui_update_callback):
        self.uri = uri
        self.ws = None
        self.connected = False
        self.gui_update_callback = gui_update_callback  # Callback to update GUI indicator
        self._stop_requested = False

    async def connect(self):
        try:
            print("\t\t\t1, before connect")
            self.ws = await websockets.connect(self.uri)
            print("\t\t\t2, after connect")
            self.connected = True
            self.gui_update_callback(connected=True)
            print("\t\t\t3, after gui_update")


            # Receive loop
            while self.connected and not self._stop_requested:


                try:
                    print("\t\t\t4, in a loop before wait_for connect")

                    message = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
                    print("\t\t\t4, in a loop after wait_for connect")

                    print("\t\tReceived message:", message)
                    print("\t\ttype(message):", type(message))
                except asyncio.TimeoutError:
                    print("\t\tTimeout error during connection ...")
                    # Timeout waiting for message, continue loop for cancellation check
                    pass
                except websockets.ConnectionClosed:
                    print("\t\tServer is down")
                    self.connected = False

        except Exception as e:
            self.connected = False
            print("Error during connection:", e)

        finally:
            if not self.connected:
                await self.disconnect()
            await asyncio.sleep(5)
            await self.connect()

    async def disconnect(self):
        self._stop_requested = True
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                print("Error closing websocket:", e)
        self.connected = False
        self.gui_update_callback(connected=False)
        print("Disconnected from websocket server")

    def reset_stop_request(self):
        self._stop_requested = False


class AsyncioThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Async WebSocket Client Demo")
        self.connection_status = tk.StringVar(value="Disconnected")

        # GUI indicator: colored label
        # self.indicator = tk.Label(root,
        #                           textvariable=self.connection_status,
        #                           width=60, height=2, bg="red", fg="white", font=("Arial", 16))
        # self.indicator.pack(pady=10)
        self.row_idx = 0

        self.websockets_status_label = tk.Label(root, text="Websockets:", font=("Arial", 12))
        self.websockets_status_indicator = tk.Label(root, width=2, height=1, background="red")

        self.websockets_status_label.grid(row=self.row_idx, column=0, sticky="w", padx=5, pady=5)
        self.websockets_status_indicator.grid(row=self.row_idx, column=1, sticky="w", padx=5, pady=5)

        self.row_idx += 1

        # Button to start/stop connection
        self.toggle_btn = ttk.Button(root, text="Connect", command=self.toggle_connection)
        self.toggle_btn.grid(row=self.row_idx, column=1, sticky="w", padx=5, pady=5)
        # self.toggle_btn.pack(pady=10)

        # Start asyncio event loop thread
        self.async_thread = AsyncioThread()
        self.async_thread.start()

        # WebSocket server URI (change as needed)
        self.ws_uri = "ws://localhost:8000/ws/support/?access_code=0dff2e7c-d54a-435c-9513-36100a1680d05145"
        self.ws_client = None

        # Automatically try connecting on startup
        self.start_connection()

    def update_indicator(self, connected):
        # This method will be called from the WebSocket client for GUI updates.
        # GUI updates must be executed in the main (Tkinter) thread.
        def update():
            if connected:
                self.websockets_status_indicator.config(bg="green")
                # self.connection_status.set("Connected")
                self.toggle_btn.config(text="Disconnect")
            else:
                self.websockets_status_indicator.config(bg="red")
                # self.connection_status.set("Disconnected")
                self.toggle_btn.config(text="Connect")

        self.root.after(0, update)

    def start_connection(self):
        print("start_connection from TK")
        if self.ws_client is None or not self.ws_client.connected:
            print("start_connection from TK - hasn't started, so starting ...")
            # Reset so that disconnect loop does not break immediately.
            self.ws_client = AsyncWebSocketClient(self.ws_uri, self.update_indicator)
            self.ws_client.reset_stop_request()
            # Schedule the websocket connection on the event loop.
            self.async_thread.loop.call_soon_threadsafe(
                lambda: asyncio.ensure_future(self.ws_client.connect(), loop=self.async_thread.loop)
            )

    def stop_connection(self):
        if self.ws_client and self.ws_client.connected:
            # Gracefully disconnect via event loop call
            self.async_thread.loop.call_soon_threadsafe(
                lambda: asyncio.ensure_future(self.ws_client.disconnect(), loop=self.async_thread.loop)
            )

    def toggle_connection(self):
        if self.ws_client is not None and self.ws_client.connected:
            self.stop_connection()
        else:
            self.start_connection()

    def on_close(self):
        # Stop the client and the asyncio event loop on application exit.
        self.stop_connection()
        self.async_thread.stop()
        self.root.destroy()


if __name__ == '__main__':
    print("block")
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
