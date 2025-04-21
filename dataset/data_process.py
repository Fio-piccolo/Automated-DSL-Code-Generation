import os
import json
import random
from pathlib import Path
from typing import List, Dict, Tuple
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)


def process_directory(root_dir: str, file_type: str) -> List[Dict[str, str]]:
    data = []
    root_path = Path(root_dir)

    for current_dir, _, files in os.walk(root_path):
        current_path = Path(current_dir)
        for file in files:
            if file.endswith(file_type):
                base_name = Path(file).stem
                sysml_file = current_path / file
                txt_file = current_path / f"{base_name}.txt"

                if not txt_file.exists():
                    logging.warning(f"Missing corresponding TXT file: {txt_file}")
                    continue

                try:
                    sysml_content = sysml_file.read_text(encoding="utf-8").strip()
                    txt_content = txt_file.read_text(encoding="utf-8").strip()

                    data.append({
                        "name": base_name,
                        "text": txt_content,
                        "label": sysml_content
                    })
                except UnicodeDecodeError as ude:
                    logging.error(f"Encoding error in {file}: {str(ude)}", exc_info=True)
                except Exception as e:
                    logging.error(f"Unexpected error processing {file}: {str(e)}", exc_info=True)

    logging.info(f"Collected {len(data)} valid example pairs")
    return data


def split_dataset(
        data: List[Dict[str, str]],
        train_ratio: float = 0.6,
        val_ratio: float = 0.2
) -> Tuple[List[Dict[str, str]], ...]:
    """
    划分数据集，包含参数校验和可复现的随机划分
    :param data: 待划分的数据集
    :param train_ratio: 训练集比例（0-1）
    :param val_ratio: 验证集比例（0-1，train_ratio+val_ratio<=1）
    :return: (训练集, 验证集, 测试集) 元组
    """
    if not (0 < train_ratio < 1 and 0 <= val_ratio < 1 and train_ratio + val_ratio <= 1):
        raise ValueError("Invalid ratio values: train_ratio + val_ratio must be <= 1 and all between 0-1")

    total = len(data)
    if total == 0:
        raise ValueError("Cannot split empty dataset")

    random.seed(42)  # 固定随机种子保证可复现性
    random.shuffle(data)

    train_size = int(total * train_ratio)
    val_size = int(total * val_ratio)
    test_size = total - train_size - val_size

    return (
        data[:train_size],
        data[train_size:train_size + val_size],
        data[train_size + val_size:train_size + val_size + test_size]
    )


def save_to_json(
        data: List[Dict[str, str]],
        filename: str,
        dataset_type: str = "train"
) -> None:
    """
    保存为指定格式的JSON文件，支持不同数据集类型
    :param data: 要保存的数据
    :param filename: 输出文件名
    :param dataset_type: 数据集类型（train/val/test）
    """
    output = {dataset_type: data}
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        logging.info(f"Successfully saved {len(data)} {dataset_type} examples to {filename}")
    except Exception as e:
        logging.error(f"Failed to save JSON file: {str(e)}", exc_info=True)


if __name__ == "__main__":
    # 改文件夹名字（会递归遍历），改处理的语言文件名后缀，如。bpml
    # 配置参数
    # INPUT_DIR = "./BPMN for Research NEW"  # 替换为实际目录
    INPUT_DIR = "./OCL"  # 替换为实际目录
    OUTPUT_TRAIN = os.path.join(INPUT_DIR,"train.json")
    OUTPUT_VAL = os.path.join(INPUT_DIR,"val.json")
    OUTPUT_TEST = os.path.join(INPUT_DIR,"test.json")

    # file_type=".bpmn" # 处理的语言文件名后缀
    file_type=".ocl" # 处理的语言文件名后缀
    # 处理文件
    try:
        all_examples = process_directory(INPUT_DIR, file_type)
        if not all_examples:
            logging.error("No valid example pairs found, exiting")
            exit(1)

        # 划分数据集
        train_data, val_data, test_data = split_dataset(all_examples)

    #     # 保存结果
    #     save_to_json(all_examples, OUTPUT_TRAIN, "val")
        save_to_json(train_data, OUTPUT_TRAIN, "train")
        save_to_json(val_data, OUTPUT_VAL, "val")
        save_to_json(test_data, OUTPUT_TEST, "test")

        logging.info("Data processing completed successfully")
        logging.info(f"Training set: {len(train_data)} examples")
        logging.info(f"Validation set: {len(val_data)} examples")
        logging.info(f"Test set: {len(test_data)} examples")
    #
    except Exception as e:
        logging.critical(f"Process failed due to: {str(e)}", exc_info=True)
        exit(1)