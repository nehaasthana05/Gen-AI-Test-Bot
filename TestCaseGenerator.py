import openai

client = openai.OpenAI(api_key="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")

# Generate test cases
def write_tests(code: str, assertions: list, model: str='3.5') -> str:
    if (model not in ['3.5', '4']) or (type(assertions) != list) or (type(code) != str):
        print("Please note that the correct use case is write_tests(code: str, assertions: [str], model: str [\"3.5\" or \"4\"])")
        raise ValueError

    astns = ""
    for astn in assertions:
        astns += astn['assertion'] + "\n"
    
    if model == '3.5':
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful bot that writes assertions for Python programs"},
                {"role": "user", "content": "Here is some python code.\n\n " + code  + "\n\nHere ends the code.\n \
                Here are some assertions for the code.\n\n" + astns + "\n\nHere end the assertions + \
                Now, expand the list of assertions for the code according to these requirements:\n \
                For each function that I gave you assertions for, generate and include new assertions. \n \
                Provide assertions to cover a wide range of scenerios. \n \
                Include all of the assertions I gave you with the assertions you generate.\n \
                IMPORTANT: THE LIST YOU GIVE ME MUST INCLUDE ALL ASSERTIONS I GAVE YOU. YOU ARE NOT CREATING A NEW LIST FROM SCRATCH, BUT RATHER EXPANDING UPON MY LIST. \n \
                Maintain the formatting of the assertions I gave you, and apply it to the new assertions. \n \
                Don't include any explanations in your responses."},
            ]
        )
    
    else:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful bot that writes test cases for Python programs"},
                {"role": "user", "content": "Here is some python code.\n\n " + code  + "\n\nHere ends the code.\n \
                Here are some assertions for the code.\n\n" + astns + "\n\nHere end the assertions + \
                Now, expand the list of assertions for the code according to these requirements:\n \
                For each function that I gave you assertions for, generate and include new assertions. \n \
                Provide assertions to cover a wide range of scenerios. \n \
                Include all of the assertions I gave you with the assertions you generate.\n \
                IMPORTANT: THE LIST YOU GIVE ME MUST INCLUDE ALL ASSERTIONS I GAVE YOU. YOU ARE NOT CREATING A NEW LIST FROM SCRATCH, BUT RATHER EXPANDING UPON MY LIST. \n \
                Maintain the formatting of the assertions I gave you, and apply it to the new assertions. \n \
                Don't include any explanations in your responses."},
            ]
        )

    return completion.choices[0].message.content

def write_updated_tests(code: str, assertions: list, diff: str, model: str='3.5') -> str:
    if (model not in ['3.5', '4']) or (type(assertions) != list) or (type(code) != str) or (type(diff) != str):
        print("Please note that the correct use case is write_tests(code: str, assertions: [str], diff: str, model: str [\"3.5\" or \"4\"])")
        raise ValueError

    astns = ""
    for astn in assertions:
        astns += astn['assertion'] + "\n"
    
    if model == '3.5':
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful bot that edits assertions for Python programs"},
                {"role": "user", "content": "Here is some python code.\n\n " + code  + "\n\nHere ends the code.\n \
                Here is a diff file showing the lastest changes to the code.\n\n" + diff + "\n\nHere ends the diff file.\n \
                Here is a list of assertions for the code.\n\n" + astns + "\n\nHere end the assertions + \
                Now, edit the list of assertions I gave you according to the diff file. \
                That is, consider all changes made to the code that is shown in the diff file and edit, add, or remove assertions where applicable.\n \
                Maintain the formatting of the assertions I gave you, and apply it to the edited assertions. \n \
                Don't include any explanations in your responses."},
            ]
        )
    
    else:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful bot that edits assertions for Python programs"},
                {"role": "user", "content": "Here is some python code.\n\n " + code  + "\n\nHere ends the code.\n \
                Here is a diff file showing the lastest changes to the code.\n\n" + diff + "\n\nHere ends the diff file.\n \
                Here is a list of assertions for the code.\n\n" + astns + "\n\nHere end the assertions + \
                Now, edit the list of assertions I gave you according to the diff file. \
                That is, consider all changes made to the code that is shown in the diff file and edit, add, or remove assertions where applicable.\n \
                Maintain the formatting of the assertions I gave you, and apply it to the edited assertions. \n \
                Don't include any explanations in your responses."},
            ]
        )

    return completion.choices[0].message.content
