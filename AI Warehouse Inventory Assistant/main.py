
"""
EXERCISE 1 — AI Warehouse Inventory Assistant

OBJECTIVE
Build a Python application using OpenAI Function Calling
to answer natural-language inventory questions.

REQUIREMENTS

1. Create a dictionary containing 4 products with:
   - Product ID
   - Product name
   - Available quantity

2. Implement a function that retrieves product information.

3. Connect this function to the OpenAI Responses API
   through Function Calling.

4. Allow users to ask inventory questions in natural language.

5. Execute the requested function and return its result
   to the model for the final response.

6. Handle unknown products and invalid requests.

ACCEPTANCE TESTS

- Existing product: Return the correct stock quantity.
- Zero stock: Report that the product is unavailable.
- Unknown product: Return a clear not-found response.
- Function Calling: Complete the full execution cycle.

CONSTRAINTS
- Python and OpenAI Responses API
- One function tool
- No FastAPI or databases
- No agent frameworks
"""

from openai import OpenAI
import json

storage_data = {'PID-1':{
                'Product name': 'Headset',
                'Available quantity': 2},
'PID-2': {'Product name': 'Controller',
                'Available quantity': 2},
'PID-3': {'Product name': 'Soundbar',
                'Available quantity': 0},
'PID-4': {'Product name': 'Deck',
                'Available quantity': 2}}

text = input('Give a question: ')


def retrieve_data(product:str) :

    product = product.strip().upper()
    if '-' not in product:
       product = product.replace('PID','PID-')
    product_data = storage_data.get(product)

    if product_data is None:
        result = 'Product not found'
    else:
        result = {'Found':True,
                  'Product Id': product,
                  **product_data}
    return result


tool = {'type': 'function',
        'name': 'retrieve_data',
        'description': ('Retrieve name and quantity based on the exact product id'),
'parameters': {'type': 'object',
               'properties': {'product': {'type': 'string'}},
'required': ['product'],
'additionalProperties': False},
'strict': True}

client = OpenAI()

response = client.responses.create(
    model = 'gpt-6-luna',
reasoning={"effort": "none"},
instructions=(
    "You are a warehouse inventory assistant. "
    "For questions about a specific product or its availability, "
    "always use the retrieve_data tool. "
    "If the Product ID is missing, ask the user to provide it. "
    "Do not use the tool for unrelated questions. "
    "Never invent inventory information. "
    "Respond in plain text without Markdown formatting."
),
input = text,
tools = [tool],
parallel_tool_calls=False )

tool_call = None
for item in response.output:
    if item.type == 'function_call':
        tool_call = item
        break

if tool_call is None:
    print(response.output_text)
else:
    if tool_call.name != 'retrieve_data':
        raise ValueError('Unsupported tool')

    arguments = json.loads(tool_call.arguments)
    product = arguments['product']


    if product.strip() == '':
        result = {'found': False, 'error': 'Empty product id'}
    else:
        result = retrieve_data(product)


    tool_output = {
    "type": "function_call_output",
    "call_id": tool_call.call_id,
    "output": json.dumps(result)}

    second_response = client.responses.create(
    model="gpt-6-luna",
    reasoning={"effort": "none"},
    instructions="Respond in plain text without Markdown formatting.",
    previous_response_id = response.id,
    input=[tool_output])

    if second_response.output_text:
        print(second_response.output_text)
    else:
        print("The model did not yet return a final text answer.")








































































