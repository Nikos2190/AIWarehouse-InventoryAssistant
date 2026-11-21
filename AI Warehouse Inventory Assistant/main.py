from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    APIStatusError
)
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

def get_quantity(units:int):
    result = []

    found = 0
    for product_id,item in storage_data.items():
        if item['Available quantity'] < units:
            result.append({'Product Id':product_id,item['Product name']:item['Available quantity']})
            found += 1
    if found == 0:
        return 'No product has less units available'
    else:
        return {'Found': len(result),
                'Products': result}

def shipping(units:int,ship_method:str):
    if units < 0:
        return ('Units cannot be of negative number')

    ship_method = ship_method.lower().strip()
    if ship_method not in('standard','express'):
        return'Please give an option between standard and express'
    else:
        return 3 * units if ship_method == 'standard' else 5 * units

tool = [{'type': 'function',
        'name': 'retrieve_data',
        'description': ('Retrieve name and quantity based on the exact product id'),
'parameters': {'type': 'object',
               'properties': {'product': {'type': 'string'}},
'required': ['product'],
'additionalProperties': False},
'strict': True},

{'type': 'function',
'name': 'get_quantity',
'description': (
    'Find all products whose available quantity is strictly less '
    'than the units threshold provided by the user.'
),
'parameters': {'type': 'object',
               'properties': {'units': {'type': 'integer'}},
'required': ['units'],
'additionalProperties': False},
'strict': True},

{'type': 'function',
     'name': 'shipping',
     'description': ('Calculate the cost of shipping based on the units and the type of shipping'),
 'parameters': {'type': 'object',
                'properties': {'units': {'type': 'integer'},'ship_method':{'type': 'string'}},
                'required': ['units', 'ship_method'],
                'additionalProperties': False},
 'strict': True}]

instruct = ("You are a warehouse inventory assistant. "
"For questions about a specific product or its availability, "
"always use the retrieve_data tool. "
"If the Product ID is missing, ask the user to provide it only if you need the retrieve data tool. "
"Do not use the tool for unrelated questions. "
"If you want to search based on quantity use the get_quantity tool. "
"Never invent inventory information. "
"If the user asks about low stock without specifying a numeric threshold, "
"ask them to provide the threshold before using any tool. "
"Do not assume a threshold. "
"Respond in plain text without Markdown formatting. "
"For every shipping cost calculation, always use the shipping tool. "
"Never calculate shipping costs yourself. "
"When the user requests shipping for all available units of a product, "
"first retrieve its current stock using retrieve_data, "
"then use the returned quantity as input to the shipping tool. ")

client = OpenAI()

try:
    response = client.responses.create(
        model = 'gpt-6-luna',
    reasoning={"effort": "none"},
    instructions= instruct,
    input = text,
    tools = tool )

    repeats = 0
    while repeats < 10:
        total_calls = []
        for item in response.output:
            if item.type == 'function_call':
                total_calls.append(item)


        if total_calls == []:
            print(response.output_text)
            break
        else:
            tool_output = []
            for tool_call in total_calls:
                print("Tool executed:", tool_call.name, tool_call.arguments)

                try:
                    arguments = json.loads(tool_call.arguments)

                except json.JSONDecodeError:
                    result = {"error": "Invalid JSON arguments"}

                else:
                    if tool_call.name == 'retrieve_data':
                        product = arguments['product']

                        if product.strip() == '':
                            result = {'found': False, 'error': 'Empty product id'}
                        else:
                            result = retrieve_data(product)

                    elif tool_call.name == 'get_quantity':
                        units = arguments['units']

                        if units < 0:
                            result = {'found': False, 'error': 'Negative number'}
                        else:
                            result = get_quantity(units)

                    elif tool_call.name == 'shipping':
                        units = arguments['units']
                        ship_method = arguments['ship_method']
                        result = shipping(units, ship_method)

                    else:
                        raise ValueError('Unsupported tool')

                tool_output.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(result)
                })

            second_response = client.responses.create(
            model="gpt-6-luna",
            reasoning={"effort": "none"},
            instructions= instruct,
            previous_response_id = response.id,
            tools = tool,
            input=tool_output)


            response = second_response
            repeats += 1

    if repeats == 10:
        if response.output_text and not any(
                item.type == "function_call" for item in response.output
        ):
            print(response.output_text)
        else:
            print("Maximum tool-calling iterations reached. Request not completed.")


except APITimeoutError :
    print("The OpenAI API request timed out. Please try again later.")
except APIConnectionError:
    print("Connection to OpenAI failed.")
except RateLimitError:
    print("OpenAI API rate limit exceeded. Please try again later.")
except APIStatusError as e:
    print(f"OpenAI API request failed with HTTP status {e.status_code}.")










































































