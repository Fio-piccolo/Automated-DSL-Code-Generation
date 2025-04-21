import os
import glob
from openai import OpenAI


ARK_API_KEY = "sk-sR8RiK6YYrtk8Rss1b29047069804d108211285c7a25356c"
model_name="gpt-4"

cnt = 0
client = OpenAI(
    # base_url="https://ark.cn-beijing.volces.com/api/v3",
    base_url="https://api.yesapikey.com/v1",
    api_key=ARK_API_KEY
)

# BPMN_DIR = "./BPMN for Research NEW"
BPMN_DIR = "./OCL"
# PROMPT_TEMPLATE = "请根据以下BPMN代码，分析其业务逻辑。生成自然语言的需求描述，只给出答案，要求必须用英文回答，即自然语言文本内容，不需要格式，回答开头为：需求如下：\n{}"
PROMPT_TEMPLATE = "请根据以下OCL代码，分析其业务逻辑。生成自然语言的需求描述，只给出答案，要求必须用英文回答，即自然语言文本内容，不需要格式，回答开头为：需求如下：\n{}"


def process_bpmn_file(file_path):
    """处理单个BPMN文件"""
    global cnt
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            bpmn_content = f.read()

        prompt = PROMPT_TEMPLATE.format(bpmn_content)
        messages = [
            {"role": "system", "content": "你是OCL代码分析专家，擅长将OCL代码逆向转换为自然语言的需求描述，假设已经有了代码，请问生成这个代码所需的自然语言是怎样描述的呢？要求必须用英文回答"},
            # {"role": "system", "content": "你是BPMN代码分析专家，擅长将BPMN代码逆向转换为自然语言的需求描述，假设已经有了代码，请问生成这个代码所需的自然语言是怎样描述的呢？要求必须用英文回答"},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=False
        )

        analysis_result = response.choices[0].message.content.strip()
        print(analysis_result)
        txt_path = os.path.splitext(file_path)[0] + ".txt"

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(analysis_result)

        print(f"成功处理文件：{file_path} -> {txt_path}")
        cnt += 1
        print("已处理文件数量 ： ", cnt)

    except Exception as e:
        print(f"处理文件失败 {file_path}: {str(e)}")


def main():
    # 改模型名、提示、语言后缀名
    global cnt
    """递归遍历目录并处理所有BPMN文件"""
    bpmn_dir_standard = os.path.normpath(BPMN_DIR)
    bpmn_files = []

    # 收集所有BPMN文件路径
    # for ext in ["*.bpmn", "*.bpmn20.xml"]:
    for ext in ["*.ocl",]:
        bpmn_files.extend(glob.glob(os.path.join(bpmn_dir_standard, "**", ext), recursive=True))

    if not bpmn_files:
        print(f"在目录 {bpmn_dir_standard} 中未找到任何BPMN文件")
        return

    # 去重并按路径排序
    unique_files = list(set(bpmn_files))
    print("总文件数量：",len(unique_files))

    for file_path in sorted(unique_files, key=str.lower):
        if not os.path.isfile(file_path):
            continue  # 跳过非文件项

        txt_path = os.path.splitext(file_path)[0] + ".txt"

        # 检查TXT文件是否已存在
        if os.path.exists(txt_path):
            print(f"跳过已存在的文件：{txt_path}")
            cnt+=1
            print("已处理文件数量 ： ",cnt)
            continue

        process_bpmn_file(file_path)


if __name__ == "__main__":
    main()