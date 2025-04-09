import os
import json
import time
from tqdm import tqdm
from openai import OpenAI
from argparse import ArgumentParser


# 导入必要的库
# os: 文件路径操作
# json: JSON数据处理
# time: 时间相关操作
# tqdm: 进度条显示
# openai: OpenAI API接口
# argparse: 命令行参数解析

def parser_args():
    # 定义命令行参数解析函数
    parser = ArgumentParser()
    parser.add_argument("--task", type=str, required=True)  # 任务类型（entity/relation）
    parser.add_argument("--train_dir", type=str, required=True)  # 训练数据路径
    parser.add_argument("--test_dir", type=str, required=True)  # 测试数据路径
    parser.add_argument("--shot_dir", type=str, required=True)  # 示例数据路径
    parser.add_argument("--shot_num", type=int, required=True)  # 示例数量
    parser.add_argument("--prompt_dir", type=str, required=True)  # 提示模板路径
    parser.add_argument("--model", type=str, required=True)  # 使用的模型名称
    parser.add_argument("--moda", type=str, default='greedy')  # 生成模式（默认贪心）
    parser.add_argument("--output_dir", type=str, required=True)  # 输出路径
    return parser.parse_args()


def get_completion(args, prompt, id):
    # 创建OpenAI客户端并获取模型响应
    client = OpenAI(
        api_key = "sk-sR8RiK6YYrtk8Rss1b29047069804d108211285c7a25356c",  # 这里需要填写有效的API Key
        base_url = "https://api.openai.com/v1"
    )
    client.base_url = "https://ai-yyds.com/v1"  # 设置备用API端点
    flag = False
    while not flag:
        try:
            # 调用模型生成响应
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=args.model,
                temperature=0  # 生成确定性输出
            )
            flag = True
        except Exception as e:
            print(e)
            time.sleep(0.5)  # 异常重试机制
    return response.choices[0].message.content  # 返回生成结果


def get_ner_shot_prompt(i, train_data, shot_data, shot_num):
    # 构建NER任务的示例提示
    prompt = "\n## Examples\n"
    few_shots = shot_data[i]["id"][:shot_num]  # 获取当前测试样本对应的示例ID列表
    for shot_id in few_shots:
        shot_input = train_data[shot_id]["text"]  # 示例输入文本
        shot_answer = train_data[shot_id]["entity"]  # 示例实体标注结果
        prompt += f"Input:{shot_input}\n"
        prompt += f"Answer:{shot_answer}\n"
    return prompt


def get_ner_prompt(args):
    # 生成NER任务的完整提示列表
    with open(args.train_dir, 'r', encoding='utf-8') as train_file:
        train_data = json.load(train_file)  # 加载训练数据
    with open(args.test_dir, 'r', encoding='utf-8') as test_file:
        test_data = json.load(test_file)  # 加载测试数据
    with open(args.shot_dir, 'r', encoding='utf-8') as shot_file:
        shot_data = json.load(shot_file)  # 加载示例映射数据
    with open(args.prompt_dir, 'r', encoding='utf-8') as prompt_file:
        prompt_templeate = prompt_file.read()  # 加载提示模板

    prompt_list = []
    if args.shot_num == 0:
        # 零样本情况
        for test_item in test_data:
            input_req = test_item["text"]
            prompt = prompt_templeate.format(examples="", input_req=input_req)
            prompt_list.append(prompt)
    else:
        # 少样本情况
        for i, test_item in enumerate(test_data):
            input_req = test_item["text"]
            shot_prompt = get_ner_shot_prompt(i, train_data, shot_data, args.shot_num)
            prompt = prompt_templeate.format(examples=shot_prompt, input_req=input_req)
            prompt_list.append(prompt)
    return prompt_list


def get_rel_shot_prompt(i, train_data, shot_data, shot_num):
    # 构建REL任务的示例提示
    prompt = "\n## Examples\n"
    few_shots = shot_data[i]["id"][:shot_num]
    for shot_id in few_shots:
        shot_input = train_data[shot_id]["text"]
        shot_entity = train_data[shot_id]["entity"]  # 示例实体标注
        shot_answer = train_data[shot_id]["relation"]  # 示例关系标注
        prompt += f"Input:{shot_input}\n"
        prompt += f"Entities:{shot_entity}\n"
        prompt += f"Answer:{shot_answer}\n"
    return prompt


def get_rel_prompt(args):
    # 生成REL任务的完整提示列表
    with open(args.train_dir, 'r', encoding='utf-8') as train_file:
        train_data = json.load(train_file)
    with open(args.test_dir, 'r', encoding='utf-8') as test_file:
        test_data = json.load(test_file)
    with open(args.shot_dir, 'r', encoding='utf-8') as shot_file:
        shot_data = json.load(shot_file)
    with open(args.prompt_dir, 'r', encoding='utf-8') as prompt_file:
        prompt_templeate = prompt_file.read()

    prompt_list = []
    if args.shot_num == 0:
        # 零样本情况
        for test_item in test_data:
            input_req = test_item["text"]
            entities = test_item["entity"]
            prompt = prompt_templeate.format(examples="", input_req=input_req, entity_list=entities)
            prompt_list.append(prompt)
    else:
        # 少样本情况
        for i, test_item in enumerate(test_data):
            input_req = test_item["text"]
            entities = test_item["entity"]
            shot_prompt = get_rel_shot_prompt(i, train_data, shot_data, args.shot_num)
            prompt = prompt_templeate.format(examples=shot_prompt, input_req=input_req, entity_list=entities)
            prompt_list.append(prompt)
    return prompt_list


def gpt_inference(args):
    # 主推理函数
    if args.task == "entity":
        prompt_list = get_ner_prompt(args)  # 根据任务类型生成提示
    elif args.task == "relation":
        prompt_list = get_rel_prompt(args)

    predict_list = []
    id = -1
    for prompt in tqdm(prompt_list, desc='generate answer'):
        id += 1
        predict = get_completion(args, prompt, id)  # 获取模型预测结果
        predict_dict = {"predict": predict}
        predict_list.append(predict_dict)
        time.sleep(0.5)  # 添加延迟防止API调用超限

    # 构建输出路径
    output_dir = os.path.join(args.output_dir, f"{args.task}/{args.model}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_dir = os.path.join(output_dir, "fold_0")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, f"{args.shot_num}.json")

    # 保存结果
    json_data = json.dumps(predict_list, ensure_ascii=False, indent=2)
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(json_data)


def main():
    args = parser_args()  # 解析命令行参数
    print(args.shot_num)
    print(args.model)
    gpt_inference(args)  # 执行推理任务


if __name__ == "__main__":
    main()