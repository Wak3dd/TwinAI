import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import threading
import requests
import uuid
import time
from typing import Optional, Dict, List, Callable

# Cryptography for API key encryption
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


# ============================================================================
# ENCRYPTION
# ============================================================================

ENCRYPTION_KEY_FILE = "encryption.key"


def get_encryption_key() -> bytes:
    """Get or generate the encryption key for API keys."""
    if not CRYPTO_AVAILABLE:
        return b""

    if os.path.exists(ENCRYPTION_KEY_FILE):
        try:
            with open(ENCRYPTION_KEY_FILE, "rb") as f:
                return f.read()
        except Exception:
            pass

    key = Fernet.generate_key()
    try:
        with open(ENCRYPTION_KEY_FILE, "wb") as f:
            f.write(key)
    except Exception:
        pass
    return key


def encrypt_value(value: str, key: bytes) -> str:
    """Encrypt a string value."""
    if not value or not CRYPTO_AVAILABLE or not key:
        return value
    try:
        f = Fernet(key)
        return f.encrypt(value.encode("utf-8")).decode("utf-8")
    except Exception:
        return value


def decrypt_value(encrypted_value: str, key: bytes) -> str:
    """Decrypt an encrypted string value."""
    if not encrypted_value or not CRYPTO_AVAILABLE or not key:
        return encrypted_value
    try:
        f = Fernet(key)
        return f.decrypt(encrypted_value.encode("utf-8")).decode("utf-8")
    except Exception:
        # If decryption fails, return as-is (might be unencrypted legacy value)
        return encrypted_value


# ============================================================================
# TRANSLATIONS
# ============================================================================

TRANSLATIONS = {
    "en": {
        "app_title": "AI Dialogue",
        "settings": "Settings",
        "appearance": "Appearance",
        "dark": "Dark",
        "light": "Light",
        "font_family": "Font Family",
        "font_size": "Font Size",
        "app_language": "App Language",
        "bot": "Bot",
        "preset": "Preset",
        "custom": "Custom",
        "name": "Name",
        "provider": "Provider",
        "base_url": "Base URL",
        "api_key": "API Key",
        "model": "Model",
        "advanced_settings": "Advanced Settings",
        "system_prompt": "System Prompt",
        "tone": "Tone",
        "emoji_frequency": "Emoji Frequency",
        "temperature": "Temperature",
        "max_tokens": "Max Tokens",
        "ai_language": "AI Response Language",
        "save_settings": "Save Settings",
        "chats": "Chats",
        "new_chat": "New Chat",
        "delete_chat": "Delete",
        "export_chat": "Export",
        "import_chat": "Import",
        "start_cycle": "Start Cycle",
        "stop_cycle": "Stop Cycle",
        "write_as_bot": "Write as",
        "clear": "Clear",
        "ready": "Ready",
        "cycling": "Cycling...",
        "stopped": "Stopped",
        "typing": "typing...",
        "no_messages": "No Messages",
        "no_messages_text": "Send an initial message before starting the cycle.",
        "missing_api_keys": "Missing API Keys",
        "missing_api_keys_text": "Both bots need API keys configured to run the cycle.",
        "streaming": "Streaming",
        "streaming_text": "Cannot write manually while streaming.",
        "edit_message": "Edit Message",
        "editing_from": "Editing message from",
        "save": "Save",
        "cancel": "Cancel",
        "send": "Send",
        "write_as": "Write as",
        "write_a_message_as": "Write a message as",
        "enter_initial_message": "Enter initial message to start the dialogue...",
        "no_api_key_for": "No API key for",
        "error": "Error",
        "invalid_input": "Invalid Input",
        "max_tokens_must_be_number": "Max Tokens must be a number.",
        "confirm_delete": "Confirm Delete",
        "confirm_delete_chat": "Are you sure you want to delete this chat?",
        "cycle_delay": "Delay between responses (seconds)",
        "untitled_chat": "Untitled Chat",
        "crypto_not_available": "Cryptography library not installed. API keys will be stored in plain text. Install with: pip install cryptography",
        "api_format": "API Format",
    },
    "ru": {
        "app_title": "ИИ Диалог",
        "settings": "Настройки",
        "appearance": "Оформление",
        "dark": "Тёмная",
        "light": "Светлая",
        "font_family": "Шрифт",
        "font_size": "Размер шрифта",
        "app_language": "Язык приложения",
        "bot": "Бот",
        "preset": "Пресет",
        "custom": "Свой",
        "name": "Имя",
        "provider": "Провайдер",
        "base_url": "Base URL",
        "api_key": "API ключ",
        "model": "Модель",
        "advanced_settings": "Доп. настройки",
        "system_prompt": "Системный промпт",
        "tone": "Тон",
        "emoji_frequency": "Частота эмодзи",
        "temperature": "Температура",
        "max_tokens": "Макс. токенов",
        "ai_language": "Язык ответов ИИ",
        "save_settings": "Сохранить",
        "chats": "Чаты",
        "new_chat": "Новый чат",
        "delete_chat": "Удалить",
        "export_chat": "Экспорт",
        "import_chat": "Импорт",
        "start_cycle": "Запустить цикл",
        "stop_cycle": "Остановить цикл",
        "write_as_bot": "Писать как",
        "clear": "Очистить",
        "ready": "Готов",
        "cycling": "Цикл...",
        "stopped": "Остановлен",
        "typing": "печатает...",
        "no_messages": "Нет сообщений",
        "no_messages_text": "Отправьте начальное сообщение перед запуском цикла.",
        "missing_api_keys": "Отсутствуют API ключи",
        "missing_api_keys_text": "Оба бота должны иметь настроенные API ключи для работы цикла.",
        "streaming": "Стриминг",
        "streaming_text": "Невозможно писать вручную во время стриминга.",
        "edit_message": "Редактировать сообщение",
        "editing_from": "Редактирование сообщения от",
        "save": "Сохранить",
        "cancel": "Отмена",
        "send": "Отправить",
        "write_as": "Написать как",
        "write_a_message_as": "Написать сообщение как",
        "enter_initial_message": "Введите начальное сообщение для начала диалога...",
        "no_api_key_for": "Нет API ключа для",
        "error": "Ошибка",
        "invalid_input": "Неверный ввод",
        "max_tokens_must_be_number": "Макс. токенов должно быть числом.",
        "confirm_delete": "Подтвердите удаление",
        "confirm_delete_chat": "Вы уверены, что хотите удалить этот чат?",
        "cycle_delay": "Задержка между ответами (сек)",
        "untitled_chat": "Безымянный чат",
        "crypto_not_available": "Библиотека cryptography не установлена. API ключи будут храниться в открытом виде. Установите: pip install cryptography",
        "api_format": "Формат API",
    }
}


# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG_FILE = "ai_chat_config.json"
CHATS_DIR = "chats"

DEFAULT_CONFIG = {
    "theme": "dark",
    "font_family": "Segoe UI",
    "font_size": 14,
    "language": "en",
    "cycle_delay": 2.0,
    "current_chat_id": None,
    "keys_encrypted": False,
    "bot1": {
        "name": "Assistant 1",
        "provider": "openai",
        "base_url": "https://api.openai.com/v1",
        "api_key": "",
        "model": "gpt-4o-mini",
        "system_prompt": "You are a helpful assistant engaged in a thoughtful conversation with another AI. Respond naturally and keep the dialogue flowing.",
        "tone": "neutral",
        "emoji_frequency": "none",
        "temperature": 0.7,
        "max_tokens": 1024,
        "ai_language": "auto",
        "api_format": "openai"
    },
    "bot2": {
        "name": "Assistant 2",
        "provider": "anthropic",
        "base_url": "https://api.anthropic.com",
        "api_key": "",
        "model": "claude-sonnet-4-20250514",
        "system_prompt": "You are a helpful assistant engaged in a thoughtful conversation with another AI. Respond naturally and keep the dialogue flowing.",
        "tone": "neutral",
        "emoji_frequency": "none",
        "temperature": 0.7,
        "max_tokens": 1024,
        "ai_language": "auto",
        "api_format": "openai"
    }
}

PRESETS = {
    "OpenAI": {
        "provider": "openai",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    },
    "Anthropic": {
        "provider": "anthropic",
        "base_url": "https://api.anthropic.com",
        "models": ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
    },
    "Ollama": {
        "provider": "ollama",
        "base_url": "http://localhost:11434/v1",
        "models": ["llama3", "mistral", "codellama", "phi3", "qwen2"]
    },
    "Mistral": {
        "provider": "mistral",
        "base_url": "https://api.mistral.ai/v1",
        "models": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest", "open-mistral-7b"]
    },
    "Custom": {
        "provider": "custom",
        "base_url": "",
        "models": []
    }
}

AI_LANGUAGES = [
    "auto", "English", "Russian", "Spanish", "French",
    "German", "Chinese", "Japanese", "Korean", "Portuguese", "Italian"
]


def load_config() -> dict:
    """Load configuration from file, merging with defaults."""
    encryption_key = get_encryption_key()

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            merged = json.loads(json.dumps(DEFAULT_CONFIG))
            for key in merged:
                if key in config:
                    if isinstance(merged[key], dict) and isinstance(config[key], dict):
                        for sub_key in merged[key]:
                            if sub_key in config[key]:
                                merged[key][sub_key] = config[key][sub_key]
                    else:
                        merged[key] = config[key]

            # Decrypt API keys if they were encrypted
            if merged.get("keys_encrypted") and CRYPTO_AVAILABLE:
                for bot_key in ["bot1", "bot2"]:
                    api_key = merged[bot_key].get("api_key", "")
                    if api_key:
                        merged[bot_key]["api_key"] = decrypt_value(api_key, encryption_key)

            # Migrate: encrypt keys if they weren't encrypted before
            if not merged.get("keys_encrypted") and CRYPTO_AVAILABLE:
                for bot_key in ["bot1", "bot2"]:
                    api_key = merged[bot_key].get("api_key", "")
                    if api_key:
                        merged[bot_key]["api_key"] = encrypt_value(api_key, encryption_key)
                merged["keys_encrypted"] = True
                save_config_raw(merged)

            return merged
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_CONFIG))


def save_config_raw(config: dict):
    """Save configuration to file without encryption logic."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to save config: {e}")


def save_config(config: dict):
    """Save configuration to file with encrypted API keys."""
    encryption_key = get_encryption_key()

    # Create a copy for saving
    config_copy = json.loads(json.dumps(config))

    # Encrypt API keys before saving
    if CRYPTO_AVAILABLE and encryption_key:
        for bot_key in ["bot1", "bot2"]:
            api_key = config_copy[bot_key].get("api_key", "")
            if api_key:
                config_copy[bot_key]["api_key"] = encrypt_value(api_key, encryption_key)
        config_copy["keys_encrypted"] = True
    else:
        config_copy["keys_encrypted"] = False

    save_config_raw(config_copy)


def ensure_chats_dir():
    """Ensure the chats directory exists."""
    if not os.path.exists(CHATS_DIR):
        os.makedirs(CHATS_DIR, exist_ok=True)


# ============================================================================
# CHAT MANAGER
# ============================================================================

class ChatManager:
    """Manages chat persistence, loading, and CRUD operations."""

    @staticmethod
    def list_chats() -> List[Dict]:
        """List all saved chats with metadata."""
        ensure_chats_dir()
        chats = []
        for filename in os.listdir(CHATS_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(CHATS_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    chats.append({
                        "id": filename[:-5],
                        "title": data.get("title", "Untitled Chat"),
                        "created": data.get("created", 0),
                        "updated": data.get("updated", 0),
                        "message_count": len(data.get("messages", []))
                    })
                except Exception:
                    continue
        chats.sort(key=lambda x: x["updated"], reverse=True)
        return chats

    @staticmethod
    def create_chat(title: str = "Untitled Chat") -> str:
        """Create a new chat and return its ID."""
        ensure_chats_dir()
        chat_id = str(uuid.uuid4())
        now = time.time()
        data = {
            "id": chat_id,
            "title": title,
            "created": now,
            "updated": now,
            "messages": []
        }
        filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return chat_id

    @staticmethod
    def load_chat(chat_id: str) -> Optional[Dict]:
        """Load a chat by ID."""
        ensure_chats_dir()
        filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    @staticmethod
    def save_chat(chat_id: str, title: str, messages: List[Dict]):
        """Save a chat to disk."""
        ensure_chats_dir()
        filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")

        existing = ChatManager.load_chat(chat_id)
        created = existing.get("created", time.time()) if existing else time.time()

        clean_messages = []
        for msg in messages:
            clean_messages.append({
                "id": msg.get("id", str(uuid.uuid4())),
                "sender": msg.get("sender", ""),
                "content": msg.get("content", ""),
                "model": msg.get("model", "")
            })

        data = {
            "id": chat_id,
            "title": title,
            "created": created,
            "updated": time.time(),
            "messages": clean_messages
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def delete_chat(chat_id: str):
        """Delete a chat by ID."""
        filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)

    @staticmethod
    def export_chat(chat_id: str, dest_path: str) -> bool:
        """Export a chat to a JSON file."""
        chat_data = ChatManager.load_chat(chat_id)
        if not chat_data:
            return False
        try:
            with open(dest_path, "w", encoding="utf-8") as f:
                json.dump(chat_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False

    @staticmethod
    def import_chat(source_path: str) -> Optional[str]:
        """Import a chat from a JSON file. Returns the new chat ID."""
        try:
            with open(source_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "messages" not in data or not isinstance(data["messages"], list):
                return None
            new_id = str(uuid.uuid4())
            data["id"] = new_id
            data["created"] = data.get("created", time.time())
            data["updated"] = time.time()
            ensure_chats_dir()
            filepath = os.path.join(CHATS_DIR, f"{new_id}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return new_id
        except Exception:
            return None


# ============================================================================
# API CLIENT
# ============================================================================

class APIClient:
    """Handles API calls to different LLM providers with streaming support."""

    LANGUAGE_INSTRUCTIONS = {
        "English": "You MUST respond in English.",
        "Russian": "You MUST respond in Russian.",
        "Spanish": "You MUST respond in Spanish.",
        "French": "You MUST respond in French.",
        "German": "You MUST respond in German.",
        "Chinese": "You MUST respond in Chinese.",
        "Japanese": "You MUST respond in Japanese.",
        "Korean": "You MUST respond in Korean.",
        "Portuguese": "You MUST respond in Portuguese.",
        "Italian": "You MUST respond in Italian."
    }

    @staticmethod
    def build_messages(bot_config: dict, conversation_history: list, last_message: str) -> list:
        """Build the message list for an API call from this bot's perspective."""
        messages = []

        system_prompt = bot_config.get("system_prompt", "")
        tone = bot_config.get("tone", "neutral")
        emoji_freq = bot_config.get("emoji_frequency", "none")
        ai_lang = bot_config.get("ai_language", "auto")

        enhanced_prompt = system_prompt

        if ai_lang != "auto" and ai_lang in APIClient.LANGUAGE_INSTRUCTIONS:
            enhanced_prompt += "\n" + APIClient.LANGUAGE_INSTRUCTIONS[ai_lang]

        if tone != "neutral":
            enhanced_prompt += f"\nMaintain a {tone} tone throughout your responses."
        if emoji_freq == "none":
            enhanced_prompt += "\nDo not use any emojis in your responses."
        elif emoji_freq == "rare":
            enhanced_prompt += "\nUse emojis very sparingly, only when absolutely appropriate."
        elif emoji_freq == "occasional":
            enhanced_prompt += "\nFeel free to use occasional emojis when they add meaning."
        elif emoji_freq == "frequent":
            enhanced_prompt += "\nUse emojis frequently to express emotions and add personality."

        if enhanced_prompt.strip():
            messages.append({"role": "system", "content": enhanced_prompt})

        for msg in conversation_history:
            if msg["sender"] == bot_config["name"]:
                messages.append({"role": "assistant", "content": msg["content"]})
            else:
                messages.append({"role": "user", "content": msg["content"]})

        if last_message:
            messages.append({"role": "user", "content": last_message})

        return messages

    @staticmethod
    def stream_response(bot_config: dict, messages: list,
                        token_callback: Callable[[str], None],
                        done_callback: Callable[[], None],
                        error_callback: Callable[[str], None]):
        """Stream a response from the configured API."""
        provider = bot_config["provider"]
        base_url = bot_config["base_url"].rstrip("/")
        api_key = bot_config["api_key"]
        model = bot_config["model"]
        temperature = bot_config.get("temperature", 0.7)
        max_tokens = bot_config.get("max_tokens", 1024)
        api_format = bot_config.get("api_format", "openai")

        try:
            if provider in ["openai", "mistral", "ollama", "custom"]:
                if provider == "custom" and api_format == "anthropic":
                    APIClient._stream_anthropic(
                        base_url, api_key, model, messages,
                        temperature, max_tokens, token_callback, done_callback
                    )
                else:
                    APIClient._stream_openai_compatible(
                        base_url, api_key, model, messages,
                        temperature, max_tokens, token_callback, done_callback
                    )
            elif provider == "anthropic":
                APIClient._stream_anthropic(
                    base_url, api_key, model, messages,
                    temperature, max_tokens, token_callback, done_callback
                )
            else:
                error_callback(f"Unknown provider: {provider}")
        except requests.exceptions.ConnectionError:
            error_callback("Connection failed. Check your Base URL and internet connection.")
        except requests.exceptions.Timeout:
            error_callback("Request timed out. The server took too long to respond.")
        except requests.exceptions.HTTPError as e:
            error_callback(f"HTTP Error: {e.response.status_code} - {e.response.text[:100] if e.response.text else 'Unknown'}")
        except Exception as e:
            error_callback(f"Unexpected error: {str(e)[:100]}")

    @staticmethod
    def _stream_openai_compatible(base_url, api_key, model, messages,
                                   temperature, max_tokens, token_callback, done_callback):
        """Handle streaming for OpenAI-compatible APIs."""
        url = f"{base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if line is None:
                continue
            line = line.strip()
            if not line:
                continue
            if line.startswith("data: "):
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    choices = chunk.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            token_callback(content)
                except json.JSONDecodeError:
                    continue

        done_callback()

    @staticmethod
    def _stream_anthropic(base_url, api_key, model, messages,
                          temperature, max_tokens, token_callback, done_callback):
        """Handle streaming for Anthropic API."""
        url = f"{base_url}/v1/messages"

        system_msg = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append({"role": msg["role"], "content": msg["content"]})

        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": model,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        if system_msg:
            payload["system"] = system_msg

        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if line is None:
                continue
            line = line.strip()
            if not line:
                continue
            if line.startswith("data: "):
                data = line[6:]
                try:
                    event = json.loads(data)
                    event_type = event.get("type", "")
                    if event_type == "content_block_delta":
                        delta = event.get("delta", {})
                        text = delta.get("text", "")
                        if text:
                            token_callback(text)
                    elif event_type == "message_stop":
                        break
                except json.JSONDecodeError:
                    continue

        done_callback()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class AIChatApp:
    """Main application class for the AI Dialogue chat interface."""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AI Dialogue")
        self.root.geometry("1200x800")
        self.root.minsize(width=960, height=640)

        # Check cryptography availability
        if not CRYPTO_AVAILABLE:
            self.root.after(1000, lambda: messagebox.showwarning(
                "Warning",
                TRANSLATIONS["en"]["crypto_not_available"]
            ))

        # Load configuration
        self.config = load_config()
        ensure_chats_dir()

        # Chat state
        self.messages: List[Dict] = []
        self.is_cycling = False
        self.cycle_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.current_streaming = False
        self.streaming_text: Dict[str, str] = {}

        # Current chat
        self.current_chat_id: Optional[str] = self.config.get("current_chat_id")
        self.chat_buttons = {}

        # Store default button colors
        self._btn_default_fg = None
        self._btn_default_hover = None

        # Setup
        self._setup_theme()
        self._setup_ui()
        self._apply_font_settings()
        self._load_current_chat()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def tr(self, key: str) -> str:
        """Get translation for a key."""
        lang = self.config.get("language", "en")
        return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

    # ========================================================================
    # UI SETUP
    # ========================================================================

    def _setup_theme(self):
        """Apply the saved theme."""
        theme = self.config.get("theme", "dark")
        ctk.set_appearance_mode(theme)

    def _setup_ui(self):
        """Build the complete UI layout."""
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Left sidebar
        self.sidebar = ctk.CTkScrollableFrame(self.root, width=340, corner_radius=10)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        # Main content area
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()

    def _build_sidebar(self):
        """Build the sidebar with settings, chats, and bot configurations."""
        title = ctk.CTkLabel(
            self.sidebar, text=self.tr("app_title"),
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(15, 20))

        # Chats section
        self._build_chats_section()

        ctk.CTkFrame(self.sidebar, height=1, fg_color="gray30").pack(
            fill="x", pady=15, padx=15
        )

        # Settings section
        self._build_settings_section()

        ctk.CTkFrame(self.sidebar, height=1, fg_color="gray30").pack(
            fill="x", pady=15, padx=15
        )

        # Bot 1 section
        self._build_bot_section(1, self.config["bot1"])

        ctk.CTkFrame(self.sidebar, height=1, fg_color="gray30").pack(
            fill="x", pady=15, padx=15
        )

        # Bot 2 section
        self._build_bot_section(2, self.config["bot2"])

        ctk.CTkFrame(self.sidebar, height=20).pack()

    def _build_chats_section(self):
        """Build the chats management section."""
        label = ctk.CTkLabel(
            self.sidebar, text=self.tr("chats"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.pack(pady=(0, 10))

        btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkButton(
            btn_frame, text=self.tr("new_chat"), width=100, height=32,
            command=self._create_new_chat, corner_radius=6
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btn_frame, text=self.tr("export_chat"), width=70, height=32,
            command=self._export_chat, corner_radius=6,
            fg_color="gray40"
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame, text=self.tr("import_chat"), width=70, height=32,
            command=self._import_chat, corner_radius=6,
            fg_color="gray40"
        ).pack(side="left", padx=2)

        self.chats_list_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.chats_list_frame.pack(fill="x", padx=15)

        self._refresh_chats_list()

    def _refresh_chats_list(self):
        """Refresh the list of available chats."""
        for widget in self.chats_list_frame.winfo_children():
            widget.destroy()
        self.chat_buttons.clear()

        chats = ChatManager.list_chats()
        for chat in chats:
            chat_frame = ctk.CTkFrame(
                self.chats_list_frame, corner_radius=6,
                fg_color="transparent", height=40
            )
            chat_frame.pack(fill="x", pady=2)
            chat_frame.grid_columnconfigure(0, weight=1)

            is_current = chat["id"] == self.current_chat_id
            bg_color = ("gray80", "gray35") if is_current else "transparent"

            btn = ctk.CTkButton(
                chat_frame,
                text=chat["title"],
                anchor="w",
                height=32,
                corner_radius=6,
                fg_color=bg_color,
                hover_color=("gray70", "gray45"),
                command=lambda cid=chat["id"]: self._switch_chat(cid)
            )
            btn.grid(row=0, column=0, sticky="ew", padx=(2, 0), pady=2)

            del_btn = ctk.CTkButton(
                chat_frame,
                text="x",
                width=30, height=32,
                corner_radius=6,
                fg_color="#C62828",
                hover_color="#8B0000",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda cid=chat["id"]: self._delete_chat(cid)
            )
            del_btn.grid(row=0, column=1, padx=(0, 2), pady=2)

            self.chat_buttons[chat["id"]] = btn

    def _build_settings_section(self):
        """Build the settings section."""
        label = ctk.CTkLabel(
            self.sidebar, text=self.tr("settings"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.pack(pady=(0, 10))

        # App language
        self._create_field_with_label(
            "settings", "language", self.tr("app_language"),
            widget_type="combobox",
            values=["en", "ru"],
            default_value=self.config["language"],
            command=self._change_app_language,
            width=150
        )

        # Theme
        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_frame.pack(fill="x", padx=15, pady=(0, 5))

        ctk.CTkLabel(theme_frame, text=self.tr("appearance"), font=ctk.CTkFont(size=12)).pack(
            anchor="w", pady=(5, 3)
        )

        theme_radio_frame = ctk.CTkFrame(theme_frame, fg_color="transparent")
        theme_radio_frame.pack(fill="x")

        self.theme_var = ctk.StringVar(value=self.config["theme"])
        ctk.CTkRadioButton(
            theme_radio_frame, text=self.tr("dark"), variable=self.theme_var,
            value="dark", command=self._change_theme
        ).pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(
            theme_radio_frame, text=self.tr("light"), variable=self.theme_var,
            value="light", command=self._change_theme
        ).pack(side="left")

        # Font family
        font_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        font_frame.pack(fill="x", padx=15, pady=(5, 5))

        ctk.CTkLabel(font_frame, text=self.tr("font_family"), font=ctk.CTkFont(size=12)).pack(
            anchor="w", pady=(5, 3)
        )

        available_fonts = [
            "Segoe UI", "Arial", "Helvetica", "Courier New",
            "Georgia", "Verdana", "Times New Roman", "Consolas"
        ]
        self.font_var = ctk.StringVar(value=self.config["font_family"])
        ctk.CTkComboBox(
            font_frame, values=available_fonts, variable=self.font_var,
            command=self._change_font
        ).pack(fill="x")

        # Font size
        size_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        size_frame.pack(fill="x", padx=15, pady=(5, 5))

        size_header = ctk.CTkFrame(size_frame, fg_color="transparent")
        size_header.pack(fill="x", pady=(5, 0))
        ctk.CTkLabel(size_header, text=self.tr("font_size"), font=ctk.CTkFont(size=12)).pack(side="left")
        self.size_display = ctk.CTkLabel(size_header, text=str(self.config["font_size"]),
                                          font=ctk.CTkFont(size=12, weight="bold"))
        self.size_display.pack(side="right")

        self.size_slider = ctk.CTkSlider(
            size_frame, from_=10, to=24, number_of_steps=14,
            command=self._on_size_slider_change
        )
        self.size_slider.set(self.config["font_size"])
        self.size_slider.pack(fill="x", pady=(5, 5))

        # Cycle delay
        delay_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        delay_frame.pack(fill="x", padx=15, pady=(5, 5))

        delay_header = ctk.CTkFrame(delay_frame, fg_color="transparent")
        delay_header.pack(fill="x", pady=(5, 0))
        ctk.CTkLabel(delay_header, text=self.tr("cycle_delay"), font=ctk.CTkFont(size=12)).pack(side="left")
        self.delay_display = ctk.CTkLabel(delay_header, text=f"{self.config.get('cycle_delay', 2.0):.1f}s",
                                           font=ctk.CTkFont(size=12, weight="bold"))
        self.delay_display.pack(side="right")

        self.delay_slider = ctk.CTkSlider(
            delay_frame, from_=0.5, to=10.0, number_of_steps=19,
            command=self._on_delay_slider_change
        )
        self.delay_slider.set(self.config.get("cycle_delay", 2.0))
        self.delay_slider.pack(fill="x", pady=(5, 5))

    def _build_bot_section(self, bot_num: int, bot_config: dict):
        """Build configuration section for a specific bot."""
        bot_key = f"bot{bot_num}"

        ctk.CTkLabel(
            self.sidebar, text=f"{self.tr('bot')} {bot_num}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 8))

        self._create_field_with_label(
            bot_key, "preset", self.tr("preset"),
            widget_type="combobox",
            values=list(PRESETS.keys()),
            default_value="Custom",
            command=lambda v, b=bot_num: self._apply_preset(b, v),
            width=150
        )

        self._create_field_with_label(
            bot_key, "name", self.tr("name"),
            widget_type="entry",
            default_value=bot_config["name"],
            bind_key=True
        )

        self._create_field_with_label(
            bot_key, "provider", self.tr("provider"),
            widget_type="combobox",
            values=["openai", "anthropic", "ollama", "mistral", "custom"],
            default_value=bot_config["provider"],
            bind_key=True
        )

        self._create_field_with_label(
            bot_key, "base_url", self.tr("base_url"),
            widget_type="entry",
            default_value=bot_config["base_url"],
            bind_key=True
        )

        self._create_field_with_label(
            bot_key, "api_key", self.tr("api_key"),
            widget_type="entry",
            default_value=bot_config["api_key"],
            show_char="*",
            bind_key=True
        )

        self._create_field_with_label(
            bot_key, "model", self.tr("model"),
            widget_type="entry",
            default_value=bot_config["model"],
            bind_key=True
        )

        ctk.CTkButton(
            self.sidebar, text=self.tr("advanced_settings"),
            command=lambda b=bot_num: self._show_advanced_settings(b),
            height=32, corner_radius=6
        ).pack(fill="x", padx=15, pady=(10, 5))

    def _create_field_with_label(self, section_key, field, label_text, widget_type,
                                  default_value="", values=None, command=None,
                                  show_char=None, bind_key=False, width=150):
        """Create a labeled input field."""
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=2)

        ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=12)).pack(
            anchor="w", pady=(5, 2)
        )

        if widget_type == "entry":
            entry = ctk.CTkEntry(frame, width=width)
            if show_char:
                entry.configure(show=show_char)
            entry.insert(0, default_value)
            entry.pack(fill="x", pady=(0, 3))

            if bind_key:
                if section_key == "settings":
                    entry.bind(
                        "<KeyRelease>",
                        lambda e, f=field: self._update_config_section(f, e.widget.get())
                    )
                else:
                    entry.bind(
                        "<KeyRelease>",
                        lambda e, sk=section_key, f=field: self._update_config(sk, f, e.widget.get())
                    )
            setattr(self, f"{section_key}_{field}", entry)

        elif widget_type == "combobox":
            var = ctk.StringVar(value=default_value)
            combo = ctk.CTkComboBox(
                frame, values=values or [], variable=var, width=width,
                command=lambda v, sk=section_key, f=field, cmd=command: self._on_combobox_change(sk, f, v, cmd)
            )
            combo.pack(fill="x", pady=(0, 3))
            setattr(self, f"{section_key}_{field}_var", var)
            setattr(self, f"{section_key}_{field}_combo", combo)

    def _build_main_area(self):
        """Build the main chat area."""
        control_frame = ctk.CTkFrame(self.main_frame, height=55, corner_radius=8)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        control_frame.grid_columnconfigure(2, weight=1)

        self.cycle_btn = ctk.CTkButton(
            control_frame, text=self.tr("start_cycle"), width=120, height=35,
            command=self._toggle_cycle,
            font=ctk.CTkFont(size=13, weight="bold"), corner_radius=6
        )
        self.cycle_btn.grid(row=0, column=0, padx=10, pady=10)

        self._btn_default_fg = self.cycle_btn.cget("fg_color")
        self._btn_default_hover = self.cycle_btn.cget("hover_color")

        self.status_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        self.status_frame.grid(row=0, column=1, padx=10, pady=10)

        self.status_dot = ctk.CTkLabel(
            self.status_frame, text="", width=10, height=10,
            fg_color="#4CAF50", corner_radius=5
        )
        self.status_dot.pack(side="left", padx=(0, 5))

        self.status_label = ctk.CTkLabel(
            self.status_frame, text=self.tr("ready"),
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left")

        write_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        write_frame.grid(row=0, column=2, padx=10, sticky="e")

        self.write_btn1 = ctk.CTkButton(
            write_frame, text=f"{self.tr('write_as_bot')} 1", width=110, height=30,
            command=lambda: self._write_as_bot(1), corner_radius=6
        )
        self.write_btn1.pack(side="left", padx=3)

        self.write_btn2 = ctk.CTkButton(
            write_frame, text=f"{self.tr('write_as_bot')} 2", width=110, height=30,
            command=lambda: self._write_as_bot(2), corner_radius=6
        )
        self.write_btn2.pack(side="left", padx=3)

        self.clear_btn = ctk.CTkButton(
            control_frame, text=self.tr("clear"), width=70, height=35,
            command=self._clear_chat,
            fg_color="#C62828", hover_color="#8B0000",
            font=ctk.CTkFont(size=12), corner_radius=6
        )
        self.clear_btn.grid(row=0, column=3, padx=10, pady=10)

        self.chat_scroll = ctk.CTkScrollableFrame(
            self.main_frame, corner_radius=8, fg_color=("gray90", "gray17")
        )
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        input_frame = ctk.CTkFrame(self.main_frame, height=55, corner_radius=8)
        input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text=self.tr("enter_initial_message"),
            height=36, corner_radius=6
        )
        self.input_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.input_entry.bind("<Return>", lambda e: self._send_initial_message())

        self.send_btn = ctk.CTkButton(
            input_frame, text=self.tr("send"), width=80, height=36,
            command=self._send_initial_message, corner_radius=6
        )
        self.send_btn.grid(row=0, column=1, padx=(5, 10), pady=10)

    # ========================================================================
    # CHAT MANAGEMENT
    # ========================================================================

    def _create_new_chat(self):
        """Create a new chat and switch to it."""
        chat_id = ChatManager.create_chat(self.tr("untitled_chat"))
        self._switch_chat(chat_id)
        self._refresh_chats_list()

    def _switch_chat(self, chat_id: str):
        """Switch to a different chat."""
        if self.current_chat_id:
            self._save_current_chat()

        if self.is_cycling:
            self._stop_cycle()

        chat_data = ChatManager.load_chat(chat_id)
        if chat_data:
            self.messages = chat_data.get("messages", [])
        else:
            self.messages = []

        self.current_chat_id = chat_id
        self.config["current_chat_id"] = chat_id
        save_config(self.config)

        self._rerender_all_messages()
        self._refresh_chats_list()

    def _delete_chat(self, chat_id: str):
        """Delete a chat after confirmation."""
        if not messagebox.askyesno(self.tr("confirm_delete"), self.tr("confirm_delete_chat")):
            return

        ChatManager.delete_chat(chat_id)

        if chat_id == self.current_chat_id:
            chats = ChatManager.list_chats()
            if chats:
                self._switch_chat(chats[0]["id"])
            else:
                new_id = ChatManager.create_chat(self.tr("untitled_chat"))
                self._switch_chat(new_id)

        self._refresh_chats_list()

    def _save_current_chat(self):
        """Save the current chat to disk."""
        if not self.current_chat_id:
            return

        title = self.tr("untitled_chat")
        if self.messages:
            first_msg = self.messages[0].get("content", "")
            if first_msg:
                title = first_msg[:50] + ("..." if len(first_msg) > 50 else "")

        ChatManager.save_chat(self.current_chat_id, title, self.messages)

    def _load_current_chat(self):
        """Load the current chat on startup."""
        if self.current_chat_id:
            chat_data = ChatManager.load_chat(self.current_chat_id)
            if chat_data:
                self.messages = chat_data.get("messages", [])
            else:
                self.messages = []
        else:
            self.messages = []

    def _export_chat(self):
        """Export the current chat to a file."""
        if not self.current_chat_id:
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Chat"
        )
        if filepath:
            if ChatManager.export_chat(self.current_chat_id, filepath):
                messagebox.showinfo("Success", "Chat exported successfully.")
            else:
                messagebox.showerror("Error", "Failed to export chat.")

    def _import_chat(self):
        """Import a chat from a file."""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Chat"
        )
        if filepath:
            new_id = ChatManager.import_chat(filepath)
            if new_id:
                self._switch_chat(new_id)
                self._refresh_chats_list()
                messagebox.showinfo("Success", "Chat imported successfully.")
            else:
                messagebox.showerror("Error", "Failed to import chat. Invalid file format.")

    # ========================================================================
    # SETTINGS HANDLERS
    # ========================================================================

    def _change_theme(self):
        """Change the application theme."""
        self.config["theme"] = self.theme_var.get()
        ctk.set_appearance_mode(self.config["theme"])
        save_config(self.config)

    def _change_font(self, font_name: str):
        """Change the font family."""
        self.config["font_family"] = font_name
        self._apply_font_settings()
        save_config(self.config)

    def _on_size_slider_change(self, value):
        """Handle font size slider changes."""
        size = int(value)
        self.config["font_size"] = size
        self.size_display.configure(text=str(size))
        self._apply_font_settings()
        save_config(self.config)

    def _on_delay_slider_change(self, value):
        """Handle cycle delay slider changes."""
        delay = round(float(value), 1)
        self.config["cycle_delay"] = delay
        self.delay_display.configure(text=f"{delay:.1f}s")
        save_config(self.config)

    def _apply_font_settings(self):
        """Apply font settings to the application."""
        font_family = self.config["font_family"]
        font_size = self.config["font_size"]
        try:
            self.root.option_add("*Font", (font_family, font_size))
        except tk.TclError:
            pass

    def _change_app_language(self, lang: str):
        """Change the application language."""
        self.config["language"] = lang
        save_config(self.config)
        messagebox.showinfo(
            "Language Changed",
            "Please restart the application for all UI elements to update."
        )

    def _update_config(self, section_key: str, field: str, value: str):
        """Update a configuration field and save."""
        self.config[section_key][field] = value
        save_config(self.config)

    def _update_config_section(self, field: str, value: str):
        """Update a top-level configuration field and save."""
        self.config[field] = value
        save_config(self.config)

    def _on_combobox_change(self, section_key: str, field: str, value: str, extra_command=None):
        """Handle combobox changes."""
        if section_key == "settings":
            self.config[field] = value
        else:
            self.config[section_key][field] = value
        save_config(self.config)
        if extra_command:
            extra_command(value)

    def _apply_preset(self, bot_num: int, preset_name: str):
        """Apply a preset configuration to a bot."""
        bot_key = f"bot{bot_num}"
        preset = PRESETS.get(preset_name)
        if not preset:
            return

        self.config[bot_key]["provider"] = preset["provider"]
        self.config[bot_key]["base_url"] = preset["base_url"]
        if preset["models"]:
            self.config[bot_key]["model"] = preset["models"][0]
        else:
            self.config[bot_key]["model"] = ""

        if hasattr(self, f"{bot_key}_provider_combo"):
            getattr(self, f"{bot_key}_provider_combo").set(preset["provider"])
        if hasattr(self, f"{bot_key}_base_url"):
            entry = getattr(self, f"{bot_key}_base_url")
            entry.delete(0, "end")
            entry.insert(0, preset["base_url"])
        if hasattr(self, f"{bot_key}_model"):
            entry = getattr(self, f"{bot_key}_model")
            entry.delete(0, "end")
            entry.insert(0, preset["models"][0] if preset["models"] else "")

        save_config(self.config)

    def _show_advanced_settings(self, bot_num: int):
        """Show the advanced settings dialog for a bot."""
        bot_key = f"bot{bot_num}"
        bot_config = self.config[bot_key]

        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"{self.tr('bot')} {bot_num} - {self.tr('advanced_settings')}")
        dialog.geometry("550x750")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ctk.CTkScrollableFrame(dialog, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=25, pady=20)

        # System Prompt
        ctk.CTkLabel(
            frame, text=self.tr("system_prompt"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        sys_prompt_text = ctk.CTkTextbox(frame, height=120, corner_radius=6)
        sys_prompt_text.insert("1.0", bot_config.get("system_prompt", ""))
        sys_prompt_text.pack(fill="x", pady=(0, 15))

        # Tone
        ctk.CTkLabel(
            frame, text=self.tr("tone"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        tone_var = ctk.StringVar(value=bot_config.get("tone", "neutral"))
        ctk.CTkComboBox(
            frame,
            values=["neutral", "friendly", "formal", "casual", "academic", "creative", "sarcastic"],
            variable=tone_var, width=250
        ).pack(anchor="w", pady=(0, 15))

        # Emoji Frequency
        ctk.CTkLabel(
            frame, text=self.tr("emoji_frequency"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        emoji_var = ctk.StringVar(value=bot_config.get("emoji_frequency", "none"))
        ctk.CTkComboBox(
            frame,
            values=["none", "rare", "occasional", "frequent"],
            variable=emoji_var, width=250
        ).pack(anchor="w", pady=(0, 15))

        # AI Language
        ctk.CTkLabel(
            frame, text=self.tr("ai_language"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        lang_var = ctk.StringVar(value=bot_config.get("ai_language", "auto"))
        ctk.CTkComboBox(
            frame,
            values=AI_LANGUAGES,
            variable=lang_var, width=250
        ).pack(anchor="w", pady=(0, 15))

        # API Format (for custom provider)
        ctk.CTkLabel(
            frame, text=self.tr("api_format"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        api_format_var = ctk.StringVar(value=bot_config.get("api_format", "openai"))
        ctk.CTkComboBox(
            frame,
            values=["openai", "anthropic"],
            variable=api_format_var, width=250
        ).pack(anchor="w", pady=(0, 15))

        # Temperature
        temp_value = bot_config.get("temperature", 0.7)
        temp_label = ctk.CTkLabel(
            frame, text=f"{self.tr('temperature')}: {temp_value:.1f}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        temp_label.pack(anchor="w", pady=(0, 5))
        temp_slider = ctk.CTkSlider(frame, from_=0.0, to=2.0, number_of_steps=20)
        temp_slider.set(temp_value)
        temp_slider.pack(fill="x", pady=(0, 3))

        temp_display = ctk.CTkLabel(frame, text=f"{temp_value:.1f}")
        temp_display.pack(anchor="w", pady=(0, 15))

        def update_temp_display(val):
            temp_display.configure(text=f"{float(val):.1f}")
            temp_label.configure(text=f"{self.tr('temperature')}: {float(val):.1f}")
        temp_slider.configure(command=update_temp_display)

        # Max Tokens
        ctk.CTkLabel(
            frame, text=self.tr("max_tokens"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        tokens_entry = ctk.CTkEntry(frame, width=250)
        tokens_entry.insert(0, str(bot_config.get("max_tokens", 1024)))
        tokens_entry.pack(anchor="w", pady=(0, 20))

        def save_settings():
            self.config[bot_key]["system_prompt"] = sys_prompt_text.get("1.0", "end").strip()
            self.config[bot_key]["tone"] = tone_var.get()
            self.config[bot_key]["emoji_frequency"] = emoji_var.get()
            self.config[bot_key]["ai_language"] = lang_var.get()
            self.config[bot_key]["api_format"] = api_format_var.get()
            self.config[bot_key]["temperature"] = temp_slider.get()
            try:
                self.config[bot_key]["max_tokens"] = int(tokens_entry.get())
            except ValueError:
                messagebox.showwarning(self.tr("invalid_input"), self.tr("max_tokens_must_be_number"))
                return
            save_config(self.config)
            dialog.destroy()

        ctk.CTkButton(
            frame, text=self.tr("save_settings"), command=save_settings,
            font=ctk.CTkFont(size=14, weight="bold"), height=38, corner_radius=6
        ).pack(fill="x", pady=(10, 0))

    # ========================================================================
    # CHAT FUNCTIONALITY
    # ========================================================================

    def _send_initial_message(self):
        """Send the initial message from the input field."""
        if self.current_streaming:
            return

        text = self.input_entry.get().strip()
        if not text:
            return

        self.input_entry.delete(0, "end")

        msg = {
            "id": str(uuid.uuid4()),
            "sender": self.config["bot1"]["name"],
            "content": text,
            "model": self.config["bot1"]["model"]
        }
        self.messages.append(msg)
        self._render_message(msg, len(self.messages) - 1)
        self._auto_scroll()
        self._save_current_chat()

        self._request_response(2)

    def _toggle_cycle(self):
        """Toggle the automatic cycling between bots."""
        if self.is_cycling:
            self._stop_cycle()
        else:
            self._start_cycle()

    def _start_cycle(self):
        """Start the automatic conversation cycle."""
        if not self.messages:
            messagebox.showwarning(self.tr("no_messages"), self.tr("no_messages_text"))
            return

        bot1_key = self.config["bot1"].get("api_key", "")
        bot2_key = self.config["bot2"].get("api_key", "")
        if (not bot1_key and self.config["bot1"]["provider"] != "ollama") or \
           (not bot2_key and self.config["bot2"]["provider"] != "ollama"):
            messagebox.showwarning(
                self.tr("missing_api_keys"),
                self.tr("missing_api_keys_text")
            )
            return

        self.is_cycling = True
        self.stop_event.clear()
        self.cycle_btn.configure(
            text=self.tr("stop_cycle"),
            fg_color="#C62828",
            hover_color="#8B0000"
        )
        self._set_status(self.tr("cycling"), "#FF9800")

        self.cycle_thread = threading.Thread(target=self._cycle_loop, daemon=True)
        self.cycle_thread.start()

    def _stop_cycle(self):
        """Stop the automatic conversation cycle."""
        self.is_cycling = False
        self.stop_event.set()

        self.cycle_btn.configure(
            text=self.tr("start_cycle"),
            fg_color=self._btn_default_fg,
            hover_color=self._btn_default_hover
        )
        self._set_status(self.tr("stopped"), "#FFC107")

    def _cycle_loop(self):
        """Main loop for automatic cycling between bots."""
        while self.is_cycling and not self.stop_event.is_set():
            if not self.messages:
                break

            last_sender = self.messages[-1]["sender"]
            if last_sender == self.config["bot1"]["name"]:
                next_bot = 2
            else:
                next_bot = 1

            self._request_response_sync(next_bot)

            if self.stop_event.is_set():
                break

            delay = self.config.get("cycle_delay", 2.0)
            steps = int(delay * 5)
            if steps <= 0:
                steps = 1
            sleep_per_step = delay / steps

            for _ in range(steps):
                if self.stop_event.is_set():
                    break
                time.sleep(sleep_per_step)

        self.root.after(0, self._stop_cycle)

    def _request_response(self, bot_num: int):
        """Request a response from a bot (asynchronous)."""
        thread = threading.Thread(target=self._request_response_sync, args=(bot_num,), daemon=True)
        thread.start()

    def _request_response_sync(self, bot_num: int):
        """Request a response from a bot (synchronous, runs in thread)."""
        bot_key = f"bot{bot_num}"
        bot_config = self.config[bot_key]

        if not bot_config.get("api_key") and bot_config["provider"] != "ollama":
            self.root.after(0, lambda: self._set_status(
                f"{self.tr('no_api_key_for')} {self.tr('bot')} {bot_num}", "#F44336"
            ))
            return

        self.root.after(0, lambda: self._set_status(
            f"{self.tr('bot')} {bot_num} {self.tr('typing')}", "#2196F3"
        ))
        self.current_streaming = True

        last_message = self.messages[-1]["content"] if self.messages else ""
        conversation_history = self.messages[:-1]
        api_messages = APIClient.build_messages(bot_config, conversation_history, last_message)

        msg_id = str(uuid.uuid4())
        msg = {
            "id": msg_id,
            "sender": bot_config["name"],
            "content": "",
            "model": bot_config["model"]
        }
        self.streaming_text[msg_id] = ""

        self.root.after(0, lambda: self._add_streaming_message(msg))

        def on_token(token: str):
            self.streaming_text[msg_id] = self.streaming_text.get(msg_id, "") + token
            self.root.after(0, lambda t=token, mid=msg_id: self._update_streaming_message(mid, t))

        def on_done():
            msg["content"] = self.streaming_text.get(msg_id, "")
            self.current_streaming = False
            self.messages.append(msg)
            self.root.after(0, lambda: self._set_status(self.tr("ready"), "#4CAF50"))
            self.root.after(0, lambda mid=msg_id: self._finalize_streaming_message(mid))
            self.root.after(0, self._save_current_chat)

        def on_error(error: str):
            self.current_streaming = False
            self.root.after(0, lambda: self._set_status(
                f"{self.tr('error')}: {error[:60]}", "#F44336"
            ))
            self.root.after(0, lambda mid=msg_id: self._remove_streaming_message(mid))

        APIClient.stream_response(bot_config, api_messages, on_token, on_done, on_error)

    # ========================================================================
    # STREAMING MESSAGE HANDLING
    # ========================================================================

    def _add_streaming_message(self, msg: dict):
        """Add a streaming message placeholder to the chat."""
        msg_id = msg["id"]
        frame = ctk.CTkFrame(self.chat_scroll, corner_radius=8)
        row = len(self.chat_scroll.winfo_children())
        frame.grid(row=row, column=0, sticky="ew", pady=14, padx=10)
        frame.grid_columnconfigure(0, weight=1)

        setattr(self, f"_stream_frame_{msg_id}", frame)

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 0))

        ctk.CTkLabel(
            header, text=msg["sender"],
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            header, text=f"  |  {msg['model']}",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        ).pack(side="left")

        typing_label = ctk.CTkLabel(
            header, text=self.tr("typing"),
            font=ctk.CTkFont(size=11),
            text_color="#FF9800"
        )
        typing_label.pack(side="right")
        setattr(self, f"_stream_typing_{msg_id}", typing_label)

        content_label = ctk.CTkLabel(
            frame, text="", anchor="w", justify="left",
            wraplength=700, font=ctk.CTkFont(size=self.config["font_size"])
        )
        content_label.grid(row=1, column=0, sticky="ew", padx=12, pady=(5, 10))
        setattr(self, f"_stream_content_{msg_id}", content_label)

        self._auto_scroll()

    def _update_streaming_message(self, msg_id: str, token: str):
        """Update a streaming message with a new token."""
        content_label = getattr(self, f"_stream_content_{msg_id}", None)
        if content_label:
            current_text = self.streaming_text.get(msg_id, "")
            content_label.configure(text=current_text)
            self._auto_scroll()

    def _finalize_streaming_message(self, msg_id: str):
        """Replace streaming placeholder with a finalized interactive message."""
        frame = getattr(self, f"_stream_frame_{msg_id}", None)
        if frame:
            frame.destroy()

        for attr_suffix in [f"_stream_frame_{msg_id}", f"_stream_typing_{msg_id}",
                           f"_stream_content_{msg_id}"]:
            if hasattr(self, attr_suffix):
                delattr(self, attr_suffix)

        if self.messages:
            idx = len(self.messages) - 1
            self._render_message(self.messages[idx], idx)

    def _remove_streaming_message(self, msg_id: str):
        """Remove a streaming message on error."""
        frame = getattr(self, f"_stream_frame_{msg_id}", None)
        if frame:
            frame.destroy()
        for attr_suffix in [f"_stream_frame_{msg_id}", f"_stream_typing_{msg_id}",
                           f"_stream_content_{msg_id}"]:
            if hasattr(self, attr_suffix):
                delattr(self, attr_suffix)
        if msg_id in self.streaming_text:
            del self.streaming_text[msg_id]

    # ========================================================================
    # MESSAGE RENDERING AND INTERACTION
    # ========================================================================

    def _render_message(self, msg: dict, index: int):
        """Render a message with interactive controls."""
        frame = ctk.CTkFrame(self.chat_scroll, corner_radius=8)
        frame.grid(row=index, column=0, sticky="ew", pady=14, padx=10)
        frame.grid_columnconfigure(0, weight=1)

        msg["_frame"] = frame

        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 0))

        ctk.CTkLabel(
            header, text=msg["sender"],
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            header, text=f"  |  {msg['model']}",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        ).pack(side="left")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        edit_btn = ctk.CTkButton(
            btn_frame, text=self.tr("edit_message"), width=55, height=26,
            font=ctk.CTkFont(size=11), corner_radius=4,
            command=lambda i=index: self._edit_message(i)
        )
        edit_btn.pack(side="left", padx=2)

        del_btn = ctk.CTkButton(
            btn_frame, text=self.tr("delete_chat"), width=60, height=26,
            font=ctk.CTkFont(size=11), corner_radius=4,
            fg_color="#C62828", hover_color="#8B0000",
            command=lambda i=index: self._delete_message(i)
        )
        del_btn.pack(side="left", padx=2)

        content_label = ctk.CTkLabel(
            frame, text=msg["content"], anchor="w", justify="left",
            wraplength=700, font=ctk.CTkFont(size=self.config["font_size"])
        )
        content_label.grid(row=1, column=0, sticky="ew", padx=12, pady=(5, 10))
        msg["_content_label"] = content_label

    def _edit_message(self, index: int):
        """Open a dialog to edit a message."""
        if index >= len(self.messages):
            return

        msg = self.messages[index]

        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.tr("edit_message"))
        dialog.geometry("550x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=f"{self.tr('editing_from')} {msg['sender']}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 10))

        text_box = ctk.CTkTextbox(dialog, height=180, corner_radius=6)
        text_box.pack(fill="both", expand=True, padx=25, pady=10)
        text_box.insert("1.0", msg["content"])

        def save_edit():
            new_text = text_box.get("1.0", "end").strip()
            if new_text:
                msg["content"] = new_text
                if "_content_label" in msg:
                    msg["_content_label"].configure(text=new_text)
                self._save_current_chat()
            dialog.destroy()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))
        ctk.CTkButton(btn_frame, text=self.tr("save"), command=save_edit, width=80,
                     corner_radius=6).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=self.tr("cancel"), command=dialog.destroy, width=80,
                     fg_color="gray40", corner_radius=6).pack(side="left", padx=10)

    def _delete_message(self, index: int):
        """Delete a message and its paired response/request."""
        if index >= len(self.messages):
            return

        indices_to_delete = set()

        if index % 2 == 0:
            indices_to_delete.add(index)
            if index + 1 < len(self.messages):
                indices_to_delete.add(index + 1)
        else:
            indices_to_delete.add(index)
            if index - 1 >= 0:
                indices_to_delete.add(index - 1)

        for idx in sorted(indices_to_delete, reverse=True):
            if idx < len(self.messages):
                msg = self.messages[idx]
                if "_frame" in msg:
                    try:
                        msg["_frame"].destroy()
                    except tk.TclError:
                        pass

        for idx in sorted(indices_to_delete, reverse=True):
            if idx < len(self.messages):
                del self.messages[idx]

        self._rerender_all_messages()
        self._save_current_chat()

    def _rerender_all_messages(self):
        """Clear and re-render all messages with correct indices."""
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()

        for i, msg in enumerate(self.messages):
            for key in ["_frame", "_content_label"]:
                if key in msg:
                    del msg[key]
            self._render_message(msg, i)

    def _write_as_bot(self, bot_num: int):
        """Open a dialog to manually write a message as a specific bot."""
        if self.current_streaming:
            messagebox.showwarning(self.tr("streaming"), self.tr("streaming_text"))
            return

        bot_key = f"bot{bot_num}"
        bot_config = self.config[bot_key]

        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"{self.tr('write_as')} {bot_config['name']}")
        dialog.geometry("550x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=f"{self.tr('write_a_message_as')} {bot_config['name']}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 10))

        text_box = ctk.CTkTextbox(dialog, height=180, corner_radius=6)
        text_box.pack(fill="both", expand=True, padx=25, pady=10)

        def send_msg():
            text = text_box.get("1.0", "end").strip()
            if not text:
                return

            msg = {
                "id": str(uuid.uuid4()),
                "sender": bot_config["name"],
                "content": text,
                "model": bot_config["model"]
            }
            self.messages.append(msg)
            self._render_message(msg, len(self.messages) - 1)
            self._auto_scroll()
            self._save_current_chat()
            dialog.destroy()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))
        ctk.CTkButton(btn_frame, text=self.tr("send"), command=send_msg, width=80,
                     corner_radius=6).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=self.tr("cancel"), command=dialog.destroy, width=80,
                     fg_color="gray40", corner_radius=6).pack(side="left", padx=10)

    def _clear_chat(self):
        """Clear all chat messages."""
        if self.current_streaming:
            messagebox.showwarning(self.tr("streaming"), self.tr("streaming_text"))
            return

        self.messages.clear()
        self.streaming_text.clear()
        for widget in self.chat_scroll.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass
        self._set_status(self.tr("ready"), "#4CAF50")
        self._save_current_chat()

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _set_status(self, text: str, color: str = "#4CAF50"):
        """Update the status indicator and label."""
        self.status_label.configure(text=text)
        self.status_dot.configure(fg_color=color)

    def _auto_scroll(self):
        """Scroll the chat to the bottom."""
        try:
            self.chat_scroll._parent_canvas.yview_moveto(1.0)
        except (AttributeError, tk.TclError):
            pass

    def _on_close(self):
        """Handle application close."""
        if self.is_cycling:
            self._stop_cycle()
        self._save_current_chat()
        self.root.destroy()

    def run(self):
        """Start the application main loop."""
        self.root.mainloop()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    app = AIChatApp()
    app.run()
