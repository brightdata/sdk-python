import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brightdata import bdclient

client = bdclient()

# Basic extraction
result = client.extract("Extract news headlines from CNN.com")
print(result)

# Using URL parameter with structured output
schema = {
    "type": "object",
    "properties": {
        "headlines": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["headlines"],
    "additionalProperties": False
}

result = client.extract(
    query="Extract main headlines",
    url="https://cnn.com",
    output_scheme=schema
)
print(result)