import argparse
import torch
import clip
import torch.linalg
from pybquiz.db.opentdb import OpenTriviaDB
from torch.utils.data import DataLoader
from tqdm import tqdm
import pandas as pd
import numpy as np


def main(args):
    
    # Get data and loader
    opentdb = OpenTriviaDB()  
    loader = DataLoader(opentdb, batch_size=64, shuffle=False, drop_last=False)
    
    # Check if model is available
    models_available = clip.available_models()
    if args.arch not in models_available:
        raise NotImplementedError
    
    # Get pretrained model
    model, _ = clip.load(args.arch, device="cpu")
    
    # Apply on all questions
    uuids = []
    zs = []
    ys = []
    
    for data in tqdm(loader):
        # Tokenize values
        x_text = data.get("question", [])
        y_text = data.get("category", [])
        uuid_text = data.get("uuid", [])
        
        x_text_token = clip.tokenize(x_text).to("cpu")
        # Embedd text
        with torch.no_grad():
            texts_features = model.encode_text(x_text_token)
        # Append to results
        uuids.extend(uuid_text)
        zs.extend(texts_features)
        ys.extend(y_text)
        
    # Perform clustering
    zs = torch.stack(zs)
    zs = zs / torch.linalg.norm(zs, dim=1, keepdims=True)
    ys = pd.Categorical(ys)
    ys_label = ys.categories.values
    ys_code = ys.codes
    
    # Centers
    nc = ys_code.max() + 1
    mu = torch.zeros(nc, zs.shape[1])
    
    for c in np.unique(ys_code):
        mu[c] = zs[ys_code == c].mean(dim=0)
        mu[c] = mu[c] / torch.linalg.norm(mu[c])

    # Predicted labels
    ys_pred = (mu @ zs.T).argmax(dim=0)
    np.mean(ys_pred.numpy() == ys_code)
    
    from sklearn.metrics import confusion_matrix
    
    r = confusion_matrix(ys_code, ys_pred.numpy(), normalize="true")
    r[np.eye(ns, ns).astype(bool)]

if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='Text embedding',
        description='Embed text for feature description',
    )
    parser.add_argument('--arch', default="RN50",
                        help='Default pretrained architecture. Default is RN50.')
    args = parser.parse_args()
    
    main(args=args)
    