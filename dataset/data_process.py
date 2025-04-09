import os
import json
import random


def process_directory(root_dir):
    """递归处理目录并收集数据"""
    data = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.sysml'):
                # 提取基础名称
                base_name = os.path.splitext(file)[0]
                # 构建对应的txt文件路径
                txt_file = os.path.join(root, f"{base_name}.txt")
                if os.path.exists(txt_file):
                    try:
                        # 读取文件内容
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            sysml_content = f.read()
                        with open(txt_file, 'r', encoding='utf-8') as f:
                            txt_content = f.read()

                        data.append({
                            "name": base_name,
                            "text": txt_content.strip(),
                            "label": sysml_content.strip()
                        })
                    except Exception as e:
                        print(f"Error processing {file}: {str(e)}")
    return data


def split_dataset(data, train_ratio=0.6, val_ratio=0.2):
    """划分数据集"""
    random.shuffle(data)
    total = len(data)
    train_size = int(total * train_ratio)
    val_size = int(total * val_ratio)

    return (
        data[:train_size],
        data[train_size:train_size + val_size],
        data[train_size + val_size:]
    )


def save_to_json(data, filename):
    """保存为指定格式的JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "train": data
        }, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # 配置参数
    INPUT_DIR = "validation" # 替换为实际目录
    OUTPUT_TRAIN = "validation.json"
    OUTPUT_VAL = "validation.json"
    OUTPUT_TEST = "testing.json"

    # 处理文件
    all_examples = process_directory(INPUT_DIR)
    print(f"Total valid example pairs: {len(all_examples)}")

    if not all_examples:
        print("No valid example pairs found.")
        exit()

    # 划分数据集
    # training, validation, testing = split_dataset(all_examples)

    # 保存结果
    save_to_json(all_examples, OUTPUT_TRAIN)
    # save_to_json(validation, OUTPUT_VAL)
    # save_to_json(testing, OUTPUT_TEST)

    print("Data processing completed:")
    print(f"Training set: {len(all_examples)} examples")
    # print(f"Validation set: {len(validation)} examples")
    # print(f"Testing set: {len(testing)} examples")