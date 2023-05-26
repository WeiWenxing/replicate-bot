import logging

import replicate
from replicate.client import Client


def high_op(url_path, token="abc123"):
    try:
        client = Client(api_token=token)
        output = client.run(
            "nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b",
            input={"image": url_path, "face_enhance": True, "scale": 2},
        )
        success = True
    except replicate.exceptions.ReplicateError as e:
        success = False
        output = str(e)
    except:
        success = False
        output = r'please input your replicate token as /token <apitoken>, you should sign up and get API token: https://replicate.com/account/api-tokens'

    logging.info(output)
    return success, output


def nude_op(token, image, mask, prompt, negative_prompt, num_outputs=1, num_inference_steps=20):
    try:
        client = Client(api_token=token)
        output = client.run(
            "stability-ai/stable-diffusion-inpainting:c28b92a7ecd66eee4aefcd8a94eb9e7f6c3805d5f06038165407fb5cb355ba67",
            input={"image": image,
                   "mask":open(mask, "rb"),
                   "prompt": prompt,
                   "negative_prompt": negative_prompt,
                    "num_outputs": num_outputs,
                   "num_inference_steps": num_inference_steps,
                   },
        )
        success = True
        token_is_good = True
    except replicate.exceptions.ReplicateError as e:
        success = False
        token_is_good = False
        output = str(e)
    except Exception as e:
        success = False
        token_is_good = True
        output = r'please input your replicate token as /token <apitoken>, you should sign up and get API token: https://replicate.com/account/api-tokens'
        output = str(e)

    logging.info(output)
    return success, token_is_good, output
