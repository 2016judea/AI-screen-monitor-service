import torch
import open_clip
from PIL import Image
import torchvision.transforms as transforms

# Load model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
tokenizer = open_clip.get_tokenizer('ViT-B-32')

model.to(device)
model.eval()

def embed_pil_image(img: Image.Image) -> list[float]:
    image_input = preprocess(img).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image_input)
        image_features /= image_features.norm(dim=-1, keepdim=True)
    embedding = image_features.cpu().tolist()[0]
    return embedding


# --- Embed TEXT (agent query) ---
def embed_text(text: str) -> list[float]:
    text_input = tokenizer([text]).to(device)

    with torch.no_grad():
        text_features = model.encode_text(text_input)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    embedding = text_features.cpu().tolist()[0]
    return embedding
