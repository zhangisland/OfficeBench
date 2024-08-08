from http import HTTPStatus
from openai import OpenAI
import time
import numpy as np
import google.generativeai as genai
from loguru import logger
import dashscope
import random


class ChatGPT:
    def __init__(self, model_name, key, system_message=None):
        self.model_name = model_name
        self.key = key
        self.system_message = system_message
        
        self.client = OpenAI(
            api_key=key
        )
                

    def get_model_options(
        self,
        temperature=0,
        per_example_max_decode_steps=1024,
        per_example_top_p=1,
        n_sample=1,
    ):
        return dict(
            temperature=temperature,
            n=n_sample,
            top_p=per_example_top_p,
            max_tokens=per_example_max_decode_steps,
        )

    def generate_plus_with_score(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()
        messages = [
            {
                "role": "system",
                "content": (
                    "I will give you some examples, you need to follow the examples and complete the text, and no other content."
                    if self.system_message is None
                    else self.system_message
                ),
            },
            {"role": "user", "content": prompt},
        ]
        gpt_responses = None
        retry_num = 0
        retry_limit = 2
        error = None
        while gpt_responses is None:
            try:
                gpt_responses = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    stop=end_str,
                    **options,
                )
                error = None
            except Exception as e:
                logger.error(str(e))
                error = str(e)
                if "This model's maximum context length is" in str(e):
                    logger.error(e, flush=True)
                    gpt_responses = {
                        "choices": [{"message": {"content": "PLACEHOLDER"}}]
                    }
                elif retry_num > retry_limit:
                    error = "too many retry times"
                    gpt_responses = {
                        "choices": [{"message": {"content": "PLACEHOLDER"}}]
                    }
                else:
                    time.sleep(60)
                retry_num += 1
        if error:
            raise Exception(error)
        results = []
        for i, res in enumerate(gpt_responses["choices"]):
            text = res["message"]["content"]
            fake_conf = (len(gpt_responses["choices"]) - i) / len(
                gpt_responses["choices"]
            )
            results.append((text, np.log(fake_conf)))

        return results

    def generate(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()
        options["n"] = 1
        result = self.generate_plus_with_score(prompt, options, end_str)[0][0]
        return result


class Gemini:
    # gemini-1.0-pro
    # gemini-1.5-pro
    def __init__(self, model_name, key, system_message=None):
        self.model_name = model_name
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(model_name)
        self.system_message = system_message

    def generate(self, prompt):
        combined_prompt = (
            f"{self.system_message}\n\n{prompt}" if self.system_message else prompt
        )
        response = self.model.generate_content(
            combined_prompt,
            generation_config=genai.types.GenerationConfig(
                # Only one candidate for now.
                candidate_count=1,
                max_output_tokens=1024,
                temperature=1.0,
            ),
        )
        return response.text


class vLLM:
    def __init__(self, model_name, system_message=None):
        self.model_name = model_name
        self.system_message = system_message
        self.client = OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="token-abc123",
        )
    
    def get_model_options(
        self,
        temperature=0,
        per_example_max_decode_steps=512,
        per_example_top_p=1,
        n_sample=1,
    ):
        return dict(
            temperature=temperature,
            n=n_sample,
            top_p=per_example_top_p,
            max_tokens=per_example_max_decode_steps,
        )

    def generate(self, prompt):
        try:
            options = self.get_model_options()
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt},
                ],
                **options,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Generation Error: {e}")
            return "None"


class Qwen:
    def __init__(self, model_name, key, system_message=None):
        self.model_name = model_name
        self.key = key
        self.system_message = system_message
    
    def generate_model_options(self,
                               temperature=0.8,
                               seed=1234):
        # generate random seed
        seed = 1234 # random.randint(0, 1000000)
        logger.debug(f"Random seed: {seed}")
        return dict(
            temperature=temperature,
            seed=seed,
        )

    def generate(self, prompt, options=None):
        messages = [
            {
                "role": "system",
                "content": ("You are a helpful assistant." if self.system_message is None else self.system_message)
            },
            {"role": "user", "content": prompt},
        ]

        if options is None:
            options = self.generate_model_options()  # default options

        response = dashscope.Generation.call(
            model=self.model_name,
            api_key=self.key,
            messages=messages,
            result_format='message',
            **options,
        )
        if response.status_code == HTTPStatus.OK:
            result = response.output.choices[0].message.content

        else:
            logger.error(f'Request id: {response.request_id}, \
                           Status code: {response.status_code}, \
                           error code: {response.code}, \
                           error message: {response.message}')
            result = "Request failed. Please try again later."
        return result
