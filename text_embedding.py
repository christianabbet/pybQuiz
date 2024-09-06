from pybquiz.db import get_all_trivia_db
from pybquiz.db.base import TriviaTSVDB


from torch.utils.data import DataLoader
from tqdm import tqdm
import pandas as pd
import numpy as np
from typing import Optional
import argparse
import torch
import clip
import torch.linalg


def embedd(
    dataset: TriviaTSVDB, 
    model,
    batch_size: Optional[int] = 128,
):

    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, drop_last=False)

    # Apply on all questions
    uuids = []
    zs = []
    xs = []
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
        xs.extend(x_text)
        zs.extend(texts_features)        
        ys.extend(y_text)
        
    # Perform clustering
    zs = torch.stack(zs)
    zs = zs / torch.linalg.norm(zs, dim=1, keepdims=True)
    
    return zs, ys, uuids


def to_df(zs, ys, uuids):
    # Get sizes
    N, F = zs.shape
    
    # Create df
    name_f = ["f{}".format(f) for f in np.arange(F)]
    df = pd.DataFrame(zs, columns=name_f)
    
    # Index values
    df["uuid"] = uuids
    df["y"] = ys

    return df, name_f
    
    
def main(args):
    
    
    # Get data and loader
    dbs = get_all_trivia_db()

    # Check if model is available
    models_available = clip.available_models()
    if args.arch not in models_available:
        raise NotImplementedError
    
    # Get pretrained model
    model, _ = clip.load(args.arch, device="cpu")
 
    n_db = len(dbs)
    dfs = []
    for i, (db_name, db) in enumerate(dbs.items()):
        print("[{}/{}] {}".format(i+1, n_db, db_name))
        zs, ys, uuids = embedd(dataset=db, model=model)
        df, name_f = to_df(zs, ys, uuids)
        df["db"] = db_name
        
    # Centers
    dfs = pd.concat(dfs)
    # mu = torch.zeros(nc, zs.shape[1])
    
    # for c in np.unique(ys_code):
    #     mu[c] = zs[ys_code == c].mean(dim=0)
    #     mu[c] = mu[c] / torch.linalg.norm(mu[c])

    # # Predicted labels
    # ys_pred = (mu @ zs.T).argmax(dim=0)
    # np.mean(ys_pred.numpy() == ys_code)
    
    # from sklearn.metrics import confusion_matrix
    
    # r = confusion_matrix(ys_code, ys_pred.numpy(), normalize="true")
    # scores = r[np.eye(nc, nc).astype(bool)]

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
    