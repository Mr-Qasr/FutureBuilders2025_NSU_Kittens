from huggingface_hub import hf_hub_download

# Change these to the model/repo and file you want
REPO_ID = "TheBloke/openchat-3.5-1210-GGUF"
FILENAME = "openchat-3.5-1210.Q3_K_S.gguf"
LOCAL_DIR = "models/reasoning"

def main():
    path = hf_hub_download(
        repo_id=REPO_ID,
        filename=FILENAME,
        local_dir=LOCAL_DIR,
        local_dir_use_symlinks=False,
    )
    print("Downloaded to:", path)

if __name__ == "__main__":
    main()
