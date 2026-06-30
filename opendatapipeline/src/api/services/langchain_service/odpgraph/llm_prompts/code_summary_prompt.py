
def get_code_summary_prompt(code):
    prompt = f"""
    Explain the following code in a simple and concise summary. Focus on what actions were performed, such as whether a dataframe was updated, created, or retrieved. Specifically mention the alias name of the dataframe and what operation was done on it. Avoid referencing any specific library like DataframeInformation, and instead, describe the actions as they would naturally occur. 
    Example:
    Input: '<code> df = DataframeInformation.get(alias="students") df = df[['firstname'] + [col for col in df.columns if col != 'firstname']] DataframeInformation.update(alias="students", dataframe=df) </code>'
    Output:'- The dataframe named 'students' was retrieved.
    - The 'firstname' column was moved to the first position.
    - The dataframe was updated.'

    Always use past tense to summarize as this code was already applied in users dataframe and we just explaining the result. Do not make any assumptions instead just summarize the actions performed in each line.
    Here's the user Code to summarize :{code}"""
    return prompt