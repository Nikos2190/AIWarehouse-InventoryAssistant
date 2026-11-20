# AI Warehouse Inventory Assistant

A Python command-line application that uses the OpenAI Responses API and function calling to answer warehouse inventory questions in natural language.

The project demonstrates **tool selection**, **multiple independent function calls**, and **sequential tool calling**, where a later tool request depends on information retrieved earlier.

## Features

- Look up a product's name and available quantity by product ID.
- Find products with stock strictly below a user-specified threshold.
- Calculate shipping costs for a specified number of units using **Standard** or **Express** shipping.
- Look up a product's available stock before calculating the cost of shipping **all available units**.
- Handle multiple independent tool calls in a single model response.
- Process further tool calls across consecutive model responses.
- Reject unsupported shipping methods, negative quantities, and unknown product IDs.
- Stop after at most **10 tool-processing cycles** to prevent unbounded execution.

## Tech Stack

- **Python**
- **OpenAI Python SDK**
- **OpenAI Responses API** with function calling
- **JSON Schema** for tool definitions
- **In-memory Python dictionary** for inventory data

No database, web framework, or agent framework is used.

## Available Tools

| Tool | Purpose |
| --- | --- |
| `retrieve_data(product)` | Returns the name and available quantity of a specific product. |
| `get_quantity(units)` | Finds products with available quantity strictly below the specified threshold. |
| `shipping(units, ship_method)` | Calculates the shipping cost for a quantity using Standard or Express service. |

### Shipping rules

| Method | Rate per unit |
| --- | ---: |
| Standard | 3 |
| Express | 5 |

**Note:** Rates are illustrative values configured in the Python function. No currency is defined by the application, and these are not live carrier quotations.

## How Function Calling Works

The model selects a tool, but **Python executes the actual function**. Tool results are returned to the model using the associated `call_id`.

For independent requests, the application can execute multiple tool calls from the same model response and return their outputs together.

For dependent requests, the application can continue across responses:

```text
User: "How much does it cost to ship all available units of PID-2 via express?"

Model requests: retrieve_data(product="PID-2")
    -> Python returns 2 available units

Model requests: shipping(units=2, ship_method="express")
    -> Python returns 10

Model returns a final natural-language answer.
```

The application uses `previous_response_id` to connect successive Responses API requests. The processing loop exits when no further function calls are requested or when its iteration limit is reached.

## Setup and Run

1. Install Python and the OpenAI SDK:

   ```bash
   pip install openai
   ```

2. Configure your `OPENAI_API_KEY` environment variable, then run:

   ```bash
   python main.py
   ```

Enter one natural-language question when prompted with `Give a question:`. The application prints tool-call diagnostics and the model's answer.

> **API usage:** Running the application sends requests to the OpenAI API and may incur usage charges. Multi-step questions can require several API requests. The API key must be supplied through the environment, not committed to the repository.

## Example Requests

| Request | Expected behavior |
| --- | --- |
| `How many units of PID-4 are available?` | Retrieve the stock of PID-4. |
| `Which products have fewer than 2 units?` | Identify products below the threshold. |
| `How many units of PID-2 are available, and which products have fewer than 2 units?` | Use multiple independent tool calls. |
| `How much does it cost to ship 4 units via standard?` | Calculate a shipping cost using only the shipping tool. |
| `How much does it cost to ship all available units of PID-2 via express?` | Retrieve stock, then calculate shipping in a later tool call. |
| `How much does it cost to ship all available units of PID-99 via express?` | Report that the product cannot be found; do not calculate a shipping cost. |

## Implementation Progress

- **Phase 1 — Single Tool Calling:** Retrieve information about a specific product.
- **Phase 2 — Multiple Tool Selection:** Select between stock lookup and threshold search.
- **Phase 3 — Multiple Function Calls:** Process multiple independent tool calls from one model response.
- **Phase 4 — Sequential Tool Calling:** Process dependent tool calls across model responses, including shipping-cost calculation and bounded loop execution.

## Current Limitations

- Inventory is predefined in an in-memory dictionary; it is not persisted or updated.
- Shipping rates are fixed demonstration values, not real-world carrier prices.
- The application handles one user question per execution.
- Tool use and the wording of the final answer depend on the model; no automated test suite is included.
- The project is a learning and portfolio demonstration, **not a production warehouse management system**.
