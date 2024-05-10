import openai
import re

# Initialize OpenAI client with your API key
client = openai.OpenAI(api_key='insert key here')

# Fine-tuned model ID
fine_tuned_id = "ft:gpt-3.5-turbo-0125:personal:ver:9IJpVmJQ"

class FormalVerificationSolver:

    
    def __init__(self):
        self.u_input = input("Please provide a program to formally verify: ")

        # Try to match the pattern with "???" at the end
        match = re.match(r"^\s*(.*?)\s*if\s*\((.*?)\)\s*{(.*?)}\s*else\s*{(.*?)}\s*(.*?)\s*\?\?\?", self.u_input, re.DOTALL)
        if match:
            self.pre_condition = match.group(1).strip()
            self.if_condition = match.group(2).strip()
            self.if_code = match.group(3).strip()
            self.else_code = match.group(4).strip()
            self.post_condition = match.group(5).strip()
        else:
            # Try to match the pattern with "???" at the beginning
            match = re.match(r"^\s*\?\?\?\s*if\s*\((.*?)\)\s*{(.*?)}\s*else\s*{(.*?)}\s*(.*)", self.u_input, re.DOTALL)
            if match:
                self.pre_condition = ""
                self.if_condition = match.group(1).strip()
                self.if_code = match.group(2).strip()
                self.else_code = match.group(3).strip()
                self.post_condition = match.group(4).strip()
            else:
                print("Invalid input format")
                return

    def solve(self):
        if self.post_condition == "":
            if_result = self.process_preblock(self.pre_condition, self.if_code)
            else_result = self.process_preblock(self.pre_condition, self.else_code)
            
            # Combine results with "or" condition
            combined_result = f"({if_result} ^ ({self.if_condition})) or ({else_result}) ^ !({self.if_condition})"
            print("Combined result:", combined_result)

        if self.pre_condition == "":
            if_result = self.process_postblock(self.pre_condition, self.if_code)
            else_result = self.process_postblock(self.pre_condition, self.else_code)
            # Combine results with "or" condition
            combined_result = f"({if_result} ^ ({self.if_condition})) or ({else_result}) ^ !({self.if_condition})"
            print("Combined result:", combined_result)


    def process_preblock(self, pre_condition, code):
        # Initialize pre_condition for the first statement
        current_pre_condition = pre_condition
        result = ""
        
        # Split code into individual statements
        statements = code.split(";")
        
        for statement in statements:
            # Send pre_condition and current statement through OpenAI API
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant to solve formal program verification."},
                    {"role": "user", "content": f"{current_pre_condition} {statement}"}
                ],
                model=fine_tuned_id,
                max_tokens=500
            )
            # Extract completion text
            response_text = completion.choices[0].message.content
            # Set current_pre_condition to response for next iteration
            current_pre_condition = response_text
            # Append response to result
            result += response_text + " "

        return result.strip()
    

    def process_postblock(self, post_condition, code):
    # Initialize post_condition for the last statement
        current_post_condition = post_condition
        result = ""

        # Reverse the list of statements to process them in reverse order
        statements = code.split(";")[::-1]

        for statement in statements:
            # Send current statement and post_condition through OpenAI API
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant to solve formal program verification."},
                    {"role": "user", "content": f"{statement} {current_post_condition}"}
                ],
                model=fine_tuned_id,
                max_tokens=500
            )
            # Extract completion text
            response_text = completion.choices[0].message.content
            # Set current_post_condition to response for next iteration
            current_post_condition = response_text
            # Append response to result
            result = response_text + "; " + result  # Append in reverse order

        return result.strip()



if __name__ == "__main__":
    solver = FormalVerificationSolver()
    solver.solve()
