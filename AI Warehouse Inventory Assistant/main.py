
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


"""
PHASE 2 — MULTIPLE TOOL SELECTION

OBJECTIVE
Extend the existing Warehouse Inventory Assistant to support
multiple tools and intelligent tool selection.

BUSINESS SCENARIO
Warehouse employees need to identify products with low stock,
in addition to checking individual product availability.

FUNCTIONAL REQUIREMENTS

1. Preserve all existing functionality from Phase 1.

2. Add a new capability that identifies products whose
   available quantity is below a specified threshold.

3. Allow users to specify the threshold in natural language.

4. The assistant must select the appropriate tool based
   on the user's request.

5. Return accurate product information without inventing data.

6. Handle invalid thresholds and cases where no products match.

INPUTS
Natural-language inventory questions.

OUTPUTS
Clear answers containing the requested inventory information.

ACCEPTANCE TESTS

Test 1 — Individual Product
Question: "How many units of PID-2 are available?"
Expected: Return the correct quantity using the existing tool.

Test 2 — Low Stock
Question: "Which products have fewer than 2 units?"
Expected: Identify PID-3 (Soundbar).

Test 3 — No Matches
Question: "Which products have fewer than 0 units?"
Expected: No products match.

Test 4 — Missing Threshold
Question: "Which products are running low?"
Expected: Ask the user to specify a stock threshold.

Test 5 — Tool Selection
Expected: The assistant selects the appropriate tool
for each inventory request.

CONSTRAINTS
- Python and OpenAI Responses API.
- Two function tools in total.
- Reuse the existing inventory dictionary.
- No FastAPI, databases or agent frameworks.
- No multiple tool calls within a single user request.
"""


"""
PHASE 3 — MULTIPLE FUNCTION CALLS

PROJECT
AI Warehouse Inventory Assistant

OBJECTIVE
Extend the existing application to handle multiple
independent function calls within a single model response.

BUSINESS SCENARIO
Warehouse employees often need different inventory
information in a single request.

The assistant must retrieve all requested information
and provide one complete, accurate response.

FUNCTIONAL REQUIREMENTS

1. Preserve all functionality from Phases 1 and 2.

2. Support user requests that require more than one
   inventory operation.

3. Process every function call returned by the model,
   rather than handling only the first one.

4. Execute the appropriate Python function for each call.

5. Associate each function result with its corresponding
   function call.

6. Return all function results to the model.

7. Generate one final response addressing every part
   of the original user request.

8. Preserve existing validation and error handling.

INPUTS
Natural-language inventory questions containing
one or more independent requests.

OUTPUTS
A complete natural-language answer containing
all requested inventory information.

ACCEPTANCE TESTS

Test 1 — Multiple Operations
Question:
"How many units of PID-2 are available, and which
products have fewer than 2 units?"

Expected:
- Retrieve PID-2 availability.
- Identify products below the specified threshold.
- Include both results in the final answer.

Test 2 — Single Operation
Question:
"What is the availability of PID-4?"

Expected:
Process one function call correctly.

Test 3 — No Tool Required
Question:
"Hello!"

Expected:
Respond without executing inventory functions.

Test 4 — Independent Results
Question:
"Which products have fewer than 3 units, and
what is the name of PID-1?"

Expected:
Execute the required operations and return
both results accurately.

Test 5 — Invalid Product
Question:
"What is the availability of PID-99, and
which products have fewer than 2 units?"

Expected:
Report the unknown product while still returning
the valid low-stock information.

CONSTRAINTS
- Python and OpenAI Responses API.
- Reuse the existing two tools.
- No additional inventory tools.
- No FastAPI, database or agent frameworks.
- No dependent or sequential tool execution chains.
- No implementation code is provided.
"""

"""
PHASE 4 — SEQUENTIAL TOOL CALLING

PROJECT
AI Warehouse Inventory Assistant

OBJECTIVE
Extend the existing application to support dependent function
calls across multiple model responses within a single user request.

BUSINESS SCENARIO
Warehouse employees need to determine how many additional units
must be ordered to reach a desired stock level.

The assistant must use actual inventory information rather than
assume current stock quantities.

FUNCTIONAL REQUIREMENTS

1. Preserve all functionality from Phases 1, 2, and 3.

2. Introduce a new capability for calculating replenishment quantities.

3. Allow users to specify a product and a desired stock level
   in natural language.

4. Retrieve the product's current inventory information before
   calculating replenishment.

5. Use the retrieved quantity to determine how many additional
   units are required.

6. Support dependent tool operations across successive model responses.

7. Continue processing until the requested operation is complete.

8. Return one accurate final answer.

9. Never suggest ordering a negative quantity.

INPUTS
Natural-language inventory and replenishment requests.

OUTPUTS
A clear response containing:
- Product information
- Current stock
- Desired stock level
- Required replenishment quantity

ACCEPTANCE TESTS

Test 1 — Standard Replenishment
Question:
"How many units must we order to bring PID-2 up to 8 units?"

Expected:
- Current stock: 2
- Target stock: 8
- Required replenishment: 6

Test 2 — Out-of-Stock Product
Question:
"How many units are needed to bring PID-3 up to 5?"

Expected:
- Current stock: 0
- Required replenishment: 5

Test 3 — Sufficient Existing Stock
Question:
"How many units should we order to bring PID-4 up to 1?"

Expected:
- Current stock: 2
- Required replenishment: 0

Test 4 — Unknown Product
Question:
"How many units should we order for PID-99 to reach 10?"

Expected:
Report that the product does not exist.
Do not calculate a replenishment quantity.

Test 5 — Invalid Target
Question:
"Bring PID-1 to -3 units."

Expected:
Reject the invalid target.

Test 6 — Existing Functionality
Question:
"How many units of PID-2 are available, and which products
have fewer than 2 units?"

Expected:
Preserve the multiple-function-call behavior from Phase 3.

CONSTRAINTS

- Python and OpenAI Responses API.
- Preserve the existing inventory data.
- No FastAPI, databases, or agent frameworks.
- No hardcoded replenishment answers.
- Dependent operations must use actual results from preceding operations.
- Implementation and architecture decisions are yours.
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
"Respond in plain text without Markdown formatting."
"For every shipping cost calculation, always use the shipping tool. "
"Never calculate shipping costs yourself. "
"When the user requests shipping for all available units of a product, "
"first retrieve its current stock using retrieve_data, "
"then use the returned quantity as input to the shipping tool. ")

client = OpenAI()

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
        for tool_call in total_calls :
            print("Tool executed:", tool_call.name, tool_call.arguments)

            if tool_call.name == 'retrieve_data':
                arguments = json.loads(tool_call.arguments)
                product = arguments['product']

                if product.strip() == '':
                    result = {'found': False, 'error': 'Empty product id'}
                else:
                    result = retrieve_data(product)

            elif tool_call.name == 'get_quantity':
                arguments = json.loads(tool_call.arguments)
                units = arguments['units']

                if units < 0 :
                    result = {'found': False, 'error': 'Negative number'}
                else:
                    result = get_quantity(units)

            elif tool_call.name == 'shipping':
                arguments = json.loads(tool_call.arguments)
                units = arguments['units']
                ship_method = arguments['ship_method']
                result = shipping(units,ship_method)

            else:
                raise ValueError('Unsupported tool')

            tool_output.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": json.dumps(result)})



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








































































