from config import OPENAI_API_KEY
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
from tenacity import retry, wait_random_exponential, wait_fixed, stop_after_attempt


class GPTProxy:
    def __init__(self, model="gpt-3.5-turbo"):
        
        self.model = model

    @retry(wait=wait_fixed(21), stop=stop_after_attempt(10))
    def ask(self, message):
        try:
            completion = client.chat.completions.create(model=self.model,
            messages=[
                {"role": "user", "content": message}
            ])

            return completion.choices[0].message.content
        except Exception as e:
            print(e)
            raise e


if __name__ == "__main__":
    proxy = GPTProxy()
    while True:
        print("\nType your question:")
        question = input()
        answer = proxy.ask(question)
        print(answer)
