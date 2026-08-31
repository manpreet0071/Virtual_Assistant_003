import argparse
import asyncio
import sys

import importlib, os

# Lazy import helper — import modules only when needed. Some backend modules
# execute long-running loops at import-time (ImageGeneration, etc.), so avoid
# top-level imports to keep the orchestrator responsive.

def _lazy_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        print(f"[run_app] Could not import {module_name}: {e}")
        return None

# Helper to import an attribute from a module lazily
def _lazy_attr(module_name: str, attr: str):
    mod = _lazy_import(module_name)
    if not mod:
        return None
    return getattr(mod, attr, None)


def run_assistant_loop():
    chatbot = _lazy_import('chatbot')
    if chatbot is None:
        print("chatbot module not available. Ensure backend/chatbot.py exists and imports succeed.")
        return

    print("=== Assistant mode (SmartRouter) ===\nType 'exit' to quit.\n")
    while True:
        user_input = input('> ').strip()
        if user_input.lower() in ('exit', 'quit'):
            print("Exiting assistant.")
            break
        try:
            response = chatbot.SmartRouter(user_input)
            print("\nResponse:\n", response)
        except Exception as e:
            print("Error running SmartRouter:", e)


def run_smart_once(prompt: str):
    chatbot = _lazy_import('chatbot')
    if chatbot is None:
        print("chatbot module not available.")
        return
    print(chatbot.SmartRouter(prompt))


def run_chatbot_ai_once(prompt: str):
    chatbot = _lazy_import('chatbot')
    if chatbot is None:
        print("chatbot module not available.")
        return
    print(chatbot.ChatBotAI(prompt))


def run_modal(prompt: str):
    FirstLayerDMM = _lazy_attr('Modal', 'FirstLayerDMM')
    if FirstLayerDMM is None:
        print("Modal.FirstLayerDMM not available.")
        return
    print(FirstLayerDMM(prompt))


def run_realtime(prompt: str):
    RealtimeSearchEngine = _lazy_attr('RealtimeSearchEngine', 'RealtimeSearchEngine')
    if RealtimeSearchEngine is None:
        print("RealtimeSearchEngine not available.")
        return
    print(RealtimeSearchEngine(prompt))


async def run_automation(commands: list[str]):
    Automation_engine = _lazy_import('Automation_engine')
    if Automation_engine is None:
        print("Automation_engine not available.")
        return
    if not hasattr(Automation_engine, 'Automation'):
        print("Automation_engine.Automation not found.")
        return
    results = await Automation_engine.Automation(commands)
    print(results)


def run_tts(text: str):
    TTS = _lazy_attr('TTS', 'TTS')
    if TTS is None:
        print("TTS module not available.")
        return
    TTS(text)
    print("Sent to TTS (non-blocking).")


def run_image(prompt: str):
    ImageGeneration = _lazy_import('ImageGeneration')
    if ImageGeneration is None or not hasattr(ImageGeneration, 'generate'):
        print("ImageGeneration.generate not available.")
        return
    ok = ImageGeneration.generate(prompt)
    print("Image generation returned:", ok)


def run_whatsapp(prompt: str):
    whatsapp_controller = _lazy_import('whatsapp_controller')
    if whatsapp_controller is None or not hasattr(whatsapp_controller, 'WhatsAppController'):
        print("whatsapp_controller.WhatsAppController not available.")
        return
    print(whatsapp_controller.WhatsAppController(prompt))


def run_pc_control(prompt: str, use_new: bool = True):
    if use_new:
        module = _lazy_import('pc_control_new')
    else:
        module = _lazy_import('pc_control')
    if module is None or not hasattr(module, 'perform_action'):
        print("perform_action not available in selected pc_control module.")
        return
    print(module.perform_action(prompt, raw_text=prompt))


def run_llm(prompt: str):
    # lazy import ask_llm
    try:
        mod = _lazy_import('llm')
        ask_llm = getattr(mod, 'ask_llm', None) if mod else None
    except Exception:
        ask_llm = None
    if ask_llm is None:
        print("llm.ask_llm not available.")
        return
    import json
    resp = ask_llm(prompt)
    try:
        print(json.dumps(resp, ensure_ascii=True, indent=2))
    except Exception:
        print(str(resp))


def main():
    parser = argparse.ArgumentParser(description="Orchestrator for the backend services")
    sub = parser.add_subparsers(dest='cmd')

    sub.add_parser('assistant', help='Run the interactive assistant loop (SmartRouter)')

    p = sub.add_parser('smart', help='Run SmartRouter once')
    p.add_argument('prompt', nargs='+')

    p = sub.add_parser('chat', help='Run ChatBotAI once')
    p.add_argument('prompt', nargs='+')

    p = sub.add_parser('modal', help='Run Modal.FirstLayerDMM once')
    p.add_argument('prompt', nargs='+')

    p = sub.add_parser('realtime', help='Run RealtimeSearchEngine once')
    p.add_argument('prompt', nargs='+')

    p = sub.add_parser('automation', help='Run Automation_engine.Automation (async). Provide commands as separate args')
    p.add_argument('commands', nargs='+')

    p = sub.add_parser('tts', help='Send text to TTS')
    p.add_argument('text', nargs='+')

    p = sub.add_parser('image', help='Run ImageGeneration.generate once')
    p.add_argument('prompt', nargs='+')

    p = sub.add_parser('whatsapp', help='Run Whatsapp controller')
    p.add_argument('prompt', nargs='+')

    p = sub.add_parser('pc', help='Run pc_control.perform_action (use new by default)')
    p.add_argument('prompt', nargs='+')
    p.add_argument('--old', action='store_true', help='Use legacy pc_control.py instead of pc_control_new.py')

    p = sub.add_parser('llm', help='Run llm.ask_llm once')
    p.add_argument('prompt', nargs='+')

    args = parser.parse_args()

    if args.cmd == 'assistant':
        run_assistant_loop()
        return

    if args.cmd == 'smart':
        run_smart_once(' '.join(args.prompt))
        return

    if args.cmd == 'chat':
        run_chatbot_ai_once(' '.join(args.prompt))
        return

    if args.cmd == 'modal':
        run_modal(' '.join(args.prompt))
        return

    if args.cmd == 'realtime':
        run_realtime(' '.join(args.prompt))
        return

    if args.cmd == 'automation':
        asyncio.run(run_automation(args.commands))
        return

    if args.cmd == 'tts':
        run_tts(' '.join(args.text))
        return

    if args.cmd == 'image':
        run_image(' '.join(args.prompt))
        return

    if args.cmd == 'whatsapp':
        run_whatsapp(' '.join(args.prompt))
        return

    if args.cmd == 'pc':
        run_pc_control(' '.join(args.prompt), use_new=not args.old)
        return

    if args.cmd == 'llm':
        run_llm(' '.join(args.prompt))
        return

    parser.print_help()


if __name__ == '__main__':
    main()
