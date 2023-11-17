

# vand-python

Vand is a simple Python package that makes it easy to leverage [function calls](https://platform.openai.com/docs/guides/gpt/function-calling) with OpenAI's models.  This works with any public API (called ToolPacks) found on [vand.io](https://vand.io) which inculdes most ChatGPT Plugins.

# Installation
 `pip install --upgrade https://github.com/vand-io/vand-python/tarball/master`
 
To uninstall

 `pip uninstall vand-python`
# Quick Demo
Make sure you have your OpenAI key set (export OPENAI_API_KEY='sk-...')

`python simple_tool_usage_example.py `

```
system: Answer user questions as best you can.  Find and use a tool to increase accuracy or add capabilites if needed.

user: What's the weather like in Honolulu today?

assistant: {'name': 'getWeatherNow', 'arguments': '{\n  "city": "Honolulu",\n  "country": "US"\n}'}

function (getWeatherNow): {
  "base": "stations",
  "clouds": {
    "all": 20
  },
  "cod": 200,
  "coord": {
    "lat": 21.3045,
    "lon": -157.8557
  },
  "dt": 1699041629,
  "id": 5856195,
  "main": {
    "feels_like": 302.93,
    "humidity": 69,
    "pressure": 1017,
    "temp": 300.74,
    "temp_max": 302.1,
    "temp_min": 299.57
  },
  "name": "Honolulu",
  "sys": {
    "country": "US",
    "id": 47742,
    "sunrise": 1699029323,
    "sunset": 1699070070,
    "type": 2
  },
  "timezone": -36000,
  "visibility": 10000,
  "weather": [
    {
      "description": "few clouds",
      "icon": "02d",
      "id": 801,
      "main": "Clouds"
    }
  ],
  "wind": {
    "deg": 50,
    "speed": 2.06
  }
}

assistant: The weather in Honolulu today is partly cloudy with a temperature of approximately 300.74 Kelvin (27.59 degrees Celsius). The humidity is around 69% and there's a light breeze from the east-northeast with a speed of 2.06 m/s.

```

# Using vand-python in your own apps

1. Import vand-python

` from vand.vand_utils import VandBasicAPITool `

2. Fetch the tool you want.  Note you can find the ID (e.g. "vand-.*") by searching for tools at [Vand.io](https://vand.io/toolpacks).  Just swap out the Vand ID for the tool you want to use.  In this example we'll be using a [weather tool](https://www.vand.io/toolpack/vand-6657ac86-b112-4776-a5cc-fae3aa80ba56) to get the current conditions in Honolulu.

` get_weather = VandBasicAPITool.get_toolpack("vand-6657ac86-b112-4776-a5cc-fae3aa80ba56") `

3. Write the ChatCompleteion call
```py3
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "What's the weather like in Honolulu?"}],
    functions=get_weather.functions,
    function_call="auto",)

assistant_message = completion.choices[0].message.content
```
Which should return a response similar to below in this example.

```
{
    "id": "chatcmpl-7GCF1pk8pmsgtLZNyTC9LNqT4y5k8",
    "object": "chat.completion",
    "created": 1698470877,
    "model": "gpt-3.5-turbo-0613",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": null,
                "function_call": {
                    "name": "getWeatherNow",
                    "arguments": "{\n  \"city\": \"Honolulu\",\n  \"state\": \"HI\",\n  \"country\": \"US\"\n}"
                }
            },
            "finish_reason": "function_call"
        }
    ],
    "usage": {
        "prompt_tokens": 331,
        "completion_tokens": 31,
        "total_tokens": 362
    }
}
```

4. Execute the function call from the model in the chat completion response by calling `VandBasicAPITool` with the function call message.
   
```py3
if assistant_message.get("function_call"):
    toolMessage, toolPack = VandBasicAPITool.execute_function_call(assistant_message)
```

5. toolMessage is the result of the API call.  toolPack is any additional tool that the function_call might have returned to be (optionally) passed to the model.

In this case toolMessage contained the weather in Honolulu:

```py3

print(f"tool message: {toolMessage}")

tool message: {
  "base": "stations",
  "clouds": {
    "all": 0
  },
  "cod": 200,
  "coord": {
    "lat": 34.0537,
    "lon": -118.2428
  },
  "dt": 1698870346,
  "id": 5368361,
  "main": {
    "feels_like": 300.63,
    "humidity": 11,
    "pressure": 1017,
    "temp": 302.31,
    "temp_max": 304.59,
    "temp_min": 299.77
  },
  "name": "Los Angeles",
  "sys": {
    "country": "US",
    "id": 3694,
    "sunrise": 1698847942,
    "sunset": 1698886837,
    "type": 1
  },
  "timezone": -25200,
  "visibility": 10000,
  "weather": [
    {
      "description": "clear sky",
      "icon": "01d",
      "id": 800,
      "main": "Clear"
    }
  ],
  "wind": {
    "deg": 130,
    "speed": 3.6
  }
}
```

6. You then might want to pass the toolMessage and chat history back to the model.

```py3

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "What's the weather like in Honolulu?"}, 
               "role": "function", "name": assistant_message["function_call"]["name"], "content": toolMessage}],
    )

assistant_message = completion.choices[0].message.content
```

Which should return a reponse similar to:

```
assistant: The weather in Honolulu today is partly cloudy with a temperature of approximately 300.74 Kelvin (27.59 degrees Celsius). The humidity is around 69% and there's a light breeze from the east-northeast with a speed of 2.06 m/s.
```

