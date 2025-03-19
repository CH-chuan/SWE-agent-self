import tiktoken
import argparse
import yaml

def load_yaml(file_path):
    """Load and parse the YAML file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def main(config_path, model_name):
    # read example: "config/agent_configs/azure_example.yaml"
    config = load_yaml(config_path)

    agent_config = config.get('agent', {})
    templates_config = agent_config.get('templates', {})

    encoding = tiktoken.encoding_for_model(model_name)
    for key, value in templates_config.items():
        if "template" in key and isinstance(value, str):
            # token_counted = tiktoken.count_tokens(item)
            tokens = encoding.encode(value)
            token_counted = len(tokens)
            print(f"Prompt: {key} has {token_counted} tokens.")


    


if __name__ == '__main__':
    # read needed data, path to a config file for the agent using argparse
    
    # read the config file path from the command line
    parser = argparse.ArgumentParser(description='Token calculator')
    parser.add_argument('--config_path', type=str, help='path to the config file', default='config/agent_configs/azure_example.yaml')
    parser.add_argument('--model_name', type=str, help='model name', default='gpt-4o')
    args = parser.parse_args()

    main(args.config_path, args.model_name)