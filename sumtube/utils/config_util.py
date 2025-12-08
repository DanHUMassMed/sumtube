import os
import json

# Default constants
DEFAULTS = {
    'model_name': 'gpt-oss:20b',
    'temperature': 0.0,
    'num_cxt': 32 * 1024,
    'raw_text_chunk_size': 32 * 1024,
    'text_chunk_overlay_size': 100,
}

CONFIG_PATH = os.path.join(os.environ.get('HOME', '.'), '.config', 'sumtube')
CONFIG_JSON = os.path.join(CONFIG_PATH, 'config.json')

def get_config_path():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    return CONFIG_PATH

def get_config_json():
    """Load defaults from config file if it exists, otherwise use constants."""
    if os.path.exists(CONFIG_JSON):
        try:
            with open(CONFIG_JSON, 'r') as f:
                file_defaults = json.load(f)
            defaults = {**DEFAULTS, **file_defaults}  # file overrides constants
            return defaults
        except Exception as e:
            print(f"Warning: Could not read config file, using constants. Error: {e}")
    return DEFAULTS.copy()


def get_input(prompt, default, cast_type):
    """Prompt user until a valid input is entered. Supports 'k' for multiplication by 1024."""
    while True:
        user_input = input(f"{prompt} [{default}]: ").strip()
        if not user_input:
            return default
        try:
            # Handle 'k' notation for integers
            if isinstance(default, int) and user_input.lower().endswith('k'):
                num_part = int(user_input[:-1])
                return num_part * 1024
            return cast_type(user_input)
        except ValueError:
            print("Invalid input. Please try again.")

def interactive_set_config():
    defaults = get_config_json()
    print("Enter configuration parameters (press Enter to keep default values):\n")

    config_params = {}
    config_params['model_name'] = input(f"Model name [{defaults['model_name']}]: ").strip() or defaults['model_name']
    config_params['temperature'] = get_input("Temperature", defaults['temperature'], float)
    config_params['num_cxt'] = get_input("Number of context tokens", defaults['num_cxt'], int)
    config_params['raw_text_chunk_size'] = get_input("Raw text chunk size", defaults['raw_text_chunk_size'], int)
    config_params['text_chunk_overlay_size'] = get_input("Text chunk overlay size", defaults['text_chunk_overlay_size'], int)

    config_json = get_config_json()

    # Write final config to file
    with open(config_json, 'w') as f:
        json.dump(config_params, f, indent=4)

    print("\nFinal configuration saved to config.json:")
    for key, value in config_params.items():
        print(f"{key}: {value}")

def print_config():
    config = get_config_json()
    print("\nCurrent configuration:")
    for key, value in config.items():
        print(f"   {key}: {value}")

