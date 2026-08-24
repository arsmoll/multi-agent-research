"""
Hugging Face Spaces 自动部署脚本
用法: python deploy.py
"""
import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo

# ── 配置 ──
SPACE_NAME = "multi-agent-research"  # Space 名称
SPACE_SDK = "streamlit"             # SDK 类型
SPACE_VISIBILITY = "public"         # 公开访问

# 需要上传的文件/目录
UPLOAD_PATHS = [
    "app.py",
    "requirements.txt",
    "README.md",
    ".streamlit/config.toml",
    ".gitignore",
    "src/",
]

# 需要设置为 Secrets 的环境变量
SECRETS = {
    "DEEPSEEK_API_KEY": None,      # 从 .env 读取
    "TAVILY_API_KEY": None,
    "LLM_PROVIDER": "deepseek",
    "DEEPSEEK_BASE_URL": "https://api.deepseek.com/v1",
    "DEEPSEEK_MODEL": "deepseek-chat",
    "LLM_TEMPERATURE": "0.3",
    "LLM_MAX_TOKENS": "4096",
    "MAX_RESEARCH_ROUNDS": "2",
    "CREDIBILITY_THRESHOLD": "0.6",
    "SEARCH_MAX_RESULTS": "5",
}


def load_env_secrets():
    """从 .env 文件读取密钥"""
    env_path = Path(".env")
    if not env_path.exists():
        print("错误: .env 文件不存在")
        sys.exit(1)

    secrets = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in SECRETS:
                SECRETS[key] = value
            if key in ("DEEPSEEK_API_KEY", "TAVILY_API_KEY"):
                secrets[key] = value

    # 检查必需密钥
    for key in ("DEEPSEEK_API_KEY", "TAVILY_API_KEY"):
        val = SECRETS.get(key, "")
        if not val or val.startswith("your_"):
            print(f"错误: .env 中 {key} 未配置")
            sys.exit(1)

    return SECRETS


def main():
    print("=" * 50)
    print("  Hugging Face Spaces 部署工具")
    print("=" * 50)

    # 1. 获取 Token
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        token = input("\n请输入 Hugging Face Access Token\n(从 https://huggingface.co/settings/tokens 获取): ").strip()
    if not token:
        print("错误: 未提供 Token")
        sys.exit(1)

    # 2. 读取密钥
    print("\n读取 .env 密钥...")
    secrets = load_env_secrets()
    print("密钥读取完成")

    # 3. 创建 HfApi
    api = HfApi(token=token)

    # 获取用户名
    user = api.whoami()
    username = user["name"]
    repo_id = f"{username}/{SPACE_NAME}"
    print(f"\nHugging Face 用户: {username}")
    print(f"Space ID: {repo_id}")

    # 4. 创建 Space
    print(f"\n创建 Space: {repo_id}...")
    try:
        create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk=SPACE_SDK,
            space_hardware="cpu-basic",
            private=False,
            token=token,
        )
        print("Space 创建成功")
    except Exception as e:
        if "already" in str(e).lower():
            print("Space 已存在，继续上传")
        else:
            print(f"创建 Space 失败: {e}")
            sys.exit(1)

    # 5. 上传文件
    print("\n上传项目文件...")
    for path in UPLOAD_PATHS:
        p = Path(path)
        if p.is_dir():
            api.upload_folder(
                folder_path=str(p),
                repo_id=repo_id,
                repo_type="space",
                path_in_repo=path,
            )
            print(f"  上传目录: {path}/")
        elif p.exists():
            api.upload_file(
                path_or_fileobj=str(p),
                path_in_repo=path,
                repo_id=repo_id,
                repo_type="space",
            )
            print(f"  上传文件: {path}")
        else:
            print(f"  跳过(不存在): {path}")

    # 6. 设置 Secrets
    print("\n设置 Secrets...")
    for key, value in secrets.items():
        if value and not str(value).startswith("your_"):
            try:
                api.add_space_secret(
                    repo_id=repo_id,
                    key=key,
                    value=str(value),
                )
                print(f"  设置: {key}")
            except Exception as e:
                if "already" in str(e).lower():
                    # 先删除再添加
                    api.delete_space_secret(repo_id=repo_id, key=key)
                    api.add_space_secret(
                        repo_id=repo_id,
                        key=key,
                        value=str(value),
                    )
                    print(f"  更新: {key}")
                else:
                    print(f"  跳过 {key}: {e}")

    # 7. 完成
    space_url = f"https://huggingface.co/spaces/{repo_id}"
    print("\n" + "=" * 50)
    print("  部署完成!")
    print("=" * 50)
    print(f"\n访问地址: {space_url}")
    print(f"应用地址: https://{username}-{SPACE_NAME}.hf.space")
    print("\n首次构建需要 2-3 分钟，请耐心等待。")


if __name__ == "__main__":
    main()
