"""
AVA Sidebar UI

Compact floating sidebar for Windows 11.
Built with tkinter for lightweight, no-extra-dependency UI.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import logging
from typing import Callable, Optional, Any

logger = logging.getLogger(__name__)


class AVAColors:
    """Color scheme for AVA sidebar."""
    
    # Dark theme
    BG_PRIMARY = "#1a1a2e"       # Main background
    BG_SECONDARY = "#16213e"     # Secondary background
    BG_INPUT = "#0f3460"         # Input field background
    BG_BUTTON = "#533483"        # Button background
    BG_BUTTON_HOVER = "#7b2d8e"  # Button hover
    
    FG_PRIMARY = "#e8e8e8"       # Main text
    FG_SECONDARY = "#a8a8b8"     # Secondary text
    FG_ACCENT = "#00d2ff"        # Accent text
    FG_SUCCESS = "#00e676"       # Success messages
    FG_ERROR = "#ff5252"         # Error messages
    FG_WARNING = "#ffc107"       # Warning messages
    
    ORB_IDLE = "#4fc3f7"         # Orb when idle
    ORB_LISTENING = "#ff5252"    # Orb when listening
    ORB_THINKING = "#ffc107"     # Orb when processing
    ORB_SUCCESS = "#00e676"      # Orb on success
    ORB_ERROR = "#ff5252"        # Orb on error
    ORB_OFFLINE = "#757575"      # Orb when offline
    
    BORDER = "#2a2a4a"           # Border color


class SidebarUI:
    """
    Compact floating sidebar UI for AVA.
    Includes text input, voice control, conversation history, and status.
    """
    
    def __init__(self, config):
        """
        Initialize sidebar UI.
        
        Args:
            config: AVA configuration object
        """
        self.config = config
        
        # Callbacks
        self._on_text_submit: Optional[Callable[[str], None]] = None
        self._on_mic_toggle: Optional[Callable[[], None]] = None
        self._on_close: Optional[Callable[[], None]] = None
        
        # State
        self._listening = False
        self._is_online = False
        self._partial_text = ""
        
        # Create window
        self._create_window()
    
    def _create_window(self):
        """Create the main sidebar window."""
        self.root = tk.Tk()
        self.root.title("AVA - Advanced Virtual Assistant")
        self.root.overrideredirect(True)  # Remove title bar
        
        # Window settings
        width = self.config.get("ui", "width", 400)
        height = self.config.get("ui", "height", 600)
        pos_x = self.config.get("ui", "position_x", 100)
        pos_y = self.config.get("ui", "position_y", 100)
        
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        self.root.minsize(350, 400)
        
        always_on_top = self.config.get("ui", "always_on_top", True)
        if always_on_top:
            self.root.attributes('-topmost', True)
        
        opacity = self.config.get("ui", "opacity", 0.95)
        self.root.attributes('-alpha', opacity)
        
        # Configure main style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TFrame', background=AVAColors.BG_PRIMARY)
        style.configure('Dark.TLabel', 
                       background=AVAColors.BG_PRIMARY, 
                       foreground=AVAColors.FG_PRIMARY)
        style.configure('Status.TLabel',
                       background=AVAColors.BG_PRIMARY,
                       foreground=AVAColors.FG_SECONDARY)
        
        # Build UI components
        self._build_header()
        self._build_conversation_panel()
        self._build_input_panel()
        self._build_status_bar()
        
        # Make window draggable
        self._make_draggable()
        
        # Handle close
        self.root.protocol("WM_DELETE_WINDOW", self._handle_close)
    
    def _build_header(self):
        """Build the header with AVA orb and title."""
        header = tk.Frame(self.root, bg=AVAColors.BG_SECONDARY, height=50)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        # AVA Orb (status indicator)
        self.orb_canvas = tk.Canvas(header, width=30, height=30, 
                                     bg=AVAColors.BG_SECONDARY, highlightthickness=0)
        self.orb_canvas.pack(side=tk.LEFT, padx=(15, 10), pady=10)
        self.orb = self.orb_canvas.create_oval(5, 5, 25, 25, 
                                                fill=AVAColors.ORB_IDLE, outline="")
        
        # Title
        title = tk.Label(header, text="AVA", font=("Segoe UI", 14, "bold"),
                         bg=AVAColors.BG_SECONDARY, fg=AVAColors.FG_ACCENT)
        title.pack(side=tk.LEFT, padx=5)
        
        subtitle = tk.Label(header, text="Advanced Virtual Assistant",
                           font=("Segoe UI", 9), bg=AVAColors.BG_SECONDARY,
                           fg=AVAColors.FG_SECONDARY)
        subtitle.pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        btn_frame = tk.Frame(header, bg=AVAColors.BG_SECONDARY)
        btn_frame.pack(side=tk.RIGHT, padx=10)
        
        # Minimize button
        self.minimize_btn = tk.Button(btn_frame, text="—", font=("Segoe UI", 10),
                                      bg=AVAColors.BG_SECONDARY, fg=AVAColors.FG_PRIMARY,
                                      bd=0, relief=tk.FLAT, cursor="hand2",
                                      command=self._minimize)
        self.minimize_btn.pack(side=tk.LEFT, padx=3)
        
        # Close button
        self.close_btn = tk.Button(btn_frame, text="✕", font=("Segoe UI", 10),
                                   bg=AVAColors.BG_SECONDARY, fg=AVAColors.FG_PRIMARY,
                                   bd=0, relief=tk.FLAT, cursor="hand2",
                                   command=self._handle_close)
        self.close_btn.pack(side=tk.LEFT, padx=3)
    
    def _build_conversation_panel(self):
        """Build the scrollable conversation history panel."""
        # Conversation frame
        conv_frame = tk.Frame(self.root, bg=AVAColors.BG_PRIMARY)
        conv_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollable text area
        self.chat_display = scrolledtext.ScrolledText(
            conv_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg=AVAColors.BG_PRIMARY,
            fg=AVAColors.FG_PRIMARY,
            insertbackground=AVAColors.FG_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=10,
            state=tk.DISABLED,
            cursor="arrow"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different message types
        self.chat_display.tag_configure("user", foreground=AVAColors.FG_ACCENT,
                                        font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_configure("assistant", foreground=AVAColors.FG_PRIMARY,
                                        font=("Segoe UI", 10))
        self.chat_display.tag_configure("system", foreground=AVAColors.FG_SECONDARY,
                                        font=("Segoe UI", 9, "italic"))
        self.chat_display.tag_configure("error", foreground=AVAColors.FG_ERROR,
                                        font=("Segoe UI", 10))
        self.chat_display.tag_configure("success", foreground=AVAColors.FG_SUCCESS,
                                        font=("Segoe UI", 10))
        self.chat_display.tag_configure("partial", foreground=AVAColors.FG_WARNING,
                                        font=("Segoe UI", 10, "italic"))
        
        # Welcome message
        self._add_message("system", "AVA is ready. Type a command or click 🎤 to speak.")
    
    def _build_input_panel(self):
        """Build the text input and voice control panel."""
        input_frame = tk.Frame(self.root, bg=AVAColors.BG_SECONDARY, height=60)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 5))
        input_frame.pack_propagate(False)
        
        # Inner frame for layout
        inner = tk.Frame(input_frame, bg=AVAColors.BG_SECONDARY)
        inner.pack(fill=tk.BOTH, expand=True, pady=8)
        
        # Microphone button
        self.mic_btn = tk.Button(
            inner, text="🎤", font=("Segoe UI", 16),
            bg=AVAColors.BG_BUTTON, fg=AVAColors.FG_PRIMARY,
            activebackground=AVAColors.BG_BUTTON_HOVER,
            activeforeground=AVAColors.FG_PRIMARY,
            bd=0, relief=tk.FLAT, cursor="hand2",
            command=self._toggle_mic,
            width=3
        )
        self.mic_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Text input field
        self.text_input = tk.Entry(
            inner,
            font=("Segoe UI", 11),
            bg=AVAColors.BG_INPUT,
            fg=AVAColors.FG_PRIMARY,
            insertbackground=AVAColors.FG_PRIMARY,
            relief=tk.FLAT,
            bd=5
        )
        self.text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self.text_input.bind('<Return>', self._on_enter)
        
        # Send button
        self.send_btn = tk.Button(
            inner, text="➤", font=("Segoe UI", 14),
            bg=AVAColors.BG_BUTTON, fg=AVAColors.FG_PRIMARY,
            activebackground=AVAColors.BG_BUTTON_HOVER,
            activeforeground=AVAColors.FG_PRIMARY,
            bd=0, relief=tk.FLAT, cursor="hand2",
            command=self._send_text
        )
        self.send_btn.pack(side=tk.RIGHT)
    
    def _build_status_bar(self):
        """Build the bottom status bar."""
        status_frame = tk.Frame(self.root, bg=AVAColors.BG_SECONDARY, height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 5))
        status_frame.pack_propagate(False)
        
        # Online/offline indicator
        self.status_indicator = tk.Label(status_frame, text="●",
                                         font=("Segoe UI", 8),
                                         bg=AVAColors.BG_SECONDARY,
                                         fg=AVAColors.ORB_OFFLINE)
        self.status_indicator.pack(side=tk.LEFT, padx=(5, 3))
        
        # Status text
        self.status_label = tk.Label(status_frame, text="Checking connection...",
                                    font=("Segoe UI", 8),
                                    bg=AVAColors.BG_SECONDARY,
                                    fg=AVAColors.FG_SECONDARY)
        self.status_label.pack(side=tk.LEFT)
        
        # Voice status
        self.voice_status = tk.Label(status_frame, text="🎤 Ready",
                                    font=("Segoe UI", 8),
                                    bg=AVAColors.BG_SECONDARY,
                                    fg=AVAColors.FG_SECONDARY)
        self.voice_status.pack(side=tk.RIGHT, padx=5)
    
    def _make_draggable(self):
        """Make the window draggable by its header."""
        self._drag_x = 0
        self._drag_y = 0
        
        def on_press(event):
            self._drag_x = event.x
            self._drag_y = event.y
        
        def on_drag(event):
            x = self.root.winfo_pointerx() - self._drag_x
            y = self.root.winfo_pointery() - self._drag_y
            self.root.geometry(f"+{x}+{y}")
        
        # Bind to all header elements
        for widget in [self.root]:
            widget.bind("<ButtonPress-1>", on_press)
            widget.bind("<B1-Motion>", on_drag)
    
    def _minimize(self):
        """Minimize the sidebar."""
        self.root.withdraw()
    
    def restore(self):
        """Restore the sidebar from minimized state."""
        self.root.deiconify()
    
    def _handle_close(self):
        """Handle close button."""
        if self._on_close:
            self._on_close()
        self.root.destroy()
    
    def _on_enter(self, event=None):
        """Handle Enter key in text input."""
        self._send_text()
    
    def _send_text(self):
        """Send text input to command engine."""
        text = self.text_input.get().strip()
        if text and self._on_text_submit:
            self.text_input.delete(0, tk.END)
            self._on_text_submit(text)
    
    def _toggle_mic(self):
        """Toggle microphone listening."""
        if self._on_mic_toggle:
            self._on_mic_toggle()
    
    # --- Public methods for updating UI ---
    
    def set_on_text_submit(self, callback: Callable[[str], None]) -> None:
        """Set callback for text submission."""
        self._on_text_submit = callback
    
    def set_on_mic_toggle(self, callback: Callable[[], None]) -> None:
        """Set callback for microphone toggle."""
        self._on_mic_toggle = callback
    
    def set_on_close(self, callback: Callable[[], None]) -> None:
        """Set callback for window close."""
        self._on_close = callback
    
    def add_user_message(self, text: str) -> None:
        """Add a user message to the conversation."""
        self._add_message("user", f"You: {text}")
    
    def add_assistant_message(self, text: str) -> None:
        """Add an assistant response to the conversation."""
        self._add_message("assistant", f"AVA: {text}")
    
    def add_system_message(self, text: str) -> None:
        """Add a system message to the conversation."""
        self._add_message("system", text)
    
    def add_error_message(self, text: str) -> None:
        """Add an error message to the conversation."""
        self._add_message("error", f"Error: {text}")
    
    def add_success_message(self, text: str) -> None:
        """Add a success message to the conversation."""
        self._add_message("success", text)
    
    def _add_message(self, tag: str, text: str) -> None:
        """Add a message to the chat display."""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{text}\n\n", tag)
        self.chat_display.see(tk.END)
        self.chat_display.configure(state=tk.DISABLED)
    
    def update_partial_text(self, text: str) -> None:
        """Update partial speech recognition text."""
        # Remove previous partial text
        self.chat_display.configure(state=tk.NORMAL)
        
        # Find and remove any partial line
        content = self.chat_display.get("1.0", tk.END)
        lines = content.split("\n")
        new_lines = [l for l in lines if not l.startswith("🎤 ")]
        
        # Clear and rewrite
        self.chat_display.delete("1.0", tk.END)
        for line in new_lines:
            if line.strip():
                self.chat_display.insert(tk.END, f"{line}\n", "assistant")
        
        # Add new partial
        if text:
            self.chat_display.insert(tk.END, f"🎤 {text}...\n", "partial")
            self.chat_display.see(tk.END)
        
        self.chat_display.configure(state=tk.DISABLED)
    
    def set_orb_state(self, state: str) -> None:
        """
        Set orb color based on state.
        
        Args:
            state: idle, listening, thinking, success, error, offline
        """
        color_map = {
            "idle": AVAColors.ORB_IDLE,
            "listening": AVAColors.ORB_LISTENING,
            "thinking": AVAColors.ORB_THINKING,
            "success": AVAColors.ORB_SUCCESS,
            "error": AVAColors.ORB_ERROR,
            "offline": AVAColors.ORB_OFFLINE,
        }
        color = color_map.get(state, AVAColors.ORB_IDLE)
        self.orb_canvas.itemconfigure(self.orb, fill=color)
    
    def set_online_status(self, is_online: bool) -> None:
        """Update online/offline status indicator."""
        self._is_online = is_online
        if is_online:
            self.status_indicator.configure(fg=AVAColors.ORB_SUCCESS)
            self.status_label.configure(text="Online")
        else:
            self.status_indicator.configure(fg=AVAColors.ORB_OFFLINE)
            self.status_label.configure(text="Offline")
    
    def set_listening_state(self, is_listening: bool) -> None:
        """Update listening state display."""
        self._listening = is_listening
        if is_listening:
            self.mic_btn.configure(text="🔴", bg=AVAColors.ORB_LISTENING)
            self.voice_status.configure(text="🎤 Listening...")
            self.set_orb_state("listening")
        else:
            self.mic_btn.configure(text="🎤", bg=AVAColors.BG_BUTTON)
            self.voice_status.configure(text="🎤 Ready")
            self.set_orb_state("idle")
    
    def set_voice_status(self, text: str) -> None:
        """Set voice status text."""
        self.voice_status.configure(text=text)
    
    def run(self) -> None:
        """Start the UI event loop."""
        logger.info("Starting sidebar UI event loop")
        self.root.mainloop()
    
    def quit(self) -> None:
        """Quit the UI event loop."""
        try:
            self.root.quit()
        except Exception:
            pass
    
    def schedule(self, callback, *args) -> None:
        """Schedule a callback on the UI thread (thread-safe)."""
        try:
            self.root.after(0, callback, *args)
        except Exception as e:
            logger.error(f"Failed to schedule callback: {e}")
