import json
import time
import random
import config

# --- 第一套：Google 原生依赖 ---
try:
    from google import genai
    from google.genai import types as google_types
except ImportError:
    genai, google_types = None, None

# --- 第二套：OpenAI 兼容依赖 ---
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def clean_json_string(raw_text: str) -> str:
    """处理第三方代理返回的带有 markdown 标记的 JSON"""
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0]
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0]
    return raw_text.strip()

def _call_google_native(prompt: str, model_name: str, schema=None, temperature=0.2):
    if not genai: raise RuntimeError("缺少 google-genai 库")
    if not config.GOOGLE_API_KEY: raise ValueError("未配置 GOOGLE_API_KEY")
    
    client = genai.Client(api_key=config.GOOGLE_API_KEY)
    config_args = {"temperature": temperature}
    if schema:
        config_args["response_mime_type"] = "application/json"
        config_args["response_schema"] = schema
        
    conf = google_types.GenerateContentConfig(**config_args)
    return client.models.generate_content(model=model_name, contents=prompt, config=conf).text.strip()

def _call_openai_compatible(prompt: str, model_name: str, schema=None, temperature=0.2):
    if not OpenAI: raise RuntimeError("缺少 openai 库")
    if not config.OPENAI_API_KEY: raise ValueError("未配置 OPENAI_API_KEY")
    
    client = OpenAI(api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL)
    messages = []
    if schema:
        schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
        system_instruction = (
            f"You are an astrophysics assistant. You MUST return ONLY valid JSON. "
            f"Do NOT include markdown formatting like ```json. "
            f"Your JSON must strictly match this schema: {schema_json}"
        )
        messages.append({"role": "system", "content": system_instruction})
        
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"} if schema else {"type": "text"}
    )
    raw_text = response.choices[0].message.content
    return clean_json_string(raw_text) if schema else raw_text.strip()

def generate_content_with_retry(model, contents, schema=None, temperature=0.2, max_retries=4, base_delay=5, provider=None):
    # 如果调用时没有特别指定，就使用配置中的默认值
    current_provider = provider if provider else config.API_PROVIDER

    for attempt in range(max_retries):
        try:
            if current_provider == "openai":
                result = _call_openai_compatible(prompt=contents, model_name=model, schema=schema, temperature=temperature)
            else:
                result = _call_google_native(prompt=contents, model_name=model, schema=schema, temperature=temperature)
            
            if schema:
                parsed_json = json.loads(result)
                if isinstance(parsed_json, str): 
                    parsed_json = json.loads(parsed_json)
                return parsed_json
            return result
            
        except Exception as e:
            error_msg = str(e).upper()
            if any(err in error_msg for err in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "JSONDECODEERROR"]):
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt) + random.uniform(1, 3)
                    print(f"  [Warning] API波动 ({current_provider}) 等待 {wait_time:.1f}s 后重试 {attempt + 1}/{max_retries-1}...")
                    time.sleep(wait_time)
                    continue
            # 重试耗尽，直接抛出错误，交给 main.py 处理降级
            raise e