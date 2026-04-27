#!/bin/bash
# start-local-copilot.sh

(
  export COPILOT_PROVIDER=openai
  export COPILOT_OPENAI_BASE_URL="http://192.168.1.8:11434/v1"
  # export COPILOT_MODEL="qwen2.5-coder:14b"
  export COPILOT_MODEL="qwen3-coder-next:q4_K_M"
  export COPILOT_OFFLINE=true
  # export COPILOT_PROVIDER_WIRE_API="responses"
  export COPILOT_PROVIDER_WIRE_API="completions"
  export COPILOT_PROVIDER_BASE_URL="http://192.168.1.8"

  copilot --allow-all
)

# After the parentheses, the variables are GONE.
# You can check by running 'echo $COPILOT_MODEL' here—it will be empty.